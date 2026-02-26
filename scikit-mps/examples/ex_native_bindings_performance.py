#!/usr/bin/env python3
"""
Example: Using MPSlib Native C++ Bindings for Faster Simulation

This example demonstrates the new direct C++ bindings feature that eliminates
subprocess overhead by calling the simulation algorithms in-process.

Performance improvement: ~1.1-1.5x speedup for typical workflows
Main benefits:
  - No subprocess spawning overhead
  - No process startup time per simulation
  - Better for workflows with many quick simulations
  - Same API as traditional mode

Requirements:
  - Native bindings must be compiled (run: make python_bindings)
  - pybind11 installed (pip install pybind11)
"""

import numpy as np
import matplotlib.pyplot as plt
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import mpslib as mps


def create_simple_ti(size=50):
    """Create a simple binary training image with channel structure"""
    ti = np.zeros((size, size, 1))

    # Add some channel-like features
    for i in range(5):
        y_start = np.random.randint(0, size)
        x_start = np.random.randint(0, size)
        width = np.random.randint(3, 8)

        for j in range(size):
            x = int(x_start + j * 0.3 + np.random.randn() * 2)
            if 0 <= x < size and 0 <= y_start < size:
                for dy in range(-width//2, width//2):
                    if 0 <= y_start + dy < size:
                        ti[y_start + dy, x, 0] = 1

    return ti


def run_simulation(use_native, n_real=5, grid_size=(40, 40, 1), verbose=True):
    """
    Run MPSlib simulation with specified mode

    Args:
        use_native: If True, use native C++ bindings; if False, use subprocess
        n_real: Number of realizations
        grid_size: Simulation grid size (x, y, z)
        verbose: Print progress messages

    Returns:
        (mpslib_object, elapsed_time)
    """
    mode_name = "Native C++" if use_native else "Subprocess"

    if verbose:
        print(f"\n{'='*60}")
        print(f"Running with: {mode_name} mode")
        print(f"{'='*60}")

    # Create MPSlib object
    O = mps.mpslib(
        method='mps_genesim',
        use_native=use_native,
        n_real=n_real,
        rseed=42,
        simulation_grid_size=np.array(grid_size),
        verbose_level=0 if not verbose else 1,
        debug_level=-1,
        n_max_ite=100000,
        n_max_cpdf_count=10,
        n_cond=25,
        ti_fnam=f'ti_{mode_name.replace(" ", "_").lower()}.dat'
    )

    # Create and set training image
    ti = create_simple_ti(size=50)
    O.ti = ti

    # Run simulation and measure time
    if verbose:
        print(f"Simulating {n_real} realizations on {grid_size[0]}×{grid_size[1]} grid...")

    t_start = time.time()
    success = O.run(silent=not verbose)
    t_elapsed = time.time() - t_start

    if verbose:
        print(f"Status: {'✓ Success' if success else '✗ Failed'}")
        print(f"Time: {t_elapsed:.3f}s")
        print(f"Average per realization: {t_elapsed/n_real:.3f}s")

    return O, t_elapsed


def compare_modes():
    """Compare subprocess vs native bindings performance"""
    print("\n" + "="*70)
    print("PERFORMANCE COMPARISON: Subprocess vs Native Bindings")
    print("="*70)

    # Test parameters
    n_real = 10
    grid_size = (40, 40, 1)

    print(f"\nTest Configuration:")
    print(f"  Method: mps_genesim (ENESIM/Direct Sampling)")
    print(f"  Grid size: {grid_size[0]}×{grid_size[1]}×{grid_size[2]}")
    print(f"  Realizations: {n_real}")
    print(f"  Training image: 50×50 synthetic channels")

    # Test 1: Subprocess mode (traditional)
    print("\n" + "-"*70)
    print("TEST 1: Traditional Subprocess Mode")
    print("-"*70)
    O_subprocess, t_subprocess = run_simulation(
        use_native=False,
        n_real=n_real,
        grid_size=grid_size,
        verbose=True
    )

    # Test 2: Native bindings mode
    print("\n" + "-"*70)
    print("TEST 2: Native C++ Bindings Mode")
    print("-"*70)
    O_native, t_native = run_simulation(
        use_native=True,
        n_real=n_real,
        grid_size=grid_size,
        verbose=True
    )

    # Results summary
    speedup = t_subprocess / t_native
    time_saved = t_subprocess - t_native
    percent_saved = 100 * time_saved / t_subprocess

    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    print(f"  Subprocess mode:      {t_subprocess:6.3f}s")
    print(f"  Native bindings:      {t_native:6.3f}s")
    print(f"  ")
    print(f"  Speedup:              {speedup:6.2f}x")
    print(f"  Time saved:           {time_saved:6.3f}s ({percent_saved:.1f}%)")
    print(f"  ")
    print(f"  Per-realization (subprocess): {t_subprocess/n_real:.3f}s")
    print(f"  Per-realization (native):     {t_native/n_real:.3f}s")
    print("="*70)

    return O_subprocess, O_native, speedup


def plot_comparison(O_subprocess, O_native):
    """Plot side-by-side comparison of results"""
    print("\nGenerating comparison plots...")

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('MPSlib: Subprocess vs Native Bindings Comparison', fontsize=16)

    # Plot first 3 realizations from each mode
    for i in range(3):
        # Subprocess results
        ax_sub = axes[0, i]
        if i < len(O_subprocess.sim):
            im = ax_sub.imshow(O_subprocess.sim[i][:, :, 0], cmap='viridis')
            ax_sub.set_title(f'Subprocess - Real #{i+1}')
            ax_sub.axis('off')
            plt.colorbar(im, ax=ax_sub, fraction=0.046)

        # Native bindings results
        ax_nat = axes[1, i]
        if i < len(O_native.sim):
            im = ax_nat.imshow(O_native.sim[i][:, :, 0], cmap='viridis')
            ax_nat.set_title(f'Native Bindings - Real #{i+1}')
            ax_nat.axis('off')
            plt.colorbar(im, ax=ax_nat, fraction=0.046)

    plt.tight_layout()

    # Save figure
    output_file = 'native_bindings_comparison.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Saved comparison plot to: {output_file}")

    return fig


def simple_example():
    """Simple example showing basic usage"""
    print("\n" + "="*70)
    print("SIMPLE EXAMPLE: Using Native Bindings")
    print("="*70)

    print("""
This example shows the minimal code needed to use native bindings.
Just add 'use_native=True' to your mpslib() call!
    """)

    print("Code:")
    print("-" * 70)
    print("""
import mpslib as mps
import numpy as np

# Create simulation object with native bindings enabled
O = mps.mpslib(
    method='mps_genesim',
    use_native=True,          # ← Enable native C++ bindings
    n_real=3,
    simulation_grid_size=np.array([30, 30, 1])
)

# Set training image
O.ti = np.random.randint(0, 2, (30, 30, 1)).astype(float)

# Run simulation (in-process, no subprocess!)
O.run()

# Results in O.sim as usual
print(f"Generated {len(O.sim)} realizations")
    """)
    print("-" * 70)

    # Actually run it
    print("\nRunning the example code...")
    O = mps.mpslib(
        method='mps_genesim',
        use_native=True,
        n_real=3,
        simulation_grid_size=np.array([30, 30, 1]),
        verbose_level=0,
        debug_level=-1,
        ti_fnam='example_ti.dat'
    )

    O.ti = np.random.randint(0, 2, (30, 30, 1)).astype(float)

    t_start = time.time()
    success = O.run(silent=True)
    t_elapsed = time.time() - t_start

    print(f"\n✓ Complete!")
    print(f"  Generated {len(O.sim)} realizations in {t_elapsed:.3f}s")
    print(f"  Shape: {O.sim[0].shape}")
    print("="*70)


def main():
    """Main function"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█" + "  MPSlib Native C++ Bindings Example".center(68) + "█")
    print("█" + " "*68 + "█")
    print("█"*70 + "\n")

    # Check if native bindings are available
    try:
        from mpslib import _mpslib_native
        print("✓ Native bindings are available and loaded successfully!")
        print(f"  Available classes: {', '.join([c for c in dir(_mpslib_native) if not c.startswith('_')])}")
    except ImportError:
        print("✗ Native bindings not available!")
        print("  To build native bindings, run from the mpslib root:")
        print("    make clean && make")
        print("    make python_bindings")
        print("  Or: cd scikit-mps && pip install -e .")
        return

    # Run simple example
    simple_example()

    # Run performance comparison
    O_subprocess, O_native, speedup = compare_modes()

    # Generate plots
    try:
        plot_comparison(O_subprocess, O_native)
        print("\n✓ All tests completed successfully!")

        if speedup > 1.0:
            print(f"\n🚀 Native bindings are {speedup:.2f}x faster!")
        else:
            print(f"\n⚠ Native bindings showed {speedup:.2f}x performance")
            print("   (Speedup varies by grid size and number of realizations)")

    except Exception as e:
        print(f"\n⚠ Could not generate plots: {e}")
        print("   (matplotlib may not be available)")

    print("\n" + "="*70)
    print("BENEFITS OF NATIVE BINDINGS:")
    print("="*70)
    print("  ✓ Faster execution (no subprocess overhead)")
    print("  ✓ Same API - just add use_native=True")
    print("  ✓ Automatic fallback if bindings unavailable")
    print("  ✓ Better for workflows with many simulations")
    print("  ✓ In-process execution for easier debugging")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
