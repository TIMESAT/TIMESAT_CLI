from __future__ import annotations
import os, re, math, datetime
import numpy as np
from typing import List, Tuple

__all__ = ["read_time_vector"]


def _parse_dates_from_name(name: str) -> Tuple[int, int, int]:
    date_regex1 = r"\d{4}-\d{2}-\d{2}"
    date_regex2 = r"\d{4}\d{2}\d{2}"
    try:
        dates = re.findall(date_regex1, name)
        position = name.find(dates[0])
        y = int(name[position:position+4])
        m = int(name[position+5:position+7])
        d = int(name[position+8:position+10])
        return y, m, d
    except Exception:
        try:
            dates = re.findall(date_regex2, name)
            position = name.find(dates[0])
            y = int(name[position:position+4])
            m = int(name[position+4:position+6])
            d = int(name[position+6:position+8])
            return y, m, d
        except Exception as e:
            raise ValueError(f"No date found in filename: {name}") from e


def read_time_vector(tlist: str, filepaths: List[str]):
    """Return (timevector, yr, yrstart, yrend) in YYYYDOY format."""
    flist = [os.path.basename(p) for p in filepaths]
    timevector = np.ndarray(len(flist), order='F', dtype='uint32')
    if tlist == '':
        for i, fname in enumerate(flist):
            y, m, d = _parse_dates_from_name(fname)
            doy = (datetime.date(y, m, d) - datetime.date(y, 1, 1)).days + 1
            timevector[i] = y * 1000 + doy
    else:
        with open(tlist, 'r') as f:
            lines = f.read().splitlines()
        for idx, val in enumerate(lines):
            n = len(val)
            if n == 8:  # YYYYMMDD
                dt = datetime.datetime.strptime(val, "%Y%m%d")
                timevector[idx] = int(f"{dt.year}{dt.timetuple().tm_yday:03d}")
            elif n == 7:  # YYYYDOY
                _ = datetime.datetime.strptime(val, "%Y%j")
                timevector[idx] = int(val)
            else:
                raise ValueError(f"Unrecognized date format: {val}")

    yrstart = int(np.floor(timevector.min() / 1000))
    yrend   = int(np.floor(timevector.max() / 1000))
    yr      = yrend - yrstart + 1
    return timevector, yr, yrstart, yrend
