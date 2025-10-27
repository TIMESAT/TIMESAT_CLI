from __future__ import annotations
import math, os, datetime
from typing import List, Tuple

import numpy as np
import rasterio

import timesat  # external dependency

from .config import load_config
from .readers import read_file_lists, open_image_data
from .timevec import read_time_vector
from .fsutils import create_output_folders
from .writers import prepare_profiles, write_vpp_layers, write_st_layers
from .parallel import maybe_init_ray

VPP_NAMES = ["SOSD","SOSV","LSLOPE","EOSD","EOSV","RSLOPE","LENGTH",
             "MINV","MAXD","MAXV","AMPL","TPROD","SPROD"]


def _unique_by_timevector(flist: List[str], qlist: List[str], timevector):
    tv_unique, indices = np.unique(timevector, return_index=True)
    flist2 = [flist[i] for i in indices]
    qlist2 = [qlist[i] for i in indices] if qlist else []
    return tv_unique, flist2, qlist2


def _build_output_filenames(st_folder: str, vpp_folder: str, p_outindex, yrstart: int, yrend: int):
    outyfitfn = []
    for i_tv in p_outindex:
        yfitdate = datetime.date(yrstart, 1, 1) + datetime.timedelta(days=int(i_tv)) - datetime.timedelta(days=1)
        outyfitfn.append(os.path.join(st_folder, f"TIMESAT_{yfitdate.strftime('%Y%m%d')}.tif"))

    outvppfn = []
    for i_yr in range(yrstart, yrend + 1):
        for i_seas in range(2):
            for name in VPP_NAMES:
                outvppfn.append(os.path.join(vpp_folder, f"TIMESAT_{name}_{i_yr}_season_{i_seas+1}.tif"))
    outnsfn = os.path.join(vpp_folder, 'TIMESAT_nsperyear.tif')
    return outyfitfn, outvppfn, outnsfn


def _memory_plan(dx: int, dy: int, z: int, p_outindex_num: int, yr: int, max_memory_gb: float) -> Tuple[int, int]:
    num_layers = p_outindex_num + z * 2 + (13 * 2) * yr
    bytes_per = 4  # float32
    max_bytes = max_memory_gb * (2 ** 30)
    dy_max = max_bytes / (dx * num_layers * bytes_per)
    y_slice_size = int(min(math.floor(dy_max), dy)) if dy_max > 0 else dy
    y_slice_size = max(1, y_slice_size)
    num_block = int(math.ceil(dy / y_slice_size))
    return y_slice_size, num_block


def _build_param_array(
    s,
    attr: str,
    dtype,
    size: int = 255,
    shape: Tuple[int, ...] | None = None,
    fortran_2d: bool = False
):
    """
    Build a parameter array for TIMESAT class settings.

    Parameters
    ----------
    s : object
        Settings container with `classes` iterable.
    attr : str
        Attribute on each class object in `s.classes` (e.g., 'p_smooth').
    dtype : numpy dtype or dtype string (e.g., 'uint8', 'double').
    size : int
        Length of the first dimension (TIMESAT expects 255).
    shape : tuple[int, ...] | None
        Extra trailing shape for per-class vectors (e.g., (2,) for p_startcutoff).
    fortran_2d : bool
        If True and `shape==(2,)`, allocate (size,2) with order='F' to mirror legacy layout.

    Returns
    -------
    np.ndarray
        Filled parameter array.
    """
    if shape is None:
        arr = np.zeros(size, dtype=dtype)
        for i, c in enumerate(s.classes):
            arr[i] = getattr(c, attr)
        return arr

    full_shape = (size, *shape)
    order = 'F' if fortran_2d and len(shape) == 1 and shape[0] > 1 else 'C'
    arr = np.zeros(full_shape, dtype=dtype, order=order)
    for i, c in enumerate(s.classes):
        arr[i, ...] = getattr(c, attr)
    return arr


def run(jsfile: str) -> None:
    print(jsfile)
    cfg = load_config(jsfile)
    s = cfg.settings

    if s.outputfolder == '':
        print('Nothing to do...')
        return

    ray_inited = maybe_init_ray(s.para_check, s.ray_dir)

    flist, qlist = read_file_lists(s.image_file_list, s.quality_file_list)
    timevector, yr, yrstart, yrend = read_time_vector(s.tv_list, flist)
    timevector, flist, qlist = _unique_by_timevector(flist, qlist, timevector)

    z = len(flist)
    print(f'num of images: {z}')
    print('First image: ' + os.path.basename(flist[0]))
    print('Last  image: ' + os.path.basename(flist[-1]))
    print(yrstart)

    p_outindex = np.arange(
        (datetime.datetime(yrstart, 1, 1) - datetime.datetime(yrstart, 1, 1)).days + 1,
        (datetime.datetime(yrstart + yr - 1, 12, 31) - datetime.datetime(yrstart, 1, 1)).days + 1
    )[:: int(s.p_st_timestep)]
    p_outindex_num = len(p_outindex)

    with rasterio.open(flist[0], 'r') as temp:
        img_profile = temp.profile

    if sum(s.imwindow) == 0:
        dx, dy = img_profile['width'], img_profile['height']
    else:
        dx, dy = int(s.imwindow[2]), int(s.imwindow[3])

    imgprocessing = not (s.imwindow[2] + s.imwindow[3] == 2)

    if imgprocessing:
        st_folder, vpp_folder = create_output_folders(s.outputfolder)
        outyfitfn, outvppfn, outnsfn = _build_output_filenames(st_folder, vpp_folder, p_outindex, yrstart, yrend)
        img_profile_st, img_profile_vpp, img_profile_ns = prepare_profiles(img_profile, s.p_nodata, s.scale, s.offset)
        # pre-create files
        for path in outvppfn:
            with rasterio.open(path, 'w', **img_profile_vpp):
                pass
        for path in outyfitfn:
            with rasterio.open(path, 'w', **img_profile_st):
                pass

    # compute memory blocks
    y_slice_size, num_block = _memory_plan(dx, dy, z, p_outindex_num, yr, s.max_memory_gb)
    y_slice_end = dy % y_slice_size if (dy % y_slice_size) > 0 else y_slice_size
    print('y_slice_size = ' + str(y_slice_size))

    for iblock in range(num_block):
        print(f'Processing block: {iblock + 1}/{num_block}  starttime: {datetime.datetime.now()}')
        x = dx
        y = int(y_slice_size) if iblock != num_block - 1 else int(y_slice_end)
        x_map = int(s.imwindow[0])
        y_map = int(iblock * y_slice_size + s.imwindow[1])

        vi, qa, lc = open_image_data(
            x_map, y_map, x, y, flist, qlist if qlist else '', s.lc_file,
            img_profile['dtype'], s.p_a, s.para_check, s.p_band_id
        )

        print('--- start TIMESAT processing ---  starttime: ' + str(datetime.datetime.now()))

        if s.scale != 1 or s.offset != 0:
            vi = vi * s.scale + s.offset

        if s.para_check > 1 and ray_inited:
            import ray

            @ray.remote
            def runtimesat(vi_temp, qa_temp, lc_temp):
                vpp_para, vppqa, nseason_para, yfit_para, yfitqa, seasonfit, tseq = timesat.tsf2py(
                    yr, vi_temp, qa_temp, timevector, lc_temp, s.p_nclasses,
                    _build_param_array(s, 'landuse', 'uint8'),
                    p_outindex,
                    s.p_ignoreday, s.p_ylu, s.p_printflag,
                    _build_param_array(s, 'p_fitmethod', 'uint8'),
                    _build_param_array(s, 'p_smooth', 'double'),
                    s.p_nodata, s.p_davailwin, s.p_outlier,
                    _build_param_array(s, 'p_nenvi', 'uint8'),
                    _build_param_array(s, 'p_wfactnum', 'double'),
                    _build_param_array(s, 'p_startmethod', 'uint8'),
                    _build_param_array(s, 'p_startcutoff', 'double', shape=(2,), fortran_2d=True),
                    _build_param_array(s, 'p_low_percentile', 'double'),
                    _build_param_array(s, 'p_fillbase', 'uint8'),
                    s.p_hrvppformat,
                    _build_param_array(s, 'p_seasonmethod', 'uint8'),
                    _build_param_array(s, 'p_seapar', 'double'),
                    1, x, len(flist), p_outindex_num
                )
                vpp_para = vpp_para[0, :, :]
                yfit_para = yfit_para[0, :, :]
                nseason_para = nseason_para[0, :]
                return vpp_para, yfit_para, nseason_para

            futures = [
                runtimesat.remote(
                    np.expand_dims(vi[i, :, :], axis=0),
                    np.expand_dims(qa[i, :, :], axis=0),
                    np.expand_dims(lc[i, :], axis=0)
                ) for i in range(y)
            ]
            results = ray.get(futures)
            vpp = np.stack([r[0] for r in results], axis=0)
            yfit = np.stack([r[1] for r in results], axis=0)
            nseason = np.stack([r[2] for r in results], axis=0)
        else:
            # Precompute arrays once per block to pass into timesat
            landuse_arr          = _build_param_array(s, 'landuse', 'uint8')
            p_fitmethod_arr      = _build_param_array(s, 'p_fitmethod', 'uint8')
            p_smooth_arr         = _build_param_array(s, 'p_smooth', 'double')
            p_nenvi_arr          = _build_param_array(s, 'p_nenvi', 'uint8')
            p_wfactnum_arr       = _build_param_array(s, 'p_wfactnum', 'double')
            p_startmethod_arr    = _build_param_array(s, 'p_startmethod', 'uint8')
            p_startcutoff_arr    = _build_param_array(s, 'p_startcutoff', 'double', shape=(2,), fortran_2d=True)
            p_low_percentile_arr = _build_param_array(s, 'p_low_percentile', 'double')
            p_fillbase_arr       = _build_param_array(s, 'p_fillbase', 'uint8')
            p_seasonmethod_arr   = _build_param_array(s, 'p_seasonmethod', 'uint8')
            p_seapar_arr         = _build_param_array(s, 'p_seapar', 'double')

            vpp, vppqa, nseason, yfit, yfitqa, seasonfit, tseq = timesat.tsf2py(
                yr, vi, qa, timevector, lc, s.p_nclasses, landuse_arr, p_outindex,
                s.p_ignoreday, s.p_ylu, s.p_printflag, p_fitmethod_arr, p_smooth_arr,
                s.p_nodata, s.p_davailwin, s.p_outlier,
                p_nenvi_arr, p_wfactnum_arr, p_startmethod_arr, p_startcutoff_arr,
                p_low_percentile_arr, p_fillbase_arr, s.p_hrvppformat,
                p_seasonmethod_arr, p_seapar_arr,
                y, x, len(flist), p_outindex_num)

        vpp  = np.moveaxis(vpp, -1, 0)
        if s.scale == 0 and s.offset == 0:
            yfit = np.moveaxis(yfit, -1, 0).astype(img_profile['dtype'])
        else:
            yfit = np.moveaxis(yfit, -1, 0).astype('float32')

        print('--- start writing geotif ---  starttime: ' + str(datetime.datetime.now()))
        window = (x_map, y_map, x, y)
        write_vpp_layers(outvppfn, vpp, window, img_profile_vpp)
        write_st_layers(outyfitfn, yfit, window, img_profile_st)

        print(f'Block: {iblock + 1}/{num_block}  finishedtime: {datetime.datetime.now()}')
