// Python bindings for MPSlib using pybind11
// (c) 2015-2026 MPSlib Contributors

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "ENESIM_GENERAL.h"
#include "SNESIMTree.h"
#include "SNESIMList.h"

namespace py = pybind11;

// Helper: Convert 3D C++ vector to numpy array (Z, Y, X order)
py::array_t<float> vector3d_to_numpy(
    const std::vector<std::vector<std::vector<float>>>& vec3d) {

    if (vec3d.empty() || vec3d[0].empty() || vec3d[0][0].empty()) {
        return py::array_t<float>();
    }

    size_t dimZ = vec3d.size();
    size_t dimY = vec3d[0].size();
    size_t dimX = vec3d[0][0].size();

    auto result = py::array_t<float>({dimZ, dimY, dimX});
    auto buf = result.mutable_unchecked<3>();

    for (size_t z = 0; z < dimZ; z++) {
        for (size_t y = 0; y < dimY; y++) {
            for (size_t x = 0; x < dimX; x++) {
                buf(z, y, x) = vec3d[z][y][x];
            }
        }
    }
    return result;
}

// Helper: Convert numpy array to 3D C++ vector (Z, Y, X order)
std::vector<std::vector<std::vector<float>>> numpy_to_vector3d(
    py::array_t<float> arr) {

    auto buf = arr.unchecked<3>();
    size_t dimZ = buf.shape(0);
    size_t dimY = buf.shape(1);
    size_t dimX = buf.shape(2);

    std::vector<std::vector<std::vector<float>>> result(dimZ,
        std::vector<std::vector<float>>(dimY,
            std::vector<float>(dimX)));

    for (size_t z = 0; z < dimZ; z++) {
        for (size_t y = 0; y < dimY; y++) {
            for (size_t x = 0; x < dimX; x++) {
                result[z][y][x] = buf(z, y, x);
            }
        }
    }
    return result;
}

PYBIND11_MODULE(_mpslib_native, m) {
    m.doc() = "Native C++ bindings for MPSlib - Direct in-process simulation";

    // Base class MPSAlgorithm
    py::class_<MPS::MPSAlgorithm>(m, "MPSAlgorithm")
        .def("startSimulation", &MPS::MPSAlgorithm::startSimulation,
             "Run the simulation")

        // Simulation grid access
        .def("sg", [](const MPS::MPSAlgorithm& self) {
            return vector3d_to_numpy(self.sg());
        }, "Get simulation grid as numpy array")
        .def("setSg", [](MPS::MPSAlgorithm& self, py::array_t<float> arr) {
            self.setSg(numpy_to_vector3d(arr));
        }, "Set simulation grid from numpy array")

        // Training image access
        .def("TI", [](const MPS::MPSAlgorithm& self) {
            return vector3d_to_numpy(self.TI());
        }, "Get training image as numpy array")
        .def("setTI", [](MPS::MPSAlgorithm& self, py::array_t<float> arr) {
            self.setTI(numpy_to_vector3d(arr));
        }, "Set training image from numpy array")

        // Simulation grid dimensions
        .def_property("sgDimX",
            &MPS::MPSAlgorithm::sgDimX,
            &MPS::MPSAlgorithm::setSgDimX,
            "Simulation grid dimension X")
        .def_property("sgDimY",
            &MPS::MPSAlgorithm::sgDimY,
            &MPS::MPSAlgorithm::setSgDimY,
            "Simulation grid dimension Y")
        .def_property("sgDimZ",
            &MPS::MPSAlgorithm::sgDimZ,
            &MPS::MPSAlgorithm::setSgDimZ,
            "Simulation grid dimension Z")

        // Training image dimensions
        .def_property("tiDimX",
            &MPS::MPSAlgorithm::tiDimX,
            &MPS::MPSAlgorithm::setTiDimX,
            "Training image dimension X")
        .def_property("tiDimY",
            &MPS::MPSAlgorithm::tiDimY,
            &MPS::MPSAlgorithm::setTiDimY,
            "Training image dimension Y")
        .def_property("tiDimZ",
            &MPS::MPSAlgorithm::tiDimZ,
            &MPS::MPSAlgorithm::setTiDimZ,
            "Training image dimension Z")

        // Simulation parameters
        .def_property("realizationNumbers",
            &MPS::MPSAlgorithm::realizationNumbers,
            &MPS::MPSAlgorithm::setRealizationNumbers,
            "Number of realizations to generate")
        .def_property("debugMode",
            &MPS::MPSAlgorithm::debugMode,
            &MPS::MPSAlgorithm::setDebugMode,
            "Debug mode level (-2 to 3)")
        .def_property("maxIterations",
            &MPS::MPSAlgorithm::maxIterations,
            &MPS::MPSAlgorithm::setMaxIterations,
            "Maximum iterations")
        .def_property("numberOfThreads",
            &MPS::MPSAlgorithm::numberOfThreads,
            &MPS::MPSAlgorithm::setNumberOfThreads,
            "Number of threads for parallel simulation")
        .def_property("maxNeighbours",
            &MPS::MPSAlgorithm::maxNeighbours,
            &MPS::MPSAlgorithm::setMaxNeighbours,
            "Maximum number of neighbors")

        // Path shuffling
        .def_property("shuffleSgPath",
            &MPS::MPSAlgorithm::shuffleSgPath,
            &MPS::MPSAlgorithm::setShuffleSgPath,
            "Shuffle simulation grid path (0=sequential, 1=random, 2=preferential)")
        .def_property("shuffleTiPath",
            &MPS::MPSAlgorithm::shuffleTiPath,
            &MPS::MPSAlgorithm::setShuffleTiPath,
            "Shuffle training image path")

        // File names and directories
        .def_property("outputDirectory",
            &MPS::MPSAlgorithm::outputDirectory,
            &MPS::MPSAlgorithm::setOutputDirectory,
            "Output directory for results")
        .def_property("tiFilename",
            &MPS::MPSAlgorithm::tiFilename,
            &MPS::MPSAlgorithm::setTiFilename,
            "Training image filename")
        .def_property("hardDataFileNames",
            &MPS::MPSAlgorithm::hardDataFileNames,
            &MPS::MPSAlgorithm::setHardDataFileNames,
            "Hard data filenames")

        // Display
        .def_property("showPreview",
            &MPS::MPSAlgorithm::showPreview,
            &MPS::MPSAlgorithm::setShowPreview,
            "Show preview during simulation")

        // Paths
        .def_property("simulationPath",
            &MPS::MPSAlgorithm::simulationPath,
            &MPS::MPSAlgorithm::setSimulationPath,
            "Simulation path")
        .def_property("tiPath",
            &MPS::MPSAlgorithm::tiPath,
            &MPS::MPSAlgorithm::setTiPath,
            "Training image path")
        ;

    // ENESIM_GENERAL (mps_genesim equivalent)
    py::class_<MPS::ENESIM_GENERAL, MPS::MPSAlgorithm>(m, "ENESIM_GENERAL")
        .def(py::init<const std::string&>(),
             py::arg("configFile"),
             "Create ENESIM_GENERAL from configuration file")
        .def("initialize", &MPS::ENESIM_GENERAL::initialize,
             py::arg("configFile"),
             "Initialize from configuration file")
        .def("startSimulation", &MPS::ENESIM_GENERAL::startSimulation,
             "Run the GENESIM simulation")
        ;

    // SNESIMTree (mps_snesim_tree equivalent)
    py::class_<MPS::SNESIMTree, MPS::MPSAlgorithm>(m, "SNESIMTree")
        .def(py::init<const std::string&>(),
             py::arg("configFile"),
             "Create SNESIMTree from configuration file")
        .def("initialize", &MPS::SNESIMTree::initialize,
             py::arg("configFile"),
             "Initialize from configuration file")
        .def("startSimulation", &MPS::SNESIMTree::startSimulation,
             "Run the SNESIM (tree) simulation")
        ;

    // SNESIMList (mps_snesim_list equivalent)
    py::class_<MPS::SNESIMList, MPS::MPSAlgorithm>(m, "SNESIMList")
        .def(py::init<const std::string&>(),
             py::arg("configFile"),
             "Create SNESIMList from configuration file")
        .def("initialize", &MPS::SNESIMList::initialize,
             py::arg("configFile"),
             "Initialize from configuration file")
        .def("startSimulation", &MPS::SNESIMList::startSimulation,
             "Run the SNESIM (list) simulation")
        ;
}
