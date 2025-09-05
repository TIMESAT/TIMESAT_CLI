from __future__ import annotations
import json
from dataclasses import dataclass
from typing import List, Sequence, Tuple
import numpy as np


@dataclass
class ClassParams:
    landuse: int
    p_fitmethod: int
    p_smooth: float
    p_nenvi: int
    p_wfactnum: float
    p_startmethod: int
    p_startcutoff: Tuple[float, float]
    p_low_percentile: float
    p_fillbase: int
    p_seasonmethod: int
    p_seapar: float


@dataclass
class Settings:
    image_file_list: str
    quality_file_list: str
    tv_list: str
    lc_file: str
    outputfolder: str
    imwindow: Sequence[int]

    p_band_id: int
    p_ignoreday: int
    p_ylu: np.ndarray
    p_a: List[List[float]]
    p_st_timestep: int
    p_nodata: float
    p_outlier: int
    p_printflag: int
    max_memory_gb: float
    para_check: int
    ray_dir: str
    scale: float
    offset: float
    p_hrvppformat: int
    p_nclasses: int
    classes: List[ClassParams]


@dataclass
class Config:
    settings: Settings


def _as_array(value, dtype=float, fortran=False):
    arr = np.array(value, dtype=dtype)
    if fortran:
        arr = np.asfortranarray(arr)
    return arr


def load_config(jsfile: str) -> Config:
    with open(jsfile, "r") as f:
        data = json.load(f)

    s = data["settings"]
    nclasses = int(s["p_nclasses"]["value"])

    classes: List[ClassParams] = []
    for i in range(nclasses):
        k = f"class{i+1}"
        c = data[k]
        classes.append(
            ClassParams(
                landuse=int(c["landuse"]["value"]),
                p_fitmethod=int(c["p_fitmethod"]["value"]),
                p_smooth=float(_as_array(c["p_smooth"]["value"], dtype="double")),
                p_nenvi=int(c["p_nenvi"]["value"]),
                p_wfactnum=float(_as_array(c["p_wfactnum"]["value"], dtype="double")),
                p_startmethod=int(c["p_startmethod"]["value"]),
                p_startcutoff=tuple(_as_array(c["p_startcutoff"]["value"], dtype="double", fortran=True)),
                p_low_percentile=float(_as_array(c["p_low_percentile"]["value"], dtype="double")),
                p_fillbase=int(c["p_fillbase"]["value"]),
                p_seasonmethod=int(c["p_seasonmethod"]["value"]),
                p_seapar=float(_as_array(c["p_seapar"]["value"], dtype="double")),
            )
        )

    settings = Settings(
        image_file_list=s["image_file_list"]["value"],
        quality_file_list=s["quality_file_list"]["value"],
        tv_list=s["tv_list"]["value"],
        lc_file=s["lc_file"]["value"],
        outputfolder=s["outputfolder"]["value"],
        imwindow=s["imwindow"]["value"],
        p_band_id=int(s["p_band_id"]["value"]),
        p_ignoreday=int(s["p_ignoreday"]["value"]),
        p_ylu=_as_array(s["p_ylu"]["value"], dtype="double", fortran=True),
        p_a=s["p_a"]["value"],
        p_st_timestep=int(s["p_st_timestep"]["value"]),
        p_nodata=float(s["p_nodata"]["value"]),
        p_outlier=int(s["p_outlier"]["value"]),
        p_printflag=int(s["p_printflag"]["value"]),
        max_memory_gb=float(s["max_memory_gb"]["value"]),
        para_check=int(s["para_check"]["value"]),
        ray_dir=s["ray_dir"]["value"],
        scale=float(s["scale"]["value"]),
        offset=float(s["offset"]["value"]),
        p_hrvppformat=int(s["p_hrvppformat"]["value"]),
        p_nclasses=nclasses,
        classes=classes,
    )

    return Config(settings=settings)
