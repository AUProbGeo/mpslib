# MPSlib Native C++ Bindings

## Overview

MPSlib now supports **direct C++ bindings** using pybind11, enabling in-process execution without subprocess overhead. This eliminates process spawning time and provides better performance for workflows with many simulations.

## Quick Start

Simply add `use_native=True` to your `mpslib()` call:

```python
import mpslib as mps
import numpy as np

# Traditional subprocess mode
O = mps.mpslib(method='mps_genesim', n_real=5)

# NEW: Native C++ bindings mode
O = mps.mpslib(method='mps_genesim', use_native=True, n_real=5)
```

That's it! The API is identical - just better performance.

## Building Native Bindings

### Prerequisites
```bash
pip install pybind11
```

### Compile from MPSlib root directory
```bash
# Clean and rebuild C++ library
make clean && make

# Build Python bindings
make python_bindings

# Or install the package
cd scikit-mps
pip install -e .
```

## Example Scripts

### 1. `ex_native_bindings_simple.py`
**Quick comparison** between subprocess and native modes.
- Minimal code
- Side-by-side timing comparison
- Good starting point

```bash
python ex_native_bindings_simple.py
```

### 2. `ex_native_bindings_performance.py`
**Comprehensive performance benchmark** with visualization.
- Detailed comparison
- Generates plots
- Multiple test scenarios

```bash
python ex_native_bindings_performance.py
```

## Performance

Expected speedup varies by workload:

| Scenario | Grid Size | Realizations | Speedup |
|----------|-----------|--------------|---------|
| Small grid, many realizations | 20×20 | 50 | ~1.3-1.5x |
| Medium grid | 50×50 | 20 | ~1.1-1.3x |
| Large grid, few realizations | 100×100 | 5 | ~1.1-1.2x |

**Note:** Speedup primarily comes from eliminating subprocess overhead. For very long-running simulations, the benefit is smaller. For quick simulations repeated many times, the benefit is larger.

## Supported Algorithms

All three MPSlib algorithms support native bindings:

- ✅ `mps_genesim` (ENESIM/GENESIM/Direct Sampling)
- ✅ `mps_snesim_tree` (SNESIM with tree storage)
- ✅ `mps_snesim_list` (SNESIM with list storage)

## Backward Compatibility

- **Fully backward compatible** - existing code works unchanged
- **Automatic fallback** - if native bindings unavailable, uses subprocess
- **Opt-in** - `use_native=False` by default
- **No API changes** - same methods, same parameters

## Checking Availability

```python
try:
    from mpslib import _mpslib_native
    print("✓ Native bindings available")
    print("Available classes:", dir(_mpslib_native))
except ImportError:
    print("✗ Native bindings not compiled")
```

## Troubleshooting

### "Native bindings not available"
1. Make sure you've built them: `make python_bindings`
2. Check that `scikit-mps/mpslib/_mpslib_native*.so` exists
3. Try reinstalling: `cd scikit-mps && pip install -e .`

### "Cannot import _mpslib_native"
1. Check Python version compatibility (requires Python 3.7+)
2. Ensure pybind11 is installed: `pip install pybind11`
3. Rebuild: `make clean && make && make python_bindings`

### Slower than subprocess mode
This can happen if:
- Running only a few realizations (subprocess overhead is small)
- Very large grids (computation time dominates)
- Disk I/O is slow (both modes still write files)

The native bindings are most beneficial when:
- Running many simulations sequentially
- Small to medium grid sizes
- Iterative workflows (parameter tuning, sensitivity analysis)

## Architecture

```
Before:  Python → [write files] → subprocess → C++ → [write files] → Python
                   └─ overhead ─┘                     └─ overhead ─┘

After:   Python → direct C++ call (in-process) → return results
                   └─ no overhead ─┘
```

## Future Improvements

Current implementation still uses file I/O for results. Future enhancements could include:

1. **Zero-copy grid access** using pybind11 buffer protocol
2. **Direct numpy array returns** eliminating file I/O entirely
3. **Full in-memory mode** for parameter-only initialization
4. **Parallel execution** with better thread management

These would provide 3-5x total speedup.

## Technical Details

- **Technology**: pybind11 for Python/C++ interoperability
- **Build**: Creates `_mpslib_native.cpython-*.so` shared library
- **Classes**: Exposes `MPSAlgorithm`, `ENESIM_GENERAL`, `SNESIMTree`, `SNESIMList`
- **Memory**: Automatic reference counting, no manual memory management
- **Thread safety**: Same as C++ code (use `n_threads` parameter)

## Contributing

To extend the native bindings:

1. Add functionality to C++ classes in `mpslib/MPSAlgorithm.h`
2. Expose in `python_bindings/mpslib_bindings.cpp`
3. Rebuild: `make python_bindings`
4. Add tests and examples

See `python_bindings/mpslib_bindings.cpp` for the binding implementation.

## License

Same as MPSlib - LGPL 3.0

## Questions?

- Issues: https://github.com/ergosimulation/mpslib/issues
- Documentation: https://github.com/ergosimulation/mpslib
