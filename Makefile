#export CXX=clang++-8 # clang seems to perform better than g++-7
#export CXX=g++-8 # clang seems to perform better than g++-7
# use next for maximum optimization to local hardware
# export CPPFLAGS+= -static -O3 -march=native -std=c++11
CPPFLAGS = -static -O3 -std=c++11 -Wl,--no-as-needed
# export CPPFLAGS+= -O3 -std=c++11

UNAME_S := $(shell uname -s)
UNAME_P := $(shell uname -p)
ifeq ($(OS),Windows_NT)
	export CPPFLAGS += -Wl,--no-as-needed
else
    #UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
		  #export CPPFLAGS += -Wl,--no-as-needed
		  export INCLUDEFLAGS += -Wl,--no-as-needed
    endif
    ifeq ($(UNAME_S),Darwin)
        #export CPPFLAGS += -static -Wl,--no-as-needed
    endif
    #UNAME_P := $(shell uname -p)
    #ifeq ($(UNAME_P),x86_64)
    #    CCFLAGS += -D AMD64
    #endif
    #ifneq ($(filter %86,$(UNAME_P)),)
    #    CCFLAGS += -D IA32
    #endif
    #ifneq ($(filter arm%,$(UNAME_P)),)
    #    CCFLAGS += -D ARM
    #endif
endif

# NAME OF LIBRARY
MPSLIB = mpslib/mpslib.a

# SHARED LIBRARY PLATFORM DETECTION
ifeq ($(UNAME_S),Linux)
    SHLIB_EXT = so
    SHLIB_FLAGS = -shared
endif
ifeq ($(UNAME_S),Darwin)
    SHLIB_EXT = dylib
    SHLIB_FLAGS = -dynamiclib
endif
ifeq ($(OS),Windows_NT)
    SHLIB_EXT = dll
    SHLIB_FLAGS = -shared
endif

MPSLIB_SHARED = mpslib/libmpslib.$(SHLIB_EXT)

# LINK LIBRARIES
LDLIBS =  -lstdc++ -lpthread

all: mps_genesim mps_snesim_list mps_snesim_tree
	@echo $(OS)
	@echo $(UNAME_S)
	@echo $(UNAME_P)

.PHONY: mpslib
mpslib:
	make -C mpslib

# Shared library target
$(MPSLIB_SHARED): mpslib
	$(CXX) -fPIC -O3 -std=c++11 $(SHLIB_FLAGS) -o $@ mpslib/*.o $(LDLIBS)

# Python bindings target
.PHONY: python_bindings
python_bindings: mpslib ENESIM_GENERAL.o SNESIMTree.o SNESIMList.o
	$(CXX) -fPIC -O3 -std=c++11 -shared \
		$(shell python3 -m pybind11 --includes) \
		-I. -Impslib \
		python_bindings/mpslib_bindings.cpp \
		mpslib/*.o ENESIM_GENERAL.o SNESIMTree.o SNESIMList.o \
		-o scikit-mps/mpslib/_mpslib_native$(shell python3 -c "import sysconfig; print(sysconfig.get_config_var('EXT_SUFFIX'))") \
		$(LDLIBS)

# Also need to compile the algorithm implementations
ENESIM_GENERAL.o: ENESIM_GENERAL.cpp
	$(CXX) -fPIC -O3 -std=c++11 -c $< -Impslib -o $@

SNESIMTree.o: SNESIMTree.cpp
	$(CXX) -fPIC -O3 -std=c++11 -c $< -Impslib -o $@

SNESIMList.o: SNESIMList.cpp
	$(CXX) -fPIC -O3 -std=c++11 -c $< -Impslib -o $@

mps_genesim: mpslib
	$(CXX) $(CPPFLAGS) $(INCLUDEFLAGS) mps_genesim.cpp ENESIM_GENERAL.cpp $(MPSLIB) -o $@ -I mpslib/ $(LDLIBS)

mps_snesim_tree: mpslib
	$(CXX) $(CPPFLAGS) $(INCLUDEFLAGS) mps_snesim_tree.cpp SNESIMTree.cpp $(MPSLIB) -o $@ -I mpslib/ $(LDLIBS)

mps_snesim_list: mpslib
	$(CXX) $(CPPFLAGS) $(INCLUDEFLAGS) mps_snesim_list.cpp SNESIMList.cpp $(MPSLIB) -o $@ -I mpslib/ $(LDLIBS)

.PHONY: clean
clean:
	rm -f *.o mps mpslib/*.o $(MPSLIB)

cleanexe:
	rm -f *.o mps *.exe mps_genesim mps_snesim_tree mps_snesim_list mpslib/*.o $(MPSLIB)

.PHONY: cleano
cleano:
	rm -f *.o mpslib/*.o $(MPSLIB)

copy:
	cp mps_genesim scikit-mps/mpslib/bin/.
	cp mps_snesim_tree scikit-mps/mpslib/bin/.
	cp mps_snesim_list scikit-mps/mpslib/bin/.
	cp mps_*.exe scikit-mps/mpslib/bin/.


    
