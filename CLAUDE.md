# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

MPSlib is a C++ library for geostatistical multiple-point simulation (MPS), with Python bindings (scikit-mps). The library implements three main MPS algorithms:
- **SNESIM** (Single Normal Equation Simulation): Two variants - `mps_snesim_tree` and `mps_snesim_list`
- **ENESIM** (Extended Normal Equation Simulation): Available as `mps_genesim`
- **GENESIM**: A generalized implementation that can behave like ENESIM or Direct Sampling

## Build Commands

### Compile C++ executables
```bash
make                    # Build all three executables
make mps_genesim        # Build GENESIM only
make mps_snesim_tree    # Build SNESIM (tree variant) only
make mps_snesim_list    # Build SNESIM (list variant) only
```

### Clean build artifacts
```bash
make clean              # Remove object files and library
make cleanexe           # Remove executables, objects, and library
make cleano             # Remove only object files
```

### Copy executables to Python package
```bash
make copy               # Copy compiled binaries to scikit-mps/mpslib/bin/
```

### Python package installation
```bash
pip install scikit-mps                           # Install from PyPI
cd scikit-mps && pip install .                   # Install from source
cd scikit-mps && pip install -e .                # Install in editable/developer mode
```

## Architecture

### C++ Core Structure

The C++ library is organized with a class hierarchy:

1. **Base Class**: `MPSAlgorithm` (`mpslib/MPSAlgorithm.h/cpp`)
   - Abstract base class for all MPS algorithms
   - Handles simulation grids, training images, hard/soft data, paths, and I/O
   - Key grids: `_sg` (simulation), `_hdg` (hard data), `_TI` (training image), `_cg` (conditional), `_ent` (entropy)
   - Implements core functionality: file I/O, grid initialization, neighbor search, PDF sampling
   - Pure virtual: `_simulate()` and `startSimulation()` must be implemented by subclasses

2. **Algorithm Implementations**:
   - `SNESIM` (`mpslib/SNESIM.h/cpp`): Base for SNESIM algorithms using pattern dictionaries
   - `ENESIM` (`mpslib/ENESIM.h/cpp`): Implements ENESIM/GENESIM with training image scanning
   - `SNESIMTree` (`SNESIMTree.h/cpp`): Tree-based storage for conditional distributions
   - `SNESIMList` (`SNESIMList.h/cpp`): List-based storage for conditional distributions
   - `ENESIM_GENERAL` (`ENESIM_GENERAL.h/cpp`): GENESIM wrapper

3. **Utility Classes**:
   - `Coords3D` (`mpslib/Coords3D.h/cpp`): 3D coordinate handling
   - `Coords4D` (`mpslib/Coords4D.h/cpp`): 4D coordinate handling (X,Y,Z + data value)
   - `Utility` (`mpslib/Utility.h/cpp`): General utilities including coordinate conversions
   - `IO` (`mpslib/IO.h/cpp`): File I/O for EAS/GSLIB formats

4. **Executables**:
   - `mps_genesim.cpp`: Main for GENESIM
   - `mps_snesim_tree.cpp`: Main for SNESIM with tree storage
   - `mps_snesim_list.cpp`: Main for SNESIM with list storage

### Python Interface (scikit-mps)

Located in `scikit-mps/mpslib/`:
- `mpslib.py`: Main wrapper class interfacing with C++ executables via subprocess
- `eas.py`: EAS/GSLIB format file reading/writing
- `trainingimages.py`: Built-in training images access
- `plot.py`: Visualization utilities
- `bin/`: Directory containing compiled C++ executables

### Key Differences Between Algorithms

- **SNESIM (tree/list)**: Pre-scans training image to build pattern database, faster simulation
  - Tree vs List: Different memory structures for storing conditional distributions
  - Uses template/search neighborhood defined by `tem_nx`, `tem_ny`, `tem_nz`
  - Supports multiple grids via `n_mul_grids` parameter

- **GENESIM**: Scans training image during simulation, more flexible
  - When `n_max_count_cpdf=infinity`: behaves like classic ENESIM (full TI scan)
  - When `n_max_count_cpdf=1`: behaves like Direct Sampling
  - Controlled by `n_max_ite` (max iterations) and `n_cond` (max conditional points)

## Parameter Files

All algorithms read configuration from text files with format: `Parameter description # value`

**Common parameters** (all algorithms):
- Simulation grid: dimensions, origin, cell size
- Training image filename
- Output directory
- Hard data: filename, search radius
- Soft data: categories, filenames
- Random seed, number of realizations
- Shuffle options for simulation/TI paths
- Debug mode (-2 to 3)

**SNESIM-specific**:
- `n_mul_grids`: Number of multiple grids
- `n_min_node`: Minimum node count in conditional distribution
- `n_cond`: Max conditional points (within template)
- `tem_nx/ny/nz`: Template/search neighborhood size

**GENESIM-specific**:
- `n_max_count_cpdf`: Max counts for conditional PDF (controls ENESIM vs Direct Sampling behavior)
- `n_max_ite`: Max iterations scanning TI
- `n_cond`: Max conditional data points

## Data Formats

- **Training Images**: EAS/GSLIB ASCII format. First line contains dimensions as `nX nY nZ`
- **Hard Data**: EAS format with 4 columns: X, Y, Z, D (data value)
- **Soft Data**: Grid files (one per category except last), same size as simulation grid
- **Output**: Simulation grids in EAS format (plus optional GRD3 for GeoScene3D)

## Running Simulations

### C++ executables
```bash
./mps_genesim [parameter_file.txt]           # Default: mps_genesim.txt
./mps_snesim_tree [parameter_file.txt]       # Default: mps_snesim.txt
./mps_snesim_list [parameter_file.txt]       # Default: mps_snesim.txt
```

### Python interface
```python
import mpslib as mps
O = mps.mpslib(method='mps_snesim_tree')     # or 'mps_snesim_list', 'mps_genesim'
O.parameter_filename = 'my_params.txt'
O.run()
O.plot_reals()          # Plot realizations
O.plot_etype()          # Plot E-type (mean)
```

## Compiler Requirements

- C++11 standard or later
- Tested compilers: GCC (>= 4.8.1), MinGW-w64, MSVC, Clang
- Linux/macOS: Use `make` with system compiler
- Windows: Recommend MINGW-w64 via MSYS2 or use Visual Studio projects in `msvc2019/`

## Project Build System

The library is built as static library `mpslib/mpslib.a`, then linked with each executable. Compiler flags optimize for performance (`-O3 -static`) with C++11 support.
