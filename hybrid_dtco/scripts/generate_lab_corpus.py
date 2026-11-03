"""Generate a small, family-split laboratory corpus with the pinned EDA flow.

Uses an already-running offline container mounted as /project and /work.
All design variants keep the same split. Failed runs remain in the manifest.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time

from extract_reference_graph import assemble


FAMILIES = {"gcd": "train", "accumulator": "train", "fifo": "train",
            "fir": "validation", "alu": "test", "arbiter": "test"}
VARIANTS = [(32, 20.0), (45, 6.0), (58, 3.0)]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--container", required=True)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    root = args.output.resolve()
    root.mkdir(parents=True, exist_ok=True)
    manifest_path = root / "corpus.json"
    if manifest_path.exists() and not args.resume:
        parser.error("Corpus already exists; use --resume to reuse verified samples")
    project = Path(__file__).resolve().parents[1]
    design_paths = {family: project / ("examples/gcd/gcd.v" if family == "gcd"
                    else f"examples/lab/{family}.v") for family in FAMILIES}
    inputs = {str(p.relative_to(project)): sha(p) for p in design_paths.values()}
    for name in ("generate_lab_corpus.py", "export_reference_graph.tcl.in", "export_routing_grid.tcl.in"):
        inputs[f"scripts/{name}"] = sha(project / "scripts" / name)
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest["source_sha256"] != inputs:
            raise ValueError("Source changed; create a new corpus instead of mixing versions")
    else:
        manifest = {"schema_version": "0.1.0", "created_at": datetime.now(timezone.utc).isoformat(),
                    "source_sha256": inputs, "family_splits": FAMILIES, "samples": [],
                    "scope": "small original RTL; sky130hd typical corner; laboratory only"}
    details = json.loads(subprocess.check_output(["docker", "--host=unix:///var/run/docker.sock",
                                                "inspect", args.container]))[0]
    image = json.loads(subprocess.check_output(["docker", "--host=unix:///var/run/docker.sock",
                                               "image", "inspect", details["Image"]]))[0]
    if image["Config"].get("Labels", {}).get("org.dtco.upstream.digest") != "sha256:5849e1dde67ba70b36194cf90a172d6c0e4cb2cf5502d6e0dd7c1d251a6d4584":
        raise ValueError("Unexpected EDA toolchain")
    manifest["image_id"] = details["Image"]
    manifest["upstream_digest"] = image["Config"]["Labels"]["org.dtco.upstream.digest"]

    def save():
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")

    def execute(command, sample_dir, log_name):
        with (sample_dir / log_name).open("w") as log:
            result = subprocess.run(["docker", "--host=unix:///var/run/docker.sock", "exec",
                                     args.container, "bash", "-c", command],
                                    stdout=log, stderr=subprocess.STDOUT, timeout=600)
        if result.returncode:
            raise RuntimeError(f"{log_name}: exit {result.returncode}")

    save()
    for family, split in FAMILIES.items():
        for index, (utilization, period) in enumerate(VARIANTS):
            identifier = f"{family}-v{index}"
            previous = next((s for s in manifest["samples"] if s["id"] == identifier), None)
            if previous and previous["status"] == "passed":
                for rel, expected in previous["artifact_sha256"].items():
                    if sha(root / identifier / rel) != expected:
                        raise ValueError(f"Corrupt retained artifact: {identifier}/{rel}")
                continue
            sample_dir = root / identifier
            # Retrying a failed sample preserves old logs in its attempt directory.
            if sample_dir.exists():
                suffix = int(time.time())
                sample_dir.rename(root / f"{identifier}-failed-{suffix}")
            sample_dir.mkdir()
            inside = f"/work/{identifier}"
            rtl = "/project/" + str(design_paths[family].relative_to(project))
            (sample_dir / "constraints.sdc").write_text(
                f"current_design {family}\ncreate_clock -name core_clock -period {period} [get_ports clk]\n"
                f"set_clock_uncertainty 0.1 [get_clocks core_clock]\n"
                f"set_input_delay {period*0.1} -clock core_clock [all_inputs -no_clocks]\n"
                f"set_output_delay {period*0.1} -clock core_clock [all_outputs]\n")
            (sample_dir / "config.mk").write_text(
                f"export DESIGN_NAME = {family}\nexport PLATFORM = sky130hd\n"
                f"export VERILOG_FILES = {rtl}\nexport SDC_FILE = {inside}/constraints.sdc\n"
                f"export CORE_UTILIZATION = {utilization}\nexport PLACE_DENSITY = 0.70\n"
                "export TNS_END_PERCENT = 100\nexport SYNTH_REPEATABLE_BUILD = 1\nexport ADDER_MAP_FILE :=\n")
            sample = {"id": identifier, "family": family, "split": split, "status": "running",
                      "utilization_percent": utilization, "clock_period_ns": period}
            if previous:
                manifest["samples"].remove(previous)
            manifest["samples"].append(sample)
            save()
            print(f"Starting {identifier} ({split})", flush=True)
            started = time.monotonic()
            make = ("source /OpenROAD-flow-scripts/env.sh && make -f /OpenROAD-flow-scripts/flow/Makefile "
                    f"FLOW_HOME=/OpenROAD-flow-scripts/flow WORK_HOME={inside} DESIGN_CONFIG={inside}/config.mk NUM_CORES=2")
            try:
                execute(make + " grt", sample_dir, "eda-grt.log")
                results = f"{inside}/results/sky130hd/{family}/base"
                execute(f"DTCO_EARLY_ODB={results}/3_3_place_gp.odb DTCO_GRAPH_OUTPUT={inside}/early-graph.tsv "
                        "/OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad -exit -threads 2 /project/scripts/export_reference_graph.tcl.in",
                        sample_dir, "graph.log")
                graph = assemble(sample_dir / "early-graph.tsv")
                (sample_dir / "early-graph.json").write_text(json.dumps(graph) + "\n")
                execute(f"DTCO_ROUTED_ODB={results}/5_1_grt.odb DTCO_ROUTING_OUTPUT={inside}/routing-grid.tsv "
                        "/OpenROAD-flow-scripts/tools/install/OpenROAD/bin/openroad -exit -threads 2 /project/scripts/export_routing_grid.tcl.in",
                        sample_dir, "routing-grid.log")
                # Complete detailed routing/extraction for real post-route timing.
                execute(make + " finish", sample_dir, "eda-finish.log")
                final = json.loads((sample_dir / f"logs/sky130hd/{family}/base/6_report.json").read_text())
                ws = final["finish__timing__setup__ws"]
                spef = sample_dir / f"results/sky130hd/{family}/base/6_final.spef"
                if not spef.is_file() or not spef.stat().st_size:
                    raise ValueError("Missing extracted parasitics")
                sample["labels"] = {"post_route_worst_setup_slack_ns": ws,
                                    "post_route_tns_ns": final["finish__timing__setup__tns"],
                                    "timing_stage": "post_route_extracted",
                                    "congestion_stage": "global_route"}
                sample["status"] = "passed"
                sample["artifact_sha256"] = {str(p.relative_to(sample_dir)): sha(p)
                    for p in sorted(sample_dir.rglob("*")) if p.is_file()}
            except Exception as error:
                sample["status"] = "failed"
                sample["error"] = str(error)
                print(f"FAILED {identifier}: {error}", flush=True)
            sample["elapsed_seconds"] = time.monotonic() - started
            save()
            print(f"{identifier}: {sample['status']} ({sample['elapsed_seconds']:.1f}s)", flush=True)
    passed = sum(s["status"] == "passed" for s in manifest["samples"])
    print(f"Corpus complete: {passed}/{len(manifest['samples'])} passed; failures retained")


if __name__ == "__main__":
    main()
