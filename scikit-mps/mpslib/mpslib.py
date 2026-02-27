import numpy as np
import os
import subprocess
from . import plot as plot
from . import eas as eas
from . import trainingimages as trainingimages
# from . import trainingimages
import time

# Try to import native C++ bindings
try:
    from . import _mpslib_native
    HAS_NATIVE_BINDINGS = True
except ImportError:
    _mpslib_native = None
    HAS_NATIVE_BINDINGS = False


def is_exe(filename):
    return os.path.isfile(filename) and os.access(filename, os.X_OK)


# %% FUNCTIONS FOR PLOTTING OF EAS FILES


# %% THE CLASS
class mpslib:

    def __init__(self, parameter_filename='mps.txt', method='mps_genesim', debug_level=-1, n_real=1, rseed=1,
                 out_folder='.', ti_fnam='ti.dat', simulation_grid_size=np.array([40, 20, 1]),
                 mask_fnam='mask.dat',
                 origin=np.zeros(3), grid_cell_size=np.array([1, 1, 1]), hard_data_fnam='hard.dat',
                 shuffle_simulation_grid=2, entropyfactor_simulation_grid=4, shuffle_ti_grid=1,
                 hard_data_search_radius=1,
                 soft_data_categories=np.arange(2), soft_data_fnam='soft.dat', n_threads=-1, verbose_level=0,
                 template_size=np.array([8, 7, 1]), n_multiple_grids=3, n_cond=16, n_cond_soft=1, n_min_node_count=0,
                 n_max_ite=1000000, n_max_cpdf_count=1, distance_measure=1, distance_max=0, distance_pow=1,
                 max_search_radius=10000000, max_search_radius_soft=10000000,
                 remove_gslib_after_simulation=1, gslib_combine=1, ti=np.empty(0),
                 colocate_dimension=0,
                 do_estimation=0,
                 do_entropy=0,
                 distance_min=-1, #OBSOLETE
                 mpslib_exe_folder='',
                 use_native=False):
        '''Initialize variables in Class'''

        # Next few lines to keep compatibility with old (and misleading) use of O.par['dist_min']-->O.par['dist_max']
        if (distance_min>-1):
            distance_max = distance_min
        
        self.blank_grid = None
        self.blank_val = np.nan
        self.parameter_filename = parameter_filename.lower()  # change string to lower case
        self.method = method.lower()  # change string to lower case
        self.verbose_level = verbose_level

        # Native bindings configuration
        self.use_native = use_native and HAS_NATIVE_BINDINGS
        self._native_algo = None
        if use_native and not HAS_NATIVE_BINDINGS:
            print("Warning: Native bindings requested but not available. Falling back to subprocess mode.")
        
        self.remove_gslib_after_simulation = remove_gslib_after_simulation  # remove individual gslib fiels after simulation
        self.gslib_combine = gslib_combine  # combine realzations into one gslib file

        self.sim = None

        self.par = {}

        self.par['n_real'] = n_real
        self.par['rseed'] = rseed
        self.par['n_max_cpdf_count'] = n_max_cpdf_count
        self.par['out_folder'] = out_folder
        self.par['ti_fnam'] = ti_fnam.lower()  # change string to lower case
        self.par['simulation_grid_size'] = simulation_grid_size
        self.par['origin'] = origin
        self.par['grid_cell_size'] = grid_cell_size
        self.par['mask_fnam'] = mask_fnam.lower() # change string to lower case
        self.par['hard_data_fnam'] = hard_data_fnam.lower()  # change string to lower case
        self.par['shuffle_simulation_grid'] = shuffle_simulation_grid
        self.par['entropyfactor_simulation_grid'] = entropyfactor_simulation_grid
        self.par['shuffle_ti_grid'] = shuffle_ti_grid
        self.par['hard_data_search_radius'] = hard_data_search_radius
        self.par['soft_data_categories'] = soft_data_categories
        self.par['soft_data_fnam'] = soft_data_fnam.lower()  # change string to lower case
        self.par['n_threads'] = n_threads
        self.par['debug_level'] = debug_level
        self.par['do_estimation'] = do_estimation
        self.par['do_entropy'] = do_entropy


        # if the method is GENSIM, add package specific parameters
        if self.method == 'mps_genesim':
            self.par['n_cond'] = n_cond
            self.par['n_cond_soft'] = n_cond_soft
            self.par['n_max_ite'] = n_max_ite
            self.par['n_max_cpdf_count'] = n_max_cpdf_count
            self.par['distance_measure'] = distance_measure
            self.par['distance_max'] = distance_max
            self.par['distance_pow'] = distance_pow
            self.par['colocate_dimension'] = colocate_dimension
            self.par['max_search_radius'] = max_search_radius
            self.par['max_search_radius_soft'] = max_search_radius_soft
            # self.par['exe'] = 'mps_genesim'

        if self.method[0:10] == 'mps_snesim':
            self.par['template_size'] = template_size
            self.par['n_multiple_grids'] = n_multiple_grids
            self.par['n_min_node_count'] = n_min_node_count
            self.par['n_cond'] = n_cond
            # self.exe = 'mps_mps_snesim_tree'

        # Set verbose_level on eas as well
        eas.debug_level = self.par['debug_level'];
        
        # Check if on windows
        self.iswin = 0
        if (os.name == 'nt'):
            self.iswin = 1

        # Find folder with executable files
        # Fiest check the root folder of mpslib, then mslib/scikit-mps/mpslib/bin
        mpslib_py_path, fn = os.path.split(__file__)
        if len(mpslib_exe_folder)==0:
            
            mpslib_exe_folder = os.path.abspath(os.path.join(mpslib_py_path, 'bin'))
            if (self.verbose_level>0):
                print("Testing if EXEcutables in  %s" % (mpslib_exe_folder) )
            self.mpslib_exe_folder = mpslib_exe_folder
            if self.which(method,0) is None:
                mpslib_exe_folder = os.path.abspath(os.path.join(mpslib_py_path, '..', '..'))
                self.mpslib_exe_folder = mpslib_exe_folder
                if (self.verbose_level>0):
                    print("Testing if EXEcutables in  %s" % (mpslib_exe_folder) )
                
            self.which(method,0)
            
        if self.verbose_level>-1:
            print("Using %s installed in %s (scikit-mps in %s)" % (method,self.mpslib_exe_folder,__file__))
        
    def update_xyz(self):    
        # update self.x, self.y, self.z
        if (hasattr(self, 'x') == 0):
            self.x = np.arange(self.par['simulation_grid_size'][0]) * self.par['grid_cell_size'][0] + self.par['origin'][0]
        if (hasattr(self, 'y') == 0):
            self.y = np.arange(self.par['simulation_grid_size'][1]) * self.par['grid_cell_size'][1] + self.par['origin'][1]
        if (hasattr(self, 'z') == 0):
            self.z = np.arange(self.par['simulation_grid_size'][2]) * self.par['grid_cell_size'][2] + self.par['origin'][2]
        return True    
    
    def compile_mpslib(self):
        print("Recompiling mpslib")    
         # Recompile from src on Colab
        import pathlib
        import mpslib as mps
        script_name='mpslib_download_and_install.sh'
        scikit_mps_path = pathlib.Path(mps.__file__).parent.absolute()
        src_path = pathlib.Path.home().joinpath(scikit_mps_path, 'bin')
        sh = 'cd %s\n./install_latest_mpslib.sh' % (src_path)
        print("===============================================================")
        print("=== Trying to download and compile MPSlib ")
        print("=== For this wo work you need")
        print("=== a) git")
        print("=== b) Make")
        print("=== c) gcc")
        print("----------------------------------------------------------------")
        
        script = pathlib.Path.home().joinpath(pathlib.Path.cwd(), script_name)
        
        print("=== Trying to write the script: (%s) " % (script))
        with open(script_name, 'w') as file:
          file.write(sh)
        print("----------------------------------------------------------------")
        print("=== Trying to run the script: (%s) " % (script))
    
        import sys
        is_colab = 'google.colab' in sys.modules
        if (is_colab):
            print("=== WE ARE ON GOOGLE COLAB ")
            print("=== please run manually -->")
            print("=== please run manually -->")
            print("")
            print("!bash mpslib_download_and_install.sh")
            print("")
            
        else:
            os.system(script)
        
        print("----------------------------------------------------------------")
        
        return True

    def which(self, program, verb=1):
        '''
        self.which: Locate executable in the following order:
            1) current directotu
            2) MPSlib installation directory
            3) In system path
        '''
        # check if executable is found in the current folder
        if is_exe(program):
            return program
        else:
            # Check of executable is located in MPLSIB folder
            program_path_mpslib = os.path.abspath(os.path.join(self.mpslib_exe_folder, program))
            if is_exe(program_path_mpslib):
                return program_path_mpslib
            else:
                # Check of executable is located in system path
                for path in os.environ["PATH"].split(os.pathsep):
                    path = path.strip('"')
                    exe_file = os.path.join(path, program)
                    if is_exe(exe_file):
                        return exe_file
                if verb>0:
                    print("################################################################")
                    print("#")
                    print("# mpslib: " + program + " not found !!!!")
                    print("# PLEASE ADD THE MPSLIB PROGRAM TO THE SYSTEM PATH")
                    print("# OR ADD THE LOCATION OF THE MPSLIB PROGRAMS TO THE SYSTEM PATH")
                    print("#")
                    print("#################################################################")

                return None

    # % Check parameter file setting using  GENESIM
    def parfile_check_genesim(self):

        self.par.setdefault('n_cond', 25)
        self.par.setdefault('n_max_ite', 10000)
        self.par.setdefault('n_max_cpdf_count', 10)
        self.par.setdefault('distance_measure', 1)
        self.par.setdefault('distance_max', 0)
        self.par.setdefault('distance_pow', 0)
        self.par.setdefault('max_search_radius', 1000000)
        self.par.setdefault('max_search_radius_soft', 1000000)
        self.par.setdefault('colocate_dimension',0)

    # % Check parameter file setting using  SNESIM
    def parfile_check_snesim(self):

        self.par.setdefault('template_size', np.array([5, 5, 1]))
        self.par.setdefault('n_multiple_grids', 3)
        self.par.setdefault('n_min_node_count', 0)
        self.par.setdefault('n_cond', -1)

    # Change simulation method        
    def change_method(self, method='mps_genesim'):
        print(self.method)
        if method == 'mps_genesim':
            self.parfile_check_genesim()
            self.method = method
        if method[0:10] == 'mps_snesim':
            self.parfile_check_snesim()
            self.method = method

    def par_write(self):
        if self.method == 'mps_genesim':
            self.mps_genesim_par_write()
        elif self.method[0:10] == 'mps_snesim':
            self.mps_snesim_par_write()
        else:
            s = 'unknown method type: {}'.format(self.method)
            raise Exception(s)

    def mps_genesim_par_write(self):
        full_path = os.path.join(self.parameter_filename)

        if (self.verbose_level > 0):
            print('mpslib: Writing GENESIM type parameter file: ' + full_path);

        file = open(full_path, 'w')

        file.write('Number of realizations # %d\n' % self.par['n_real'])
        file.write('Random Seed (0 `random` seed) # %d \n' % self.par['rseed'])
        file.write('Maximum number of counts for condtitional pdf # %d\n' % self.par['n_max_cpdf_count'])
        file.write('Max number of conditional point: Nhard, Nsoft# %d %d\n' % (self.par['n_cond'],self.par['n_cond_soft']))
        file.write('Max number of iterations # %d\n' % self.par['n_max_ite'])
        file.write("Distance measure [1:disc, 2:cont], minimum distance, power # %d %3.1f %3.1f\n" % (
        self.par['distance_measure'], self.par['distance_max'], self.par['distance_pow']))
        file.write('Colocate Dimension # %d \n' % self.par['colocate_dimension'])
        file.write("Max Search Radius for conditional data [hard,soft] # %f %f\n" % (self.par['max_search_radius'], self.par['max_search_radius_soft']))
        file.write('Simulation grid size X # %d\n' % self.par['simulation_grid_size'][0])
        file.write('Simulation grid size Y # %d\n' % self.par['simulation_grid_size'][1])
        file.write('Simulation grid size Z # %d\n' % self.par['simulation_grid_size'][2])
        file.write('Simulation grid world/origin X # %g\n' % self.par['origin'][0])
        file.write('Simulation grid world/origin Y # %g\n' % self.par['origin'][1])
        file.write('Simulation grid world/origin Z # %g\n' % self.par['origin'][2])
        file.write('Simulation grid grid cell size X # %g\n' % self.par['grid_cell_size'][0])
        file.write('Simulation grid grid cell size Y # %g\n' % self.par['grid_cell_size'][1])
        file.write('Simulation grid grid cell size Z # %g\n' % self.par['grid_cell_size'][2])
        file.write('Training image file (spaces not allowed) # %s\n' % self.par['ti_fnam'])
        file.write('Output folder (spaces in name not allowed) # %s\n' % self.par['out_folder'])
        file.write(
            'Shuffle Simulation Grid path (0: sequential, 1: random, 2: preferential, EF) # %d %d\n' % 
            (self.par['shuffle_simulation_grid'],  self.par['entropyfactor_simulation_grid']))
        file.write('Shuffle Training Image path (1 : random, 0 : sequential) # %d\n' % self.par['shuffle_ti_grid'])
        file.write('HardData filename  (same size as the simulation grid)# %s\n' % self.par['hard_data_fnam'])
        file.write('HardData seach radius (world units) # %g\n' % self.par['hard_data_search_radius'])
        file.write('Softdata categories (separated by ;) # ')
        for c, ii in enumerate(self.par['soft_data_categories']):
            if c == 0:
                file.write('%d' % ii)
            else:
                file.write(';%d' % ii)
        file.write('\n')
        file.write('Soft datafilenames (separated by ; only need (number_categories - 1) grids) # %s\n' %
                   self.par['soft_data_fnam'])
        file.write('Number of threads (not currently used) # %d\n' % self.par['n_threads'])
        file.write(
            'Debug mode(2: write to file, 1: show preview, 0: show counters, -1: no ) # %d\n' % self.par['debug_level'])
        file.write('Mask grid filename (same size as the simulation grid)# %s\n' % self.par['mask_fnam'])
        file.write('do Entropy # %s\n' % self.par['do_entropy'])
        file.write('do Estimation# %s\n' % self.par['do_estimation'])

        file.close()

    def mps_snesim_par_write(self):
        cwd = os.getcwd();
        full_path = os.path.join(self.parameter_filename)

        if (self.verbose_level > 0):
            print('mpslib: writing SNESIM type parameter file: ' + full_path);

        file = open(full_path, 'w')

        file.write('Number of realizations # %d\n' % self.par['n_real'])
        file.write('Random Seed (0 `random` seed) # %d \n' % self.par['rseed'])
        file.write('Number of mulitple grids (start from 0) # %d\n' % self.par['n_multiple_grids'])
        file.write('Min Node count (0 if not set any limit)# %d\n' % self.par['n_min_node_count'])
        file.write('Maximum number condtitional data (0: all) # %d\n' % self.par['n_cond'])
        if (self.par['template_size'].ndim==2):
            file.write('Search template size X # %d %d\n' % (self.par['template_size'][0, 0], self.par['template_size'][0, 1]))
            file.write('Search template size Y # %d %d\n' % (self.par['template_size'][1, 0], self.par['template_size'][1, 1]))
            file.write('Search template size Z # %d %d\n' % (self.par['template_size'][2, 0], self.par['template_size'][2, 1]))
        else:
            file.write('Search template size X # %d %d\n' % (self.par['template_size'][0], self.par['template_size'][0]))
            file.write('Search template size Y # %d %d\n' % (self.par['template_size'][1], self.par['template_size'][1]))
            file.write('Search template size Z # %d %d\n' % (self.par['template_size'][2], self.par['template_size'][2]))
            #file.write('Search template size X # %d\n' % self.par['template_size'][0])
            #file.write('Search template size Y # %d\n' % self.par['template_size'][1])
            #file.write('Search template size Z # %d\n' % self.par['template_size'][2])

        file.write('Simulation grid size X # %d\n' % self.par['simulation_grid_size'][0])
        file.write('Simulation grid size Y # %d\n' % self.par['simulation_grid_size'][1])
        file.write('Simulation grid size Z # %d\n' % self.par['simulation_grid_size'][2])
        file.write('Simulation grid world/origin X # %g\n' % self.par['origin'][0])
        file.write('Simulation grid world/origin Y # %g\n' % self.par['origin'][1])
        file.write('Simulation grid world/origin Z # %g\n' % self.par['origin'][2])
        file.write('Simulation grid grid cell size X # %g\n' % self.par['grid_cell_size'][0])
        file.write('Simulation grid grid cell size Y # %g\n' % self.par['grid_cell_size'][1])
        file.write('Simulation grid grid cell size Z # %g\n' % self.par['grid_cell_size'][2])
        file.write('Training image file (spaces not allowed) # %s\n' % self.par['ti_fnam'])
        file.write('Output folder (spaces in name not allowed) # %s\n' % self.par['out_folder'])
        file.write(
            'Shuffle Simulation Grid path (0: sequential, 1: random, 2: preferential, EF) # %d %d\n' % 
            (self.par['shuffle_simulation_grid'],  self.par['entropyfactor_simulation_grid']))
        file.write('Shuffle Training Image path (1 : random, 0 : sequential) # %d\n' % self.par['shuffle_ti_grid'])
        file.write('HardData filename  (same size as the simulation grid)# %s\n' % self.par['hard_data_fnam'])
        file.write('HardData seach radius (world units) # %g\n' % self.par['hard_data_search_radius'])
        file.write('Softdata categories (separated by ;) # ')
        for c, ii in enumerate(self.par['soft_data_categories']):
            if c == 0:
                file.write('%d' % ii)
            else:
                file.write(';%d' % ii)
        file.write('\n')
        file.write('Soft datafilenames (separated by ; only need (number_categories - 1) grids) # %s\n' %
                   self.par['soft_data_fnam'])
        file.write('Number of threads (not currently used) # %d\n' % self.par['n_threads'])
        file.write(
            'Debug mode(2: write to file, 1: show preview, 0: show counters, -1: no ) # %d\n' % self.par['debug_level'])
        file.write('Mask grid filename (same size as the simulation grid)# %s\n' % self.par['mask_fnam'])
        file.write('do Entropy # %s\n' % self.par['do_entropy'])
        file.write('do Estimation# %s\n' % self.par['do_estimation'])
        file.close()

    def run_parallel(self):
        '''RUN simulation in parallel
        '''
        import os
        import copy
        from multiprocessing import Pool
        from multiprocessing import freeze_support
        from multiprocessing import cpu_count
        import time

        Ncpu_total = int(cpu_count())
        try:
            import psutil
            Ncpu = psutil.cpu_count(logical=False) or Ncpu_total
        except ImportError:
            Ncpu = int(np.ceil(Ncpu_total * 0.8))


        # make sure hard data, soft data and mask data are given as variables
        # and not only filenams (such that these are written to the thread folders)
        
        # make sure TI is set        
        if (hasattr(self, 'ti') == 0):
            if os.path.isfile(self.par['ti_fnam']):
                E=eas.read(self.par['ti_fnam'])
                self.ti=E['Dmat']
        # make sure mask is set        
        if (hasattr(self, 'd_mask') == 0):
            if os.path.isfile(self.par['mask_fnam']):
                E=eas.read(self.par['mask_fnam'])
                self.d_mask=E['Dmat']
        # make sure hard data is set   
        if (hasattr(self, 'd_hard') == 0):
            if os.path.isfile(self.par['hard_data_fnam']):
                E=eas.read(self.par['hard_data_fnam'])
                self.d_hard=E['D']
        # make sure hard data is set        
        if (hasattr(self, 'd_soft') == 0):
            if os.path.isfile(self.par['soft_data_fnam']):
                E=eas.read(self.par['soft_data_fnam'])
                self.d_soft=E['D']


        # Set number of threads to use (never more than n_real)
        if (self.par['n_threads']<1):
            # Auto mode: apply 80% cap
            Nthreads = min(Ncpu, self.par['n_real'])
        else:
            # Explicit mode: respect user's request, no 80% cap
            Nthreads = min(int(self.par['n_threads']), self.par['n_real'])

        n_real = self.par['n_real']
        # Distribute realizations as evenly as possible across threads.
        # Some threads get floor(n_real/Nthreads), others get floor+1.
        real_base = n_real // Nthreads
        n_extra = n_real % Nthreads  # first n_extra threads get one extra realization
        # Reals per thread: list of length Nthreads
        reals_per_thread = [real_base + (1 if i < n_extra else 0) for i in range(Nthreads)]

        if self.verbose_level>0:
            print('parallel: using %d threads to simulate %d realizations' % (Nthreads, n_real))
            print('parallel: with %d-%d realizations per thread' % (real_base, real_base + (1 if n_extra else 0)))


        #%% Setup structure to be parsed to parallel
        Oall=[]

        for ithread in range(Nthreads):
            OO=copy.deepcopy(self)
            OO.parameter_filename = '%s_%03d.txt' % (self.method,ithread)
            OO.par['rseed']=self.par['rseed']+ithread
            OO.par['ti_fnam'] = 'ti_thread_%03d.dat' % ithread
            OO.par['n_real'] = reals_per_thread[ithread]

            OO.par['out_folder']='./thread%03d' % ithread
            if not (os.path.isdir(OO.par['out_folder'])):
                os.mkdir(OO.par['out_folder'])
            Ocur=[]
            Ocur.append(OO)
            Ocur.append('%03d' % ithread)
            Oall.append(Ocur)
            
        # Wait some time to make sure all files have been written!!
        #time.sleep(5)

        Ncpu_used = len(Oall)

        # Perform simulation in parallal
        t_start = time.time()
        if self.verbose_level>-1:
            Ncpu_max = Ncpu if self.par['n_threads'] < 1 else Ncpu_total
            print('parallel: Using %d of max %d threads (%d logical processors)' % (Ncpu_used, Ncpu_max, Ncpu_total))
            #print('__name__ = %s' % __name__)
        freeze_support()
        p = Pool(Ncpu_used)
        Omul = p.map(mpslib.run_unpack, Oall)

        t_end = time.time()
        self.time = t_end-t_start
        
        # Collect some data
        if self.verbose_level>0:
            print('parallel: job done. Collecting data from threads')
        self.x=Omul[0].x
        self.y=Omul[0].y
        self.z=Omul[0].z
        
        if self.par['do_entropy']==1:
            self.SI = np.array(())
        
        for ithread in range(len(Omul)):
            if self.par['do_entropy']==1:
                self.SI = np.append(self.SI,Omul[ithread].SI)

            if (ithread==0):
                self.sim = Omul[ithread].sim
            else:
                if Omul[ithread].sim is not None:
                    # only us sim data if the exist
                    self.sim = self.sim + Omul[ithread].sim
                else:
                    if self.verbose_level > 0:
                        print('parallel: could not use data from thread %d' % ithread)

        if self.par['do_entropy']==1:
            self.H = np.mean(self.SI)

                    
        if self.verbose_level>0:
            print('parallel: collected %d realizations' % (len(self.sim)))

        return Omul


    def run_unpack(args):
        '''Run simulation by unpacking input args
        '''
        Omul, thread = args
        #print('Thread:%s, nr=%d' % (thread,Omul.par['n_real']) ) 
        Omul.run(thread=thread)
        return Omul


    def _run_native(self, silent=False):
        """
        Run simulation using direct C++ bindings (in-process, no subprocess)

        :param silent: boolean, determines if outputs should be written to screen
        :return: returns boolean success if the simulation has been completed
        """
        if not HAS_NATIVE_BINDINGS:
            raise Exception("Native bindings not available. Install with: pip install -e .")

        import time

        # Write TI file if we have it in memory (needed before initializing algorithm)
        if hasattr(self, 'ti') and self.ti.size > 0:
            eas.write_mat(self.ti, self.par['ti_fnam'])
            ti_data = self.ti.astype(np.float32)
        else:
            if not os.path.isfile(self.par['ti_fnam']):
                if self.verbose_level > -1:
                    print('mpslib: Training image "%s" not found - USING DEFAULT!' % (self.par['ti_fnam']))
                self.ti = trainingimages.strebelle(di=2)[0]
                eas.write_mat(self.ti, self.par['ti_fnam'])
                ti_data = self.ti.astype(np.float32)
            else:
                # Read TI from file
                TI_OUT = eas.read(self.par['ti_fnam'])
                ti_data = TI_OUT['Dmat'].astype(np.float32)

        # Write hard/soft/mask data if set (needed before initializing algorithm)
        if hasattr(self, 'd_soft'):
            eas.write(self.d_soft, self.par['soft_data_fnam'])
        if hasattr(self, 'd_hard'):
            eas.write(self.d_hard, self.par['hard_data_fnam'])
        if hasattr(self, 'd_mask'):
            eas.write_mat(self.d_mask, self.par['mask_fnam'])

        # Write parameter file
        self.par_write()

        # Instantiate the appropriate algorithm
        if self.method == 'mps_genesim':
            self._native_algo = _mpslib_native.ENESIM_GENERAL(self.parameter_filename)
        elif self.method == 'mps_snesim_tree':
            self._native_algo = _mpslib_native.SNESIMTree(self.parameter_filename)
        elif self.method == 'mps_snesim_list':
            self._native_algo = _mpslib_native.SNESIMList(self.parameter_filename)
        else:
            raise Exception(f"Unknown method for native bindings: {self.method}")

        if self.verbose_level > 0:
            print(f"mpslib: Running {self.method} with native C++ bindings")

        # Run simulation
        t_start = time.time()
        try:
            self._native_algo.startSimulation()
            success = True
        except Exception as e:
            print(f"Native simulation failed: {e}")
            success = False
            return success

        t_end = time.time()
        self.time = t_end - t_start

        if self.verbose_level > 0:
            print(f"mpslib: Native simulation completed in {self.time:.2f}s")

        # Retrieve results from C++ - currently still reading from files
        # TODO: Direct memory access for better performance
        self.sim = []
        for i in range(0, self.par['n_real']):
            filename = '%s_sg_%d.gslib' % (self.par['ti_fnam'], i)
            time.sleep(.1)
            filename_with_path = os.path.join(self.par['out_folder'], filename)
            try:
                OUT = eas.read(filename_with_path)
                if self.verbose_level > 0:
                    print('mpslib: Reading: %s' % (filename))
                self.sim.append(OUT['Dmat'])
            except:
                print('Could not read gslib output file: %s' % filename)
                success = False

        # Clean up GSLIB files if requested
        if self.remove_gslib_after_simulation == 1:
            for i in range(0, self.par['n_real']):
                filename = '%s_sg_%d.gslib' % (self.par['ti_fnam'], i)
                filename_with_path = os.path.join(self.par['out_folder'], filename)
                if os.path.exists(filename_with_path):
                    os.remove(filename_with_path)
                    if self.verbose_level > 1:
                        print('mpslib: Removed: %s' % filename)

        return success

    def run(self, normal_msg='Elapsed time (sec)', silent=False, thread=''):
        """
            *Description:*\n
            This function runs the mpslib executable from python.

            :param normal_msg: last line write to screen upon  successful completion
            :param silent: boolean, determines if modle outputs should be written to the screen

            :return: returns boolean success if the model run has been completed
            """
        import os
        import time

        # Use native bindings if enabled
        if self.use_native:
            return self._run_native(silent=silent)

        # Subprocess mode (original implementation)
        success = False

        # update self.x, self.y, self.z
        if (hasattr(self, 'x') == 0):
            self.x = np.arange(self.par['simulation_grid_size'][0]) * self.par['grid_cell_size'][0] + self.par['origin'][0]
        if (hasattr(self, 'y') == 0):
            self.y = np.arange(self.par['simulation_grid_size'][1]) * self.par['grid_cell_size'][1] + self.par['origin'][1]
        if (hasattr(self, 'z') == 0):
            self.z = np.arange(self.par['simulation_grid_size'][2]) * self.par['grid_cell_size'][2] + self.par['origin'][2]



        # check if TI is set, if not, get the one
        if (not os.path.isfile(self.par['ti_fnam'])) and (not hasattr(self, 'ti')):
            if self.verbose_level>-1:
                print('mpslib: Training image "%s" not found - USING DEFAULT!' % (self.par['ti_fnam']))
            self.ti = trainingimages.strebelle(di=2)[0]

        # write training image if set
        if hasattr(self, 'ti'):
            if self.ti.shape[0] > 0:
                # self.par['ti_fnam']='TrainingImage.dat'
                eas.write_mat(self.ti, self.par['ti_fnam'])

        # write soft data if set
        if hasattr(self, 'd_soft'):
            #self.delete_soft_data()
            eas.write(self.d_soft, self.par['soft_data_fnam'])

        # write hard data if set
        if hasattr(self, 'd_hard'):
            #self.delete_hard_data()
            eas.write(self.d_hard, self.par['hard_data_fnam'])

        # write mask if set
        if hasattr(self, 'd_mask'):
            eas.write_mat(self.d_mask, self.par['mask_fnam'])


        # write parameter file
        self.par_write()
        
        if not self.iswin:
            # Flushing may be necessary in linux, to make sure fiels are written before simulation starts
            try:
                subprocess.run(["sync"])
            except:
                print('Could not run sync!')
            

        exe_file = self.method
        if self.iswin:
            exe_file = exe_file + '.exe'

        exe_path = self.which(exe_file)

        if (self.verbose_level > 0):
            print("mpslib: trying to run '%s' using '%s'\n" % (exe_path,self.parameter_filename))

        if exe_path is None:
            s = 'mpslib: The program {} does not exist or is not executable.'.format(exe_file)
            raise Exception(s)
            return -1
        else:
            if (self.verbose_level > 0):
                s = 'mpslib: Using the following executable to run the model: {}'.format(exe_path)
                print(s)


        if not os.path.isfile(os.path.join(self.parameter_filename)):
            s = 'The the mpslib input file does not exists: {}'.format(self.parameter_filename)
            raise Exception(s)

        if (self.verbose_level > 0):
            print("mpslib: trying to run  " + exe_path + " " + self.parameter_filename)


        # Next line may be needed when using parallel simulation
        if len(thread)>0:
            time.sleep(1)    

        t_start = time.time()
        if self.iswin:
            CREATE_NO_WINDOW = 0x08000000
            # stdout = subprocess.run([cmd,self.parameter_filename], stdout=subprocess.PIPE, creationflags=CREATE_NO_WINDOW)
            proc = subprocess.Popen([exe_path, self.parameter_filename], stdout=subprocess.PIPE,
                                    creationflags=CREATE_NO_WINDOW)
        else:
            proc = subprocess.Popen([exe_path, self.parameter_filename], stdout=subprocess.PIPE)

        while success == False:
            line = proc.stdout.readline()
            c = line.decode('utf-8', errors='ignore')
            if c != '':
                if normal_msg.lower() in c.lower():
                    success = True
                c = c.rstrip('\r\n')
                if not silent:
                    print('{}'.format(c))
            else:
                break
            
        t_end = time.time()
        self.time = t_end-t_start
        if (self.verbose_level > 0):
            print("mpslib: '%s' ran in  %6.2fs " % (exe_file,self.time))
            
        # read in simulated data
        self.sim = []
        for i in range(0, self.par['n_real']):
            filename = '%s_sg_%d.gslib' % (self.par['ti_fnam'], i)
            time.sleep(.1) # SOMETIMES NEEEDED WHEN FILES IS NOT YET ACCESSIBLE
            filename_with_path = os.path.join(self.par['out_folder'], filename)
            try:
                OUT = eas.read(filename_with_path)
                if (self.verbose_level > 0):
                    print('mpslib: Reading: %s' % (filename))
                self.sim.append(OUT['Dmat'])
                success = True
            except:
                if self.verbose_level > 0:
                    print('%s:Could not read gslib output file: %s' % (thread,filename))
                success = False

        # read entropy information
        if (self.par['do_entropy']):
            filename = '%s_selfInf.dat' % (self.par['ti_fnam'])
            time.sleep(.1) # SOMETIMES NEEEDED WHEN FILES IS NOT YET ACCESSIBLE
            filename_with_path = os.path.join(self.par['out_folder'], filename)
            try:
                SI = np.loadtxt(filename_with_path)
                self.SI=SI
                self.H=np.mean(self.SI)
                self.Hstd=np.std(self.SI)
                success = True
            except:
                if self.verbose_level > 0:
                    print('%s:Could not read selfinformation from: %s' % (thread,filename))
                success = False


        # combine gslib output files
        if (self.gslib_combine):
            import os
            n = 0;
            header = []
            try:
                for i in range(self.par['n_real']):
                    cur_file = '%s_sg_%d.gslib' % (self.par['ti_fnam'], i)
                    cur_file = os.path.join(self.par['out_folder'], cur_file)
                    if os.path.isfile(cur_file):
                        if (self.verbose_level > 1):
                            print('mpslib: Merging %s' % cur_file)
                        d_cur = eas.read(cur_file)
                        if n == 0:
                            n_data = len(d_cur['D'])
                            Dall = np.zeros((n_data, self.par['n_real']))
                        header.append('Real #%d' % (i + 1))
                        Dall[:, i] = d_cur['D']
                        n = n + 1
                Dall = Dall[:, range(n)]
                filename_out = '%s.gslib' % (self.par['ti_fnam'])
                title = 'Realizations from %s - %s' % (self.method, d_cur['title'])
                eas.write(Dall, filename_out, title=title, header=header)
            except:
                if self.verbose_level > 0:
                    print('%s:Could not read/combine gslib output files - perhaps empty output?' % (thread))

        # Load conditional Entropy
        if self.par['do_entropy']==1:
            self.load_conditional_entropy()

        # Load local estimation
        if self.par['do_estimation']==1:
            self.load_estimation()

        # remove gslib output files
        if (self.remove_gslib_after_simulation):
            self.delete_gslib()


        return success

    def blank_sim(self):
        if hasattr(self, 'sim') is False:
            s = 'Simulation results not imported'
            raise Exception(s)

        if self.blank_grid is None:
            s = 'No blanking grid defined'
            raise Exception(s)

        nsim = len(self.sim)
        sim_grid_size = np.shape(self.sim[0])
        blank_grid_size = np.shape(self.blank_grid)

        if sim_grid_size != blank_grid_size:
            s = "Blank grid with size {} incompatiable with sim. grid size {} ".format(sim_grid_size, blank_grid_size)
            raise Exception(s)

        blk = self.blank_grid == 0

        self.simblk = np.copy(self.sim)
        for ii in np.arange(nsim):
            self.simblk[ii][blk == True] = self.blank_val

    # Loads existing simulation results into class without running mps algorithm
    def load_sim(self):
        # Check if simulation results are already imported
        if self.sim is not None:
            s = 'Simulation results already imported'
            raise Exception(s)

        self.sim = []
        for i in range(0, self.par['n_real']):
            filename = '%s_sg_%d.gslib' % (self.par['ti_fnam'], i)

            if os.path.isfile(filename) is False:
                s = '{} file not found'.format(filename)

            OUT = eas.read(filename)

            if (self.verbose_level > 0):
                print('mpslib: Reading: %s' % (filename))
            self.sim.append(OUT['Dmat'])

    # Loads entropy
    def load_conditional_entropy(self):
        # Check if entropy results are already imported
        if hasattr(self, 'Hcond'):
            if self.verbose_level>0:
                print('Entropy results already imported - overwriting')
            
        if (self.par['do_entropy']==1):
            filename = '%s_ent_0.gslib' % (self.par['ti_fnam'])
            if os.path.isfile(filename) is False:
                s = '{} file not found'.format(filename)
            else:
                if self.verbose_level >= 0:
                    print('loading entropy from %s' % (filename))
                OUT = eas.read(filename)
                self.Hcond = OUT['Dmat']
        else:
            if self.verbose_level >= 0:
                print('Cannot load entropy results, as entropy is not performed')
            
            
    def load_estimation(self):
        #if hasattr(self, 'est'):
        #    s = 'Estimationresults already imported'
        #    raise Exception(s)
        if (self.par['do_estimation']==1):
            NC=len(self.par['soft_data_categories'])
            self.est=[]
            for i in range(NC):
                filename = '%s_cg_%d.gslib' % (self.par['ti_fnam'],i)
                if os.path.isfile(filename) is False:
                    if self.verbose_level >= 0:
                        print('%s: file not found' % (filename))
                else:
                    if self.verbose_level >= 0:
                        print('loading estimation from %s' % (filename))
                    OUT = eas.read(filename)
                    self.est.append(OUT['Dmat'])
        else:
            if self.verbose_level >= 0:
                print('Cannot load estimation results, as estimation is not performed')

    # delete gslib files
    def delete_gslib(self, remove_all_gslib=0):
        '''Removes GSLIB output files from folder

        :param remove_all_gslib: (def=0) removes aonly GSLIB files related to the cirrent run
                                 (1) removed ALL GSLIB files.
        :return:
        '''

        import os
        import glob

        if (remove_all_gslib) == 1:
            file_list = glob.glob('*.gslib')
        else:
            file_list = glob.glob('%s/%s*.gslib' % (self.par['out_folder'], self.par['ti_fnam']))
        for file in file_list:
            #file_with_path = os.path.join(self.par['out_folder'], file)
            #os.remove(os.path.join(self.par['out_folder'], file_with_path))
            os.remove(file)
            if (self.verbose_level > 1):
                print('Removing {0}'.format(os.path.join(self.par['out_folder'], file)))

            # Delete hard data

    def delete_hard_data(self):
        import os
        try:
            if (os.path.isfile(self.par['hard_data_fnam'])):
                os.remove(self.par['hard_data_fnam'])
        except: 
            print('Could not delete %s' % self.par['hard_data_fnam'])

    # Delete soft data
    def delete_soft_data(self):
        import os
        try:
            if (os.path.isfile(self.par['soft_data_fnam'])):
                os.remove(self.par['soft_data_fnam'])
        except:
            print('Could not delete %s' % self.par['soft_data_fnam'])

    # Delete mask data
    def delete_mask_data(self):
        import os
        try:
            if (os.path.isfile(self.par['mask_fnam'])):
                os.remove(self.par['mask_fnam'])
        except:
            print('Could not delete %s' % self.par['mask_fnam'])


    # Delete locard filense
    def delete_local_files(self):
        self.delete_mask_data()
        self.delete_soft_data()
        self.delete_hard_data()
        self.delete_gslib()



    # Select random set of hard data
    def seq_gibbs_set_hard_data(self, step=0.1):
        '''
        Set hard data fro sequential GIbbs resimulation
        Currenyly only works in 2D,
        :param step: Percantage of parameters to resimulate
        :return: d_hard
        '''
        if (hasattr(self, 'x') == 0):
            self.x = np.arange(self.par['simulation_grid_size'][0]) * self.par['grid_cell_size'][0] + self.par['origin'][0]
        if (hasattr(self, 'y') == 0):
            self.y = np.arange(self.par['simulation_grid_size'][1]) * self.par['grid_cell_size'][1] + self.par['origin'][1]
        if (hasattr(self, 'z') == 0):
            self.z = np.arange(self.par['simulation_grid_size'][2]) * self.par['grid_cell_size'][2] + self.par['origin'][2]

        if (hasattr(self, 'sim') == 0):
            d_hard = np.arange(0)
            return d_hard

        D = self.sim[0]
        D = D.ravel()

        if (hasattr(self, 'xx') == 0):
            self.yy, self.xx = np.meshgrid(self.y, self.x, sparse=False, indexing='ij')
            self.xx = self.xx.ravel()
            self.yy = self.yy.ravel()

        N = self.xx.size

        N_hard = np.int16(np.ceil((1 - step) * N))

        i_hard = np.random.choice(N, N_hard)

        d_hard = np.zeros((N_hard, 4))
        for i in np.arange(i_hard.size):
            d_hard[i, 0] = self.xx[i_hard[i]]
            d_hard[i, 1] = self.yy[i_hard[i]]
            d_hard[i, 2] = self.z[0]
            d_hard[i, 3] = D[i_hard[i]]
            #print('i=%d, i_hard=%d' % (i, i_hard[i]))

        self.d_hard = d_hard
        return d_hard


    def set_nan(self, nanval=-9977799):
        if hasattr(self,'sim'):
            N=len(self.sim)
            for i in range(N):
                self.sim[i][self.sim[i]==nanval] = np.nan

    def hard_data_from_sim(self, i=0, nanval=-997799):
        #i_use = [self.sim[i]==nanval] 
        #np.isnan(O1.sim[0])
        iz=0
        n=0
        n_nonnan =  np.count_nonzero(~np.isnan(self.sim[i]))
        if self.verbose_level >= 0:
            print("Number of non-nan data: %d" % (n_nonnan))
        
        # MAKE sure nans are set
        self.set_nan()
        
        d_hard = np.zeros((n_nonnan,4))
        
        for ix in range(self.par['simulation_grid_size'][0]):
            for iy in range(self.par['simulation_grid_size'][1]):
                for iz in range(self.par['simulation_grid_size'][2]):
                    if (len(self.sim[i].shape)==1):
                        val = self.sim[i][ix]
                    elif (len(self.sim[i].shape)==2):
                        val = self.sim[i][ix, iy]
                    else:
                       val = self.sim[i][ix, iy, iz]

#                    d = np.array([[self.x[ix],self.y[iy],self.z[iz],val]])
                    d = np.array([self.x[ix],self.y[iy],self.z[iz],val])
                    if not np.isnan(val):
                        #d = np.array([[self.x(ix), self.y(iy), self.z(ix), self.sim(iy.ix)]])
                        d_hard[n,:]=d                        
                        n=n+1
                        
                        
        #print(n)
        return d_hard
                
    # plot realizations using pyvista 2D/3D
    def plot_reals_3d(self, nshow=9):
        plot.plot_3d_reals(self, nshow=nshow)
        
    # plot realizations using matplotlib in 2D
    def plot_reals(self, nshow=25, **kwargs):
        
        plot.plot_reals(self, nshow=nshow, **kwargs)
        
    def etype(self):
        '''
        Compute Etype
        '''
        import numpy as np
        from scipy import stats
        from numpy import squeeze
       
        # compute Etype
        emean =squeeze(np.mean(self.sim, axis=0))
        estd = squeeze(np.std(self.sim, axis=0))
        emode,dummy = squeeze(stats.mode(self.sim, axis=0))
        emode = squeeze(emode)
        
        self.etype_mean = emean
        self.etype_std = estd
        self.etype_mode = emode
        
        return emean, estd, emode
                
    
    def plot_etype(self, title='', hardcopy=0, hardcopy_filename='etype'):
        '''
        Plot Etype mean and variance from simulation
        '''
        
        import matplotlib.pyplot as plt
        import numpy as np
        import os
        from scipy import stats
        from numpy import squeeze
   
        if self.sim is not None:
        
            # compute Etype
            emean, estd, emode = self.etype()

            vmin=0
            vmax=1
            if (hasattr(self, 'ti')):    
                vmin = np.min(self.ti)
                vmax = np.max(self.ti)

            # plot the Etypes
            #plt.subplot(1,3,1)
            plot.plot(emean, origin=self.par['origin'], spacing=self.par['grid_cell_size'],title='Etype mean')
            #plt.subplot(1,3,2)
            plot.plot(estd, origin=self.par['origin'], spacing=self.par['grid_cell_size'],title='Etype std')
            #plt.subplot(1,3,3)
            plot.plot(emode, origin=self.par['origin'], spacing=self.par['grid_cell_size'],title='Etype mode')

        else:
            if self.verbose_level >= 0:
                print('No realizations to compute Etypes from')
        return 
    
    # plot TI
    def plot_ti(self):
        '''
        Plot TI
        '''
        #if not('ti' in self.par):
        if not(hasattr(self,'ti')):           
            try:
                E=eas.read(self.par['ti_fnam'])
                self.ti = E['Dmat']
            except:
                if self.verbose_level >= 0:
                    print('Could not load %s, and can then not plot the training image' % self.par['ti_fnam'])
                return -1

        if hasattr(self,'ti'):
            plot.plot(self.ti, title="Training image - %s" % (self.par['ti_fnam']), slice=1   )
        else:
            if self.verbose_level >= 0:
                print('Could not plot TI')
    
    def plot_simulation_grid(self):
        '''
        plot simulation grid
        '''
        import numpy as np
        if self.sim is None:
            D=np.zeros(self.par['simulation_grid_size'])
        else:
            D=self.sim[0]*0
        #D=np.squeeze(D)
        plot.plot(D,  origin=self.par['origin'], 
                  spacing=self.par['grid_cell_size'],
                  title='Simulation grid', 
                  grid_minor=True,
                  show_edges=True,
                  add_points=True,
                  opacity=0.1)

    def plot_hard(self, **kwargs):
        
        import matplotlib.pyplot as plt
        import numpy as np
        import pyvista as pv
        
        self.update_xyz()

        cmap = kwargs.get('cmap',"viridis")
    
        vmin=0
        vmax=1
        if (hasattr(self, 'ti')):    
            vmin = np.nanmin(self.ti)
            vmax = np.nanmax(self.ti)
        
        if hasattr(self,'d_hard'):
            nhard=self.d_hard.shape[0]
            if self.par['simulation_grid_size'][2]==1:
                # 2D
                if nhard<100:
                    s=10
                else:   
                    s=1
                plt.scatter(self.d_hard[:,0],self.d_hard[:,1], c=self.d_hard[:,3], s=s, vmin=vmin, vmax=vmax , cmap=cmap)
                plt.axis('image')
                plt.xlim([self.x[0],self.x[-1]])
                plt.ylim([self.y[0],self.y[-1]])
                plt.colorbar()
                plt.title('Hard data')
                plt.show()
            else: 
                # 3D
                mesh_hard=pv.PolyData(self.d_hard[:,0:3])
                mesh_hard["Pv"]=self.d_hard[:,3]
                    
                pl = pv.Plotter()
                pl.add_mesh(mesh_hard, point_size=5, render_points_as_spheres=True, style='points', cmap=cmap, clim=[vmin, vmax])
                pl.show_axes()
                pl.show_grid()
                pl.add_txt('Hard data')
                pl.show()


    def plot_soft(self, **kwargs):
        
        import matplotlib.pyplot as plt
        import numpy as np
        import pyvista as pv

        self.update_xyz()    

        cmap = kwargs.get('cmap',"viridis")
    
        vmin=0
        vmax=1
        if (hasattr(self, 'ti')):    
            vmin = np.min(self.ti)
            vmax = np.max(self.ti)
        
        if hasattr(self,'d_soft'):
            if self.par['simulation_grid_size'][2]==1:
                # 2D
                
                n_classes = self.d_soft.shape[1]-3
                for i_class in range(n_classes):
                    plt.subplot(1,2,i_class+1)
                    plt.scatter(self.d_soft[:,0],self.d_soft[:,1], c=self.d_soft[:,3+i_class], vmin=0, vmax=1 , cmap=cmap)
                    plt.axis('image')
                    plt.xlim([self.x[0],self.x[-1]])
                    plt.ylim([self.y[0],self.y[-1]])
                    plt.colorbar()
                    plt.title('Soft probability, Class %d' % (i_class))
                    plt.show()
            else: 
                # 3D
                n_classes = self.d_soft.shape[1]-3
                pl = pv.Plotter(shape=(1,n_classes))
                for i_class in range(n_classes):
                
                    pl.subplot(0,i_class)
                    pl.add_text('P(m==%d) % ', font_size=2) 
                    
                    mesh=pv.PolyData(self.d_soft[:,0:3])
                    mesh["Pv"]=self.d_soft[:,3]
                    
                    pl.add_mesh(mesh, point_size=7, render_points_as_spheres=True, style='points', show_scalar_bar=True, cmap=cmap, clim=[0, 1])
                    #pl.add_txt('Soft probability, Class %d' % (i_class))
                    pl.add_text('Soft probability, Class %d' % (i_class))
                    pl.show_axes()
                    pl.show_grid()
                pl.show()

                
        else:
            if self.verbose_level >= 0:
                print('No soft data to plot')
                
                
    
    def plot(self):
        self.plot_simulation_grid()
        
        if hasattr(self,'ti'):
            self.plot_ti()
        
        self.plot_hard()
        
        self.plot_soft()
        
        if self.sim is not None:
            self.plot_reals()
            self.plot_etype()

            
           
                
    
         
    def xxx(self, plot=0):
        
        
        #%%
        #D = np.array(O.sim)
        #cat = np.sort(np.unique(O.ti))
        D = np.array(self.sim)
        cat = np.sort(np.unique(self.ti))
        
        ncat = len(cat)
        dim = D.shape 
        dim_xyz = dim[1:4]
        nr=dim[0]
        H = np.zeros(dim_xyz)
        P = np.zeros((ncat,dim_xyz[0],dim_xyz[1],dim_xyz[2]))
        
        #%% 1D marginal stats
        marg1D=[]
        for ir in range(nr):
            c=np.zeros(ncat)
            for icat in range(ncat):
                c[icat]=np.count_nonzero(self.sim[ir]==cat[icat])
                p = c / np.sum(c)
            marg1D.append(p)
        #%%                
        self.marg1D_sim = np.array(marg1D)                
        u, c = np.unique(self.sim[ir], return_counts = True)        
        p_ti = c / np.sum(c)        
        self.marg1D_ti = p_ti                
        
        
        if (plot):
            import matplotlib.pyplot as plt
            plt.figure(1)
            plt.clf()
            plt.hist(self.marg1D_sim)
            plt.plot(self.marg1D_ti,np.zeros(len(self.marg1D_ti)),'*', markersize=50)
            plt.xlabel('1D marginal Probability of category form simulations and ti')
            
            plt.gcf()
            plt.clf()
            for icat in range(ncat):
                plt.plot(self.marg1D_sim[:,icat], label='Cat=%d'%(cat[icat]) )
            plt.legend()                
            tmp=self.marg1D_sim
            for icat in range(ncat):
                tmp[:,icat]=self.marg1D_ti[icat]
            tmp
            plt.plot(tmp, 'k-')
            plt.xlabel('Realization number')
            plt.ylabel('Porb(cat|realization)')
            
            
        return True

        
        #%% Probability map
        #for icat in range(ncat):
            
            
        
        
        
            
            
        
        