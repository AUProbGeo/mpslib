"""Multiple Point Simulation (MPS) using MPSlib
See:
https://github.com/ergosimulation/scikit-mps
"""

from setuptools import setup, find_packages, Extension
import sys, platform
from codecs import open
from os import path

# Try to import pybind11 for native C++ bindings
try:
    from pybind11.setup_helpers import Pybind11Extension, build_ext
    has_pybind11 = True
except ImportError:
    has_pybind11 = False
    print("Warning: pybind11 not found. Native bindings will not be built.")
    print("Install with: pip install pybind11")

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Configure native C++ bindings extension if pybind11 is available
ext_modules = []
cmdclass_dict = {}

if has_pybind11:
    # Path to MPSlib root (one level up from scikit-mps)
    mpslib_root = path.abspath(path.join(here, '..'))
    mpslib_include = path.join(mpslib_root, 'mpslib')
    bindings_src = path.join(mpslib_root, 'python_bindings', 'mpslib_bindings.cpp')

    # Platform-specific library settings
    library_dirs = [path.join(mpslib_root, 'mpslib')]
    libraries = ['mpslib']
    extra_compile_args = ['-std=c++11', '-O3']
    extra_link_args = []

    if platform.system() == 'Windows':
        # Windows-specific settings
        extra_link_args.append('-static')
    elif platform.system() == 'Darwin':
        # macOS-specific settings
        extra_link_args.extend(['-Wl,-rpath,@loader_path'])
    else:
        # Linux-specific settings
        extra_link_args.extend(['-Wl,-rpath,$ORIGIN'])

    ext_modules = [
        Pybind11Extension(
            "mpslib._mpslib_native",
            [bindings_src],
            include_dirs=[mpslib_root, mpslib_include],
            library_dirs=library_dirs,
            libraries=libraries,
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args,
            cxx_std=11,
        ),
    ]
    cmdclass_dict = {"build_ext": build_ext}

setup(
    name = "scikit-mps",
    version = "1.5.0",
    description = 'Multiple point statistical (MPS) simulation',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author = 'Thomas Mejer Hansen',
    author_email = 'thomas.mejer.hansen@gmail.com',
    url = 'https://github.com/ergosimulation/mpslib/tree/master/scikit-mps', # use the URL to the github repo
    #download_url = 'https://github.com/cultpenguin/scikit-mps/master.zip', # I'll explain this in a second
    keywords = ['geostatistics', 'simulation', 'MPS'], # arbitrary keywords

    packages = find_packages(),
    install_requires=['numpy >= 1.0.2', 'matplotlib >= 1.0.0', 'scipy', 'panel', 'pyvista', 'pybind11>=2.6.0'],
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', 'bin/mps_*.exe', 'bin/mps_snesim_tree', 'bin/mps_snesim_list', 'bin/mps_genesim', 'bin/install_latest_mpslib.sh' ],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },
    # Native C++ extension modules
    ext_modules=ext_modules,
    cmdclass=cmdclass_dict,
    # Build requirements for native bindings
    setup_requires=['pybind11>=2.6.0'] if has_pybind11 else [],
    #license=open('LICENSE', encoding='utf-8').read(),
    license="LGPL",
)

