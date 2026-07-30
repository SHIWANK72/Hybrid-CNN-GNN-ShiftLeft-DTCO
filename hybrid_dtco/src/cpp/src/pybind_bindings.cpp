// Copyright (c) 2026 NVIDIA + Synopsys + Google DeepMind.
// All rights reserved.
// Licensed under the Apache License, Version 2.0.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "opendb_parser.hpp"

namespace py = pybind11;

PYBIND11_MODULE(opendb_ext, m) {
    m.doc() = "C++ Python bindings for OpenDB graph extraction";

    py::class_<hybrid_dtco::eda::OpenDBParser>(m, "OpenDBParser")
        .def(py::init<>())
        .def("load_design", &hybrid_dtco::eda::OpenDBParser::load_design,
             py::arg("lef_path"), py::arg("def_path"),
             "Load LEF and DEF files into memory.")
        .def("extract_node_features", &hybrid_dtco::eda::OpenDBParser::extract_node_features,
             "Extract flattened node features for GNN.")
        .def("extract_edge_indices", &hybrid_dtco::eda::OpenDBParser::extract_edge_indices,
             "Extract edge indices in COO format.");
}
