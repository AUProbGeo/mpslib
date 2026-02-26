"""Multiple Point Simulation (MPS) using MPSlib
See:
https://github.com/ergosimulation/scikit-mps
"""

from setuptools import setup, find_packages
import sys, platform
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

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
    install_requires=['numpy >= 1.0.2', 'matplotlib >= 1.0.0', 'scipy', 'panel', 'pyvista'],
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', 'bin/mps_*.exe', 'bin/mps_snesim_tree', 'bin/mps_snesim_list', 'bin/mps_genesim', 'bin/install_latest_mpslib.sh' ],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },
    #license=open('LICENSE', encoding='utf-8').read(),    
    license="LGPL",    
)

