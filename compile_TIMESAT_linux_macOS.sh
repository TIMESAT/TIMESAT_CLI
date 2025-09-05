#!/bin/bash
set -euo pipefail

# Use the same version as in your archive-build script.
# Allow override via environment: `VERSION=4.1.8 ./build_f2py.sh`
VERSION="${VERSION:-4.1.7}"

# Ensure f2py uses gfortran (optional but helpful)
export FC="${FC:-gfortran}"

# Detect OS type using uname
OS_TYPE=$(uname)

# Pick the correct archive name (versioned), with a fallback to the symlink name
choose_lib() {
    local ver_lib="$1"
    local link_lib="$2"
    if [ -f "$ver_lib" ]; then
        echo "$ver_lib"
    elif [ -f "$link_lib" ]; then
        echo "$link_lib"
    else
        echo "ERROR: Neither '$ver_lib' nor '$link_lib' found." >&2
        exit 1
    fi
}

case "$OS_TYPE" in
  Darwin)
    echo "Running f2py on macOS..."
    LIB_AR=$(choose_lib "libtsprocess_macos_v${VERSION}.a" "libtsprocess_macos.a")
    ;;
  Linux)
    echo "Running f2py on Linux..."
    LIB_AR=$(choose_lib "libtsprocess_linux_v${VERSION}.a" "libtsprocess_linux.a")
    ;;
  *)
    echo "Unsupported OS: $OS_TYPE"
    exit 1
    ;;
esac

# Build the Python extension module `timesat` with f2py
python -m numpy.f2py -c ./python_interface/*.f90 "$LIB_AR" -m timesat

echo "f2py compilation complete. Linked archive: $LIB_AR"
