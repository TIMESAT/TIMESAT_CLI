# TIMESAT4.1.7 README

> This repository provides a Python/Fortran interface to TIMESAT.

> Clean, step‑by‑step instructions to set up, compile, and run TIMESAT. The environment can be created using **conda** and **pip**.

---

## Overview
This repository provides a Python interface (via **NumPy f2py**) to the TIMESAT Fortran routines. You will:

1. Prepare a Python environment (conda or pip).
2. Install timesat from Testpypi.
3. Run the application scripts (e.g., `main.py`) with your settings.

---


## HRVPP Notes — QFLAG2 weights
If you work with HRVPP quality flags (`QFLAG2`), the following weights `w` are commonly applied:

| QFLAG2 value | Weight `w` |
|---:|---:|
| 1     | 1.0 |
| 4097  | 1.0 |
| 8193  | 1.0 |
| 12289 | 1.0 |
| 1025  | 0.5 |
| 9217  | 0.5 |
| 2049  | 0.5 |
| 6145  | 0.5 |
| 3073  | 0.5 |

Example (settings.json):

```python
"p_a": {
  "value": [
    [1, 1.0],
    [4097, 1.0],
    [8193, 1.0],
    [12289, 1.0],
    [1025, 0.5],
    [9217, 0.5],
    [2049, 0.5],
    [6145, 0.5],
    [3073, 0.5]
  ],
  "description": "QA weighting rules. Leave empty [] to keep original QA values. Use [qa_value, weight] for exact matches or [min, max, weight] for ranges."
}
```

---

## License

This repository consists of two parts, each under different terms:

- **Python/Fortran interface code** (in `python_interface/`)  
  Licensed under the [Apache License 2.0](./python_interface/LICENSE).  
  You are free to use, modify, and distribute this code under the Apache-2.0 terms.

### 📦 Dependency Licenses

- `timesat-gui` may install additional open-source dependencies (e.g., Flask, pandas, NumPy).  
- Each dependency retains its own license (MIT, BSD, Apache, etc.).  
- Before redistributing or bundling this software, review the license terms of each dependency carefully.

### ⚖️ Summary

| Component        | License Type | Notes |
|------------------|--------------|-------|
| TIMESAT-GUI      | GPL v3       | Open source, modification and redistribution permitted under GPL. |
| TIMESAT          | Proprietary  | All rights reserved. Redistribution and modification prohibited without written consent. |
| Other Dependencies | Various (MIT/BSD/Apache) | Check individual package licenses before redistribution. |

For detailed license information, refer to the license files distributed with each installed package.

---

## Citation

If you use **TIMESAT** or **TIMESAT-GUI** in your research, please cite the corresponding release on Zenodo:

> Cai, Z., Eklundh, L., & Jönsson, P. (2025). *TIMESAT4:  is a software package for analysing time-series of satellite sensor data* (Version 4.1.x) [Computer software]. Zenodo.   
> [https://doi.org/10.5281/zenodo.17369757](https://doi.org/10.5281/zenodo.17369757)

---

## Acknowledgments

- [TIMESAT](https://www.nateko.lu.se/TIMESAT) — Original analysis framework for satellite time-series data.  
- This project acknowledges the Swedish National Space Agency (SNSA), the European Environment Agency (EEA), and the European Space Agency (ESA) for their support and for providing access to satellite data and related resources that made this software possible.

---

