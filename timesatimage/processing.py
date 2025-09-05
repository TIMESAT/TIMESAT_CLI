from __future__ import annotations
import math, os, datetime
import numpy as np
import rasterio
from typing import List, Tuple

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

        if s.scale != 0 or s.offset != 0:
            vi = vi * s.scale + s.offset

        if s.para_check > 1 and ray_inited:
            import ray

            @ray.remote
            def runtimesat(vi_temp, qa_temp, lc_temp):
                vpp_para, vppqa, nseason_para, yfit_para, yfitqa, seasonfit, tseq = timesat.tsf2py(
                    yr, vi_temp, qa_temp, timevector, lc_temp, s.p_nclasses,
                    _landuse_arr(s),
                    p_outindex,
                    s.p_ignoreday, s.p_ylu, s.p_printflag,
                    _fitmethod_arr(s),
                    _smooth_arr(s),
                    s.p_nodata, s.p_outlier,
                    _nenvi_arr(s),
                    _wfactnum_arr(s),
                    _startmethod_arr(s),
                    _startcutoff_arr(s),
                    _low_percentile_arr(s),
                    _fillbase_arr(s),
                    s.p_hrvppformat,
                    _seasonmethod_arr(s),
                    _seapar_arr(s),
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
            landuse_arr        = _landuse_arr(s)
            p_fitmethod_arr    = _fitmethod_arr(s)
            p_smooth_arr       = _smooth_arr(s)
            p_nenvi_arr        = _nenvi_arr(s)
            p_wfactnum_arr     = _wfactnum_arr(s)
            p_startmethod_arr  = _startmethod_arr(s)
            p_startcutoff_arr  = _startcutoff_arr(s)
            p_low_percentile_arr = _low_percentile_arr(s)
            p_fillbase_arr     = _fillbase_arr(s)
            p_seasonmethod_arr = _seasonmethod_arr(s)
            p_seapar_arr       = _seapar_arr(s)

            vpp, vppqa, nseason, yfit, yfitqa, seasonfit, tseq = timesat.tsf2py(
                yr, vi, qa, timevector, lc, s.p_nclasses, landuse_arr, p_outindex,
                s.p_ignoreday, s.p_ylu, s.p_printflag, p_fitmethod_arr, p_smooth_arr, s.p_nodata, s.p_outlier,
                p_nenvi_arr, p_wfactnum_arr, p_startmethod_arr, p_startcutoff_arr, p_low_percentile_arr,
                p_fillbase_arr, s.p_hrvppformat, p_seasonmethod_arr, p_seapar_arr,
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


# --- helper builders for class arrays ---

def _landuse_arr(s):
    arr = np.zeros(255, dtype='uint8')
    for i, c in enumerate(s.classes):
        arr[i] = c.landuse
    return arr

def _fitmethod_arr(s):
    arr = np.zeros(255, dtype='uint8')
    for i, c in enumerate(s.classes):
        arr[i] = c.p_fitmethod
    return arr

def _smooth_arr(s):
    arr = np.zeros(255, dtype='double')
    for i, c in enumerate(s.classes):
        arr[i] = c.p_smooth
    return arr

def _nenvi_arr(s):
    arr = np.zeros(255, dtype='uint8')
    for i, c in enumerate(s.classes):
        arr[i] = c.p_nenvi
    return arr

def _wfactnum_arr(s):
    arr = np.zeros(255, dtype='double')
    for i, c in enumerate(s.classes):
        arr[i] = c.p_wfactnum
    return arr

def _startmethod_arr(s):
    arr = np.zeros(255, dtype='uint8')
    for i, c in enumerate(s.classes):
        arr[i] = c.p_startmethod
    return arr

def _startcutoff_arr(s):
    arr = np.zeros((255, 2), order='F', dtype='double')
    for i, c in enumerate(s.classes):
        arr[i, :] = c.p_startcutoff
    return arr

def _low_percentile_arr(s):
    arr = np.zeros(255, dtype='double')
    for i, c in enumerate(s.classes):
        arr[i] = c.p_low_percentile
    return arr

def _fillbase_arr(s):
    arr = np.zeros(255, dtype='uint8')
    for i, c in enumerate(s.classes):
        arr[i] = c.p_fillbase
    return arr

def _seasonmethod_arr(s):
    arr = np.zeros(255, dtype='uint8')
    for i, c in enumerate(s.classes):
        arr[i] = c.p_seasonmethod
    return arr

def _seapar_arr(s):
    arr = np.zeros(255, dtype='double')
    for i, c in enumerate(s.classes):
        arr[i] = c.p_seapar
    return arr
