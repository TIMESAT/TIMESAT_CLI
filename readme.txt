# TIMESAT — Reworked README

> Clean, step‑by‑step instructions to set up, compile, and run the Python/Fortran bridge for TIMESAT on Linux and macOS. Includes both **YAML‑based** and **manual** environment setup paths.

---

## Overview
This repository provides a Python interface (via **NumPy f2py**) to the TIMESAT Fortran routines. You will:

1. Prepare a Python environment (choose **Option A** or **Option B** below).
2. Compile the Fortran archive into a Python extension using the provided shell script.
3. Run the application scripts (e.g., `main.py`) with your settings.

Supported platforms: **Linux** and **macOS** (Apple Silicon and Intel), assuming a working **gfortran** toolchain.

> Windows is not directly supported by the provided build script. Use WSL (Ubuntu) or a Linux/macOS machine.

---

## Prerequisites
Before you begin, ensure the following are available:

- **Python 3.9+** (3.10/3.11 recommended)
- **NumPy** (includes `numpy.f2py` used for the build)
- **gfortran** and a C/C++ toolchain compatible with your OS
- The TIMESAT static library archive for your OS (e.g., `libtsprocess_linux_vX.Y.Z.a` or `libtsprocess_macos_vX.Y.Z.a`)

Optional/common runtime packages (depending on your scripts): `scipy`, `pandas`, `matplotlib`, `tqdm`.

---

## 1) Environment Setup (choose one)

### Option A — Create environment from YAML (recommended for reproducibility)
If you prefer a pre‑pinned stack:

```bash
# Using conda or mamba
mamba env create -f TIMESAT_python.yml  # or: conda env create -f TIMESAT_python.yml
conda activate timesat
```

This will install Python, NumPy, and any additional packages declared in `TIMESAT_python.yml`.

### Option B — Manual install (no YAML)
If you prefer to use your system Python or a custom virtual environment:

```bash
# Create and activate a virtual environment (example for bash/zsh)
python3 -m venv .venv
source .venv/bin/activate

# Minimum required for building the extension
pip install --upgrade pip
pip install numpy

# (Optional) Install runtime dependencies you need for your workflow
pip install scipy pandas matplotlib tqdm
```

> Ensure `gfortran` is on your PATH. On macOS, consider installing via Homebrew: `brew install gcc`.

---

## 2) Compile the Fortran extension with f2py
Use the provided script. It auto‑detects your OS and selects the correct archive name.

```bash
# Make the script executable (first time only)
chmod +x ./compile_TIMESAT_linux_macOS.sh

# Build with default version (from the script)
./compile_TIMESAT_linux_macOS.sh

# (Advanced) Override the library version if needed
VERSION=4.1.8 ./compile_TIMESAT_linux_macOS.sh
```

What the script does, in short:
- Detects **Linux** or **macOS**.
- Looks for a versioned archive (e.g., `libtsprocess_linux_v${VERSION}.a`) and falls back to an unversioned symlink (e.g., `libtsprocess_linux.a`).
- Invokes `numpy.f2py` to build a Python module named **`timesat`** from `./python_interface/*.f90` and the archive.

After a successful build, a compiled Python extension (e.g., `timesat.cpython-*.so`) will appear in the working directory. You should then be able to import it:

```python
import timesat
```

---

## 3) Run the application
Depending on your workflow, you may have helper scripts such as `create_file_list.py` and a main driver `main.py`.

Typical commands:

```bash
# Example: generate input lists
python create_file_list.py

# Example: run with a test configuration
python main.py settings_test.json

# Example: run with a production configuration
python main.py settings.json
```

Adjust script names and configuration paths as needed for your project layout.

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
- Install a compiler toolchain.
  - macOS: `brew install gcc` (then ensure `gfortran` is on PATH)
  - Ubuntu/Debian: `sudo apt-get update && sudo apt-get install gfortran build-essential`

**`numpy.f2py: no module named numpy`**
- Activate your environment and `pip install numpy`.

**Archive not found (e.g., `libtsprocess_*.a`)**
- Verify the correct archive is present for your OS and version.
- If your file is versioned differently, either rename it to match the convention or call the build with `VERSION=X.Y.Z`.

**ImportError when importing `timesat`**
- Ensure you run Python from the same environment used to build the module.
- Confirm the compiled `.so` (Linux/macOS) resides on your Python path (current directory is fine).

---

## Reproducible builds & notes
- Prefer **Option A** (YAML) for consistent results across machines.
- If distributing to colleagues who avoid YAML/conda, provide a short list of required Python packages and OS compilers (see **Prerequisites** above) and point them to **Option B**.

---

## License & Attribution
Include your project’s license information here and acknowledge the original TIMESAT authors as appropriate.


