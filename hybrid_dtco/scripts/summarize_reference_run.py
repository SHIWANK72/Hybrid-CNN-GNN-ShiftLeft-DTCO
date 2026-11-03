"""Validate current-run artifacts and extract explicitly staged scalar labels."""

import argparse
import json
import math
from pathlib import Path
import re


def summarize(output):
    results = output / "results/sky130hd/gcd/base"
    logs = output / "logs/sky130hd/gcd/base"
    for name in (
        "3_3_place_gp.odb",
        "5_1_grt.odb",
        "6_final.odb",
        "6_final.def",
        "6_final.v",
        "6_final.gds",
        "6_final.spef",
    ):
        path = results / name
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError(f"Required current-run artifact missing/empty: {path}")
    graph = json.loads((output / "early-graph.json").read_text())
    if graph["feature_checkpoint"] != "global_placement":
        raise ValueError("Incorrect graph information boundary")
    if not graph["nodes"] or not graph["nets"]:
        raise ValueError("Empty graph")
    final = json.loads((logs / "6_report.json").read_text())
    values = [
        final[key]
        for key in ("finish__timing__setup__ws", "finish__timing__setup__tns")
    ]
    if not all(
        isinstance(value, (int, float)) and math.isfinite(value) for value in values
    ):
        raise ValueError("Timing values must be finite numbers")
    if final["finish__flow__errors__count"] != 0:
        raise ValueError("Final flow reports errors")
    # The pinned GRT table names Resource, Demand, Usage, Max H / Max V / Total
    # Congestion. Use its last complete summary; never use routing runtime as
    # an overflow label or silently treat a missing table as zero congestion.
    pattern = (
        r"^\s*Total\s+(\d+)\s+(\d+)\s+([\d.]+)%\s+(\d+)\s*/\s*(\d+)\s*/\s*(\d+)\s*$"
    )
    rows = re.findall(pattern, (logs / "5_1_grt.log").read_text(), re.MULTILINE)
    if not rows:
        raise ValueError("Global-route congestion summary is missing")
    resource, demand, usage, max_h, max_v, total = rows[-1]
    connected = {pin["node"] for net in graph["nets"] for pin in net["pins"]}
    return {
        "schema_version": "0.1.0",
        "sample_role": "pipeline_smoke_test_not_training_evidence",
        "early_checkpoint": "3_3_place_gp.odb",
        "early_graph_instances_including_physical": len(graph["nodes"]),
        "early_graph_signal_connected_instances": len(connected),
        "early_graph_signal_nets": len(graph["nets"]),
        "timing": {
            "source": "logs/sky130hd/gcd/base/6_report.json",
            "stage": "post_route_extracted",
            "units": "ns",
            "worst_setup_slack": values[0],
            "wns": min(values[0], 0.0),
            "tns": values[1],
            "definition": "WNS is min(worst setup slack, 0); positive WS is not negative slack.",
        },
        "congestion": {
            "source": "logs/sky130hd/gcd/base/5_1_grt.log",
            "stage": "global_route",
            "resource": int(resource),
            "demand": int(demand),
            "usage_percent": float(usage),
            "max_horizontal_congestion": int(max_h),
            "max_vertical_congestion": int(max_v),
            "total_congestion": int(total),
            "spatial_labels": "not_extracted",
        },
        "limitations": [
            "One small design; no model trained or generalization measured.",
            "No independent foundry sign-off or DRC/LVS qualification.",
            "Sky130 subset/typical corner only; default power activity is not measured workload power.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    summary = summarize(args.run)
    (args.run / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
