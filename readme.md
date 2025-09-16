# TIMESAT4.1.7 README

> This repository provides a Python/Fortran interface to TIMESAT, tailored for the HR-VPP2 project. It is primarily used for the calibration, validation, and production of vegetation parameters derived from high-resolution satellite data. The codebase integrates the TIMESAT processing routines with Python workflows, enabling reproducible environment setup, automated compilation, and streamlined execution for operational HR-VPP2 tasks.

> Clean, step‑by‑step instructions to set up, compile, and run the Python/Fortran bridge for TIMESAT on **Linux**. The environment can be created using **conda** or **pip**. No macOS support is provided.

---

## Overview
This repository provides a Python interface (via **NumPy f2py**) to the TIMESAT Fortran routines. You will:

1. Prepare a Python environment (conda or pip).
2. Install `gfortran` (via conda or your system package manager).
3. Compile the Fortran archive into a Python extension using the provided shell script.
4. Run the application scripts (e.g., `main.py`) with your settings.

Supported platform: **Linux** (tested on Ubuntu and similar distributions).
- The TIMESAT static library archive for Linux (e.g., `libtsprocess_linux_vX.Y.Z.a`) is **proprietary software**.
- Usage of this archive is governed by the terms in [PROPRIETARY-LICENSE.txt](./vendor/PROPRIETARY-LICENSE.txt).

---

## Prerequisites
Before you begin, ensure the following are available:

- **Python 3.9+** (3.10/3.11 recommended)
- **NumPy** (includes `numpy.f2py` used for the build)
- **gfortran** (installable via conda)
- The TIMESAT static library archive for Linux (e.g., `libtsprocess_linux_vX.Y.Z.a`)

Optional/common runtime packages (depending on your scripts): `scipy`, `pandas`, `matplotlib`, `tqdm`, 'rasterio', 'ray'.

---

## 1) Environment Setup

### Using conda
```bash
# Create environment 
conda create -n timesat python=3.10 numpy scipy pandas matplotlib tqdm rasterio ray-default gfortran_linux-64 -c conda-forge
conda activate timesat
```

> Ensure `gfortran` is accessible in your PATH after installation.

---

## 2) Compile the Fortran extension with f2py
Use the provided script. It auto‑detects your OS (Linux only) and selects the correct archive name.

```bash
# Make the script executable (first time only)
chmod +x ./compile_TIMESAT_linux_macOS.sh

# Build with default version (from the script)
./compile_TIMESAT_linux_macOS.sh

```

After a successful build, a compiled Python extension (e.g., `timesat.cpython-*.so`) will appear in the working directory. You should then be able to import it:

```python
import timesat
```

---

## 3) Run the application
Depending on your workflow, you may have helper scripts such as `create_file_list.py` and a main driver `main.py`.

Typical commands:

```bash

# Example: run with a production configuration
python main.py settings.json
```

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

## Troubleshooting

**`gfortran: command not found`**
- Install via conda:
```bash
conda install -c conda-forge gfortran_linux-64
```

**`numpy.f2py: no module named numpy`**
- Activate your environment and `pip install numpy`.

**Archive not found (e.g., `libtsprocess_linux_v*.a`)**
- Verify the correct archive is present for your OS and version.
- If your file is versioned differently, either rename it to match the convention or call the build with `VERSION=X.Y.Z`.

**ImportError when importing `timesat`**
- Ensure you run Python from the same environment used to build the module.
- Confirm the compiled `.so` (Linux) resides on your Python path (current directory is fine).

---

## Reproducible builds & notes
- Prefer conda environments for consistent results across machines.
- For pip‑only workflows, ensure conda provides `gfortran_linux-64` to avoid compiler issues.

---

## License & Attribution

This repository contains three distinct components, each under a different license:

- **Open Source License (GPLv3)**  
  You may use, modify, and distribute this software under the terms of the GNU General Public License v3.0.  
  See the [LICENSE](./LICENSE) file for the full text.

- **Commercial License**  
  If you cannot comply with the terms of the GPLv3 (for example, if you want to integrate this code into closed-source or commercial software),  
  you must obtain a separate commercial license from [Zhanzhang Cai / Lund University].  
  See [COMMERCIAL-LICENSE.txt](./COMMERCIAL-LICENSE.txt) for details, or contact us at:  
  **[zhanzhang.cai@nateko.lu.se]**

- **Precompiled Fortran static library archives (in `vendor/`)**  
  These files are **proprietary and closed-source**.  
  Their use is strictly governed by the [PROPRIETARY-LICENSE.txt](./vendor/PROPRIETARY-LICENSE.txt).  
  Redistribution, reverse engineering, or modification of these archives is prohibited.

Acknowledgement: Swedish National Space Agency, European Environment Agency, European Space Agency, VITO remote sensing, DHI remote sensing, Cloudflight, Geoville.

