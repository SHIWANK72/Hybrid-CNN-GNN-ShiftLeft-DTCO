# Copyright (c) 2026 NVIDIA + Synopsys + Google DeepMind.
# Licensed under the Apache License, Version 2.0.

cmake_minimum_required(VERSION 3.18)
project(HybridDTCO_CPP VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(pybind11 REQUIRED)
# TODO: find_package(OpenROAD REQUIRED)

include_directories(include)

pybind11_add_module(opendb_ext src/pybind_bindings.cpp src/opendb_parser.cpp)

# target_link_libraries(opendb_ext PRIVATE OpenROAD::opendb)
