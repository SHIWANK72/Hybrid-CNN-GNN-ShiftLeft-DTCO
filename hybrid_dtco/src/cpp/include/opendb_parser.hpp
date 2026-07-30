// Copyright (c) 2026 NVIDIA + Synopsys + Google DeepMind.
// All rights reserved.
// Licensed under the Apache License, Version 2.0.

#ifndef OPENDB_PARSER_HPP
#define OPENDB_PARSER_HPP

#include <string>
#include <vector>
#include <unordered_map>
#include <stdexcept>

namespace hybrid_dtco {
namespace eda {

/**
 * @class OpenDBParser
 * @brief C++ Interface for extracting hardware graph structures from OpenDB instances.
 */
class OpenDBParser {
public:
    OpenDBParser();
    ~OpenDBParser();

    /**
     * @brief Loads a DEF and LEF file into the OpenDB memory model.
     * @param lef_path Path to the LEF file.
     * @param def_path Path to the DEF file.
     * @throws std::runtime_error on parsing failure.
     */
    void load_design(const std::string& lef_path, const std::string& def_path);

    /**
     * @brief Extracts graph node features.
     * @return Flattened vector of node features.
     */
    std::vector<float> extract_node_features() const;

    /**
     * @brief Extracts graph edge indices for PyTorch Geometric (COO format).
     * @return Flat vector of edge indices [src1, dst1, src2, dst2, ...].
     */
    std::vector<int> extract_edge_indices() const;

private:
    // TODO: Add pointers to OpenDB database instances (e.g., odb::dbDatabase* db_)
    bool is_loaded_;
};

} // namespace eda
} // namespace hybrid_dtco

#endif // OPENDB_PARSER_HPP
