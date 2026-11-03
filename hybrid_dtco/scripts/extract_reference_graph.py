"""Validate Tcl/OpenDB interchange and assemble an early-checkpoint graph."""

import argparse
import base64
import json
from pathlib import Path


def text(value):
    return base64.b64decode(value, validate=True).decode("utf-8")


def assemble(path):
    nodes, nets = [], []
    units, core = None, None
    for line in path.read_text().splitlines():
        fields = line.split("\t")
        kind = fields[0]
        if kind == "META":
            units = int(fields[1])
            if units <= 0:
                raise ValueError("Invalid geometry units")
            core = [int(value) / units for value in fields[2:]]
        elif kind == "NODE":
            _, identifier, name, cell, x, y, width, height, status = fields
            if int(identifier) != len(nodes) or units is None:
                raise ValueError("Invalid node order or missing units")
            nodes.append(
                {
                    "id": int(identifier),
                    "name": text(name),
                    "cell_type": text(cell),
                    "x_um": int(x) / units,
                    "y_um": int(y) / units,
                    "width_um": int(width) / units,
                    "height_um": int(height) / units,
                    "placement_status": text(status),
                }
            )
        elif kind == "NET":
            _, identifier, name = fields
            if int(identifier) != len(nets):
                raise ValueError("Invalid net order")
            nets.append({"name": text(name), "pins": [], "ports": []})
        elif kind == "PIN":
            _, net, node, pin, direction = fields
            if not 0 <= int(node) < len(nodes):
                raise ValueError("Pin refers to a missing node")
            nets[int(net)]["pins"].append(
                {"node": int(node), "pin": text(pin), "direction": text(direction)}
            )
        elif kind == "PORT":
            _, net, name, direction = fields
            nets[int(net)]["ports"].append(
                {"name": text(name), "direction": text(direction)}
            )
        else:
            raise ValueError(f"Unknown interchange record: {kind}")
    if not nodes or not nets or core is None or len(core) != 4:
        raise ValueError("Missing or empty reference graph")
    return {
        "schema_version": "0.1.0",
        "feature_checkpoint": "global_placement",
        "coordinate_units": "um",
        "db_units_per_micron": units,
        "core_bbox_um": core,
        "nodes": nodes,
        "nets": nets,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = assemble(args.input)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        f"Extracted {len(result['nodes'])} instances and {len(result['nets'])} signal nets"
    )
