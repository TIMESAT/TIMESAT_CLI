# TIMESAT — Reworked README

> Clean, step‑by‑step instructions to set up, compile, and run the Python/Fortran bridge for TIMESAT on **Linux**. The environment can be created using **conda** or **pip**. No macOS support is provided.

---

## Overview
This repository provides a Python interface (via **NumPy f2py**) to the TIMESAT Fortran routines. You will:

1. Prepare a Python environment (conda or pip).
2. Install `gfortran` (via conda or your system package manager).
3. Compile the Fortran archive into a Python extension using the provided shell script.
4. Run the application scripts (e.g., `main.py`) with your settings.

Supported platform: **Linux** (tested on Ubuntu and similar distributions).

---

## Prerequisites
Before you begin, ensure the following are available:

- **Python 3.9+** (3.10/3.11 recommended)
- **NumPy** (includes `numpy.f2py` used for the build)
- **gfortran** (installable via conda)
- The TIMESAT static library archive for Linux (e.g., `libtsprocess_linux_vX.Y.Z.a`)

Optional/common runtime packages (depending on your scripts): `scipy`, `pandas`, `matplotlib`, `tqdm`.

---

## 1) Environment Setup

### Option A — Using conda (recommended)
```bash
# Create environment from YAML if available
conda env create -f TIMESAT_python.yml
conda activate timesat

# Or create manually
conda create -n timesat python=3.10 numpy scipy pandas matplotlib tqdm gfortran_linux-64 -c conda-forge
conda activate timesat
```

### Option B — Using pip + conda-forge compilers
```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install packages
pip install --upgrade pip
pip install numpy scipy pandas matplotlib tqdm

# Install gfortran via conda (in base or a dedicated env)
conda install -c conda-forge gfortran_linux-64
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

Example (pseudocode):

```python
w = np.ones_like(vi, dtype=float)
w[np.isin(Q2, [1, 4097, 8193, 12289])] = 1.0
w[np.isin(Q2, [1025, 9217, 2049, 6145, 3073])] = 0.5
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

This project is distributed under the terms specified in the [LICENSE](./LICENSE) file included in the repository. Please review that file for the complete licensing details.

Acknowledgement: credit the original TIMESAT authors as appropriate.

