scikit-mps: A python interface to MPSlib 
========================================================================================

.. image:: https://img.shields.io/pypi/v/scikit-mps.svg?style=flat-square
    :target: https://pypi.org/project/scikit-mps

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
    :target: https://en.wikipedia.org/wiki/MIT_License

.. image:: https://colab.research.google.com/assets/colab-badge.svg
    :target: https://colab.research.google.com/github/ergosimulation/mpslib/blob/master/scikit-mps/examples/mpslib_in_google_colab.ipynb

`scikit-mps` is a Python interface to MPSlib, https://github.com/ergosimulation/mpslib/,
which is a C++ library for geostatistical multiple point simulation, with implementations
of 'SNESIM', 'ENESIM', and 'GENESIM'

It contains three modules:
  * mpslib: Interacts with MPSlib
  * eas: read and write EAS/GSLIB formatted files
  * trainingimages: Access to a number of trainingimages

.. code::

   import mpslib as mps
   O=mps.mpslib(method='mps_snesim_tree')
   O.run()
   O.plot_reals()
   O.plot_etype()

PyPI
~~~~~~~~~
`<http://pypi.python.org/pypi/scikit-mps>`

Requirements
~~~~~~~~~~~~
* Numpy >= 1.0.2
* Matplotlib >= 1.0.2
* MPSlib needs to be downloaded, installed, and in the system path (https://github.com/ergosimulation/mpslib/)
  [Any 11 C++11 compiler should work, such as gcc, MinGW, MSVC]



Installing
~~~~~~~~~~~~~~
* Via pip:: 

    pip install scikit-mps

optionally download and reinstall:: 

    import mpslib as mps
    O=mps.mpslib
    O.compile_mpslib()

* From source code 

.. code::

   cd ROOT_OF_MPSLIB/python   
   pip install .
   cd ROOT_OF_MPSLIB
   make clean
   make   

If you wish to develop the scikit-mps package, then install it in editable developer mode using

.. code::

    pip install -e .

