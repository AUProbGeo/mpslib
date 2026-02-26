#!/usr/bin/env python3
"""
Minimal Example: Native C++ Bindings for MPSlib

This is the simplest possible example showing how to use native bindings.
Just one parameter change: use_native=True
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import mpslib as mps
import numpy as np

# Check if native bindings are available
try:
    from mpslib import _mpslib_native
    print("✓ Native bindings are available!\n")
except ImportError:
    print("✗ Native bindings not available. Run: make python_bindings\n")
    exit(1)

# Create a simple training image
print("Creating 20x20 training image...")
ti = np.random.randint(0, 2, (20, 20, 1)).astype(float)

# Run simulation with native C++ bindings
print("Running simulation with native C++ bindings...\n")
O = mps.mpslib(
    method='mps_genesim',
    use_native=True,          # ← This enables native bindings!
    n_real=3,
    simulation_grid_size=np.array([20, 20, 1]),
    verbose_level=1,
    debug_level=-1
)

O.ti = ti
O.run()

# Results
print(f"\n✓ Success!")
print(f"  Generated {len(O.sim)} realizations")
print(f"  Time: {O.time:.3f}s")
print(f"  Shape: {O.sim[0].shape}")
print(f"\nThat's it! Same API, faster execution.")
