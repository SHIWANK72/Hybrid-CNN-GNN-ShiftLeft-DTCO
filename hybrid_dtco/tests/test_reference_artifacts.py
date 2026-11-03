"""Protect graph identity/units and the distinction between missing and zero labels."""

import base64
import json
from pathlib import Path
import runpy

import pytest


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
assemble = runpy.run_path(str(SCRIPTS / "extract_reference_graph.py"))["assemble"]
summarize = runpy.run_path(str(SCRIPTS / "summarize_reference_run.py"))["summarize"]


def encoded(value):
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def test_graph_preserves_identifiers_and_dbu_conversion(tmp_path):
    name = 'unit/é "quoted"\tidentifier'
    records = [
        ["META", "1000", "0", "0", "20000", "10000"],
        ["NODE", "0", encoded(name), encoded("BUF"), "1250", "2500", "500", "1000", encoded("PLACED")],
        ["NET", "0", encoded("signal")],
        ["PIN", "0", "0", encoded("Y"), encoded("OUTPUT")],
        ["PORT", "0", encoded("out"), encoded("OUTPUT")],
    ]
    path = tmp_path / "graph.tsv"
    path.write_text("\n".join("\t".join(row) for row in records))
    graph = assemble(path)
    assert graph["nodes"][0]["name"] == name
    assert graph["nodes"][0]["x_um"] == 1.25
    assert graph["nodes"][0]["height_um"] == 1.0
    assert graph["core_bbox_um"] == [0.0, 0.0, 20.0, 10.0]
    assert graph["nets"][0]["pins"][0]["direction"] == "OUTPUT"
    assert graph["nets"][0]["ports"][0]["name"] == "out"
    path.write_text(path.read_text().replace("PIN\t0\t0", "PIN\t0\t5"))
    with pytest.raises(ValueError, match="missing node"):
        assemble(path)


@pytest.fixture
def scalar_run(tmp_path):
    results = tmp_path / "results/sky130hd/gcd/base"
    logs = tmp_path / "logs/sky130hd/gcd/base"
    results.mkdir(parents=True)
    logs.mkdir(parents=True)
    for name in ("3_3_place_gp.odb", "5_1_grt.odb", "6_final.odb", "6_final.def",
                 "6_final.v", "6_final.gds", "6_final.spef"):
        (results / name).write_text("unit-test placeholder; not physical-design evidence")
    (tmp_path / "early-graph.json").write_text(json.dumps({
        "feature_checkpoint": "global_placement", "nodes": [{"id": 0}],
        "nets": [{"pins": [{"node": 0}]}],
    }))
    (logs / "6_report.json").write_text(json.dumps({
        "finish__timing__setup__ws": 1.25,
        "finish__timing__setup__tns": 0,
        "finish__flow__errors__count": 0,
    }))
    (logs / "5_1_grt.log").write_text("Total 6744 1291 19.14% 0 / 0 / 0\n")
    return tmp_path, logs


def test_positive_slack_is_not_negative_slack(scalar_run):
    output, logs = scalar_run
    timing = summarize(output)["timing"]
    assert timing["worst_setup_slack"] == 1.25
    assert timing["wns"] == 0.0
    path = logs / "6_report.json"
    data = json.loads(path.read_text())
    data["finish__timing__setup__ws"] = -0.25
    data["finish__timing__setup__tns"] = -0.75
    path.write_text(json.dumps(data))
    assert summarize(output)["timing"]["wns"] == -0.25
    assert summarize(output)["timing"]["tns"] == -0.75


def test_missing_congestion_is_not_zero(scalar_run):
    output, logs = scalar_run
    assert summarize(output)["congestion"]["total_congestion"] == 0
    (logs / "5_1_grt.log").write_text("Incomplete tool output")
    with pytest.raises(ValueError, match="congestion summary is missing"):
        summarize(output)


def test_missing_physical_artifact_blocks_summary(scalar_run):
    output, _ = scalar_run
    (output / "results/sky130hd/gcd/base/6_final.spef").unlink()
    with pytest.raises(ValueError, match="artifact missing/empty"):
        summarize(output)
