# MPSlib: a C++ class for Multiple-Point based sequential Simulation

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ergosimulation/mpslib/blob/master/scikit-mps/examples/mpslib_in_google_colab.ipynb)
[![Documentation Status](https://readthedocs.org/projects/tag/badge/?version=latest)](https://mpslib.readthedocs.io/en/latest/)
[![PyPI version](https://badge.fury.io/py/scikit-mps.svg)](https://badge.fury.io/py/scikit-mps)

MPSlib provides a set of algorithms for simulation of models based on a multiple point
statistical model inferred from a training image.

The goal of developing these codes has been to produce a set of algorithms, based
on sequential simulation, for simulation of multiple point statistical models.
The code should be easy to compile and extend, and should be allowed for both
commercial and non-commercial use.

> MPSlib (version 1.0) has been developed by
[I-GIS](http://www.i-gis.dk/)  (Le Thanh Vu and Torben Bach) 
and
[Solid Earth Physics, Niels Bohr Institute](http://imgp.nbi.ku.dk/) (Thomas Mejer Hansen).

> MPSlib (version >1.0) maintained by
Thomas Mejer Hansen (tmeha@geo.au.dk)

Development has been funded by the Danish National Hightech Foundation (now: the Innovation fund) through the ERGO (Effective high-resolution Geological Modeling) project, a collaboration between
[IGIS](http://i-gis.dk/),
[GEUS](http://geus.dk/), and
[Niels Bohr Institute](http://nbi.ku.dk/).

## Try in Google Colab [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ergosimulation/mpslib/blob/master/scikit-mps/examples/mpslib_in_google_colab.ipynb)
Try out MPSlib using the Python interface (scikit-mps) through Google Colab.
<br><br>

### Python package  [![PyPI version](https://badge.fury.io/py/scikit-mps.svg)](https://badge.fury.io/py/scikit-mps)

Perhaps the easiest way to get started is to install the scikit-mps packages that provides access to MPSlib through Python. Install scikit-mps using

    pip install scikit-mps

Get started using 

    import mpslib as mps
    O=mps.mpslib()
    O.run()
    O.plot()
    
Check the documentaion for a number of [Python Notebook examples](https://mpslib.readthedocs.io/en/develop/Notebooks/index.html). These are also available at [Github](scikit-mps/examples/).

## Documentation [![Documentation Status](https://readthedocs.org/projects/tag/badge/?version=latest)](https://mpslib.readthedocs.io/en/latest/)

Documentation is available through [https://mpslib.readthedocs.io/en/latest/](https://mpslib.readthedocs.io/en/latest/).


## Download
The latest releases, containing statically compiled binaries for Windows and Linux, can be found here:
[https://github.com/ergosimulation/mpslib/releases/latest](https://github.com/ergosimulation/mpslib/releases/latest).

The source code can be downloaded from Github
[https://github.com/ergosimulation/mpslib](https://github.com/ergosimulation/mpslib)
and compiled using
```bash
git clone https://github.com/ergosimulation/mpslib.git MPSlib
cd MPSlib
make
```

## Compilation
The MPSlib codes are written in standard [C++11](https://www.wikiwand.com/en/C%2B%2B11).

MPSlib has been developed using the GNU C++ compiler (tested on Windows, Linux and OSX), and Visual Studio C++.

## Linux or macOS, with C++11
In general, MPSLIB can be compiled using GCC ( > 4.8.1 ),  using
```bash
make
```

## Windows: (MINGW-W64)
Compiler flags:
```bash
CPPFLAGS = -static -O3
```
MPSlib has been tested using MINGW in Windows. Note that not all builds of MINGW will work. Therefore, we specifically make use of MINGW-w64 ([http://MINGW-w64.org/doku.php]), which can be obtained in a number of ways.

One (recommended) approach is to make use of MSYS2. Follow the guide at [http://msys2.github.io/] to install MSYS2, and then install the MINGW_w64 toolchain using:
```bash
pacman -S MINGW-w64-x86_64-gcc
pacman -S make
```

## Release history

### v1.5 [26-02-2022]
Python interface (scikit-mps) updated. scikit-mps can now be installed using 

    pip install scikit-mps

### v1.4 [01-01-2021]
Support for sequential estimation

### v1.0 [15-02-2016]
Initial release of MPSlib, with
`mps_snesim_list`,
`mps_snesim_tree`, and
`mps_genesim`.


## Running MPS algorithms
The MPS algorithms are run from the command line prompt using a parameter filename as an argument -
if there is no argument file, the default parameter file is assumed to the be name of the simulation algorithm appended with `.txt`.

Therefore
```
mps_genesim
```
and

```
mps_genesim mps_genesim.txt
```
have the same meaning.


## SNESIM: `mps_snesim_tree` and `mps_snesim_list`
The `mps_snesim_tree` and `mps_snesim_list` differ only in the way conditional data is stored in memory - using either a tree or a list structure.

Both algorithms share the same format for the required parameter file:
```
Number of realizations # 1
Random Seed (0 for not random seed) # 0
Number of multiple grids # 2
Min Node count (0 if not set any limit) # 0
Max Conditional count (-1 if not using any limit) # -1
Search template size X # 5
Search template size Y # 5
Search template size Z # 1
Simulation grid size X # 100
Simulation grid size Y # 100
Simulation grid size Z # 1
Simulation grid world/origin X # 0
Simulation grid world/origin Y # 0
Simulation grid world/origin Z # 0
Simulation grid grid cell size X # 1
Simulation grid grid cell size Y # 1
Simulation grid grid cell size Z # 1
Training image file (spaces not allowed) # TI/mps_ti.dat
Output folder (spaces in name not allowed) # output/.
Shuffle Simulation Grid path (1 : random, 0 : sequential) # 1
Maximum number of counts for condtitional pdf # 10000
Shuffle Training Image path (1 : random, 0 : sequential) # 1
HardData filaneme  (same size as the simulation grid)# harddata/mps_hard_grid.dat
HardData seach radius (world units) # 15
Softdata categories (separated by ;) # 1;0
Soft datafilenames (separated by ; only need (number_categories - 1) grids) # softdata/mps_soft_xyzd_grid.dat
Number of threads (minimum 1, maximum 8 - depend on your CPU) # 1
Debug mode(2: write to file, 1: show preview, 0: show counters, -1: no ) # 1
```
<br><br>
A few lines in the parameter files are specific to the SNESIM type algorithms, and will be discussed below:
`n_mul_grids`: This parameter defines the number of multiple grids used. By assigning to 0, no multiple grid will be used.
<br><br>
`n_min_node`: The search tree will be searched only to the level where the number of counts in the conditional distribution exceeds `n_min_node`.
<br><br>
`n_cond`: Refers to the maximum number of conditional points used, within the search template.
<br><br>
`tem_nx, tem_ny, tem_nz`: The search template specifies the size of the template that is used to prescan the training picture and save the conditional distribution for all data template configurations - through a tree or list.
<br><br>
## Generalized ENESIM: mps_genesim
`mps_genesim` is a generalized version of the ENESIM algorithm, that can be used to perform MPS simulation
similar to both ENESIM and Direct sampling (and in-between) depending how it is run.

An example of a parameter file is:
```
Number of realizations # 1
Random Seed (0 `random` seed) # 0
Maximum number of counts for conditional pdf # 1
Max number of conditional point # 25
Max number of iterations # 10000
Simulation grid size X # 18
Simulation grid size Y # 16
Simulation grid size Z # 1
Simulation grid world/origin X # 0
Simulation grid world/origin Y # 0
Simulation grid world/origin Z # 0
Simulation grid grid cell size X # 1
Simulation grid grid cell size Y # 1
Simulation grid grid cell size Z # 1
Training image file (spaces not allowed) # ti.dat
Output folder (spaces in name not allowed) # .
Shuffle Simulation Grid path (1 : random, 0 : sequential) # 2
Shuffle Training Image path (1 : random, 0 : sequential) # 1
HardData filename  (same size as the simulation grid)# conditional.dat
HardData seach radius (world units) # 1
Softdata categories (separated by ;) # 0;1
Soft datafilenames (separated by ; only need (number_categories - 1) grids) # soft.dat
Number of threads (minimum 1, maximum 8 - depend on your CPU) # 1
Debug mode(2: write to file, 1: show preview, 0: show counters, -1: no ) # -2
```

A few lines in the parameter files are specific to the GENESIM type algorithm, and will be discussed below:
`n_max_count_cpdf`: This parameter defines the maximum number of counts in the conditional distribution obtained from the training image - when `n_max_count_cpdf` has been reached the scanning of the training image stops.

**Observation: In case `n_max_count_cpdf=infinity`, `mps_genesim` will behave exactly to the classical ENESIM
algorithm, where the full training is scanned at each iteration. Also, in case `n_max_count_cpdf=1`, `mps_genesim` will behave similar to the Direct Sampling algorithm.**
<br><br>
`n_cond`: A maximum of `n_cond` conditional data are considered at each iteration when inferring the
conditional pdf from the training image.
<br><br>
`n_max_ite`: A maximum of iterations of searching through the training image are performed.
<br><br>
## General options in the parameter files
The following entries appear in all parameter files:
<br><br>
`Number of realizations`: The number of realizations to run and generate.
<br><br>
`random_seed`: An integer that determines the random seed. A fixed value will return the same realizations for each run.
<br>
**Observation: Assigning `0` to `random_seed` will generate a new seed at each iteration**
<br><br>
`simulation_grid_size`: The dimensions of the simulation grid cell, a `numpy` array with 3 dimensions - X, Y, Z.
<br><br>
`origin`: Simulation grid origin X, Y, Z, must be a `numpy` array of integers - refers to the value of the coordinates in the X, Y, and Z direction.
<br><br>
`grid_cell_size`: The size of each pixel in the simulation grid, in the X, Y, and Z direction.
<br><br>
`ti_fnam`: The name of the training image file (no spaces allowed). It must be in GLSIB/EAS ASCII format, and the first line (the 'title') must contain the dimension of the training file as nX, nY, nZ.
<br><br>
`out_folder`: The path to the folder containing all output. Use forward slash '/' to separate folders - also, spaces in the folder name are not allowed.
<br><br>
`shuffle_simulation_grid`: Shuffle simulation grid path:
- `0`: follows a sequential path through the simulation grid.
- `1`: follows a random path through the simulation grid.
- `2`: follows a preferential path.
<br><br>
`n_max_cpdf_count`: The maximum number of counts for conditional PDF.
<br><br>
`shuffle_ti_grid`: Shuffle Training Image path - does not affect SNESIM type algrothms.
- `0`: sequential path
- `1`: random path
<br><br>
`hard_data_fnam`: Hard data filename - this file consists of an EAS archive with 4 columns: X, Y, Z, and D
<br><br>
`hard_data_search_radius`: World units around the search radius for hard data.
<br><br>
`soft_data_categories`: Soft data categories, separated by `;`.
<br><br>
`soft_data_fnam`: Soft data filenames - separated by `;` only need `number_categories - 1` grids
<br><br>
`n_threads`: Refers to the quantity of CPUs to use for simulation (minimum 1, maximum 8 - depends on your CPU)
Currently not used.
<br><br>
`debug_level`: Refers to the level of debugging during processing. 
- `-2`: No information is written to screen or files on disk
- `-1`: + Simulation output is written to files on disk.
- `0`: + Information about the simulations is written to the console
- `1`: + Simulated realization(s) are shown in terminal
- `2`: + Extra information is written to disk (Random path, ...)
- `3`: + Debug information written to screen (in general not useful for an end-user)


