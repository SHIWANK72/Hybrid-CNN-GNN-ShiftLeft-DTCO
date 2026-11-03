# First reference experiment: Sky130 GCD

The first engineering milestone is an original 16-bit GCD design through a
pinned OpenROAD flow, with an early graph and downstream measurement artifacts.
This establishes the data-generation path before model training.

The master’s release deadline remains **3 May 2027**.

## Verified checkpoint — 3 November 2026

`/workspace/experiments/sky130-gcd/run-002` completed the entire harness from a
fresh output directory. Its `manifest.json` records stage results and artifact
SHA-256 hashes. The first run completed physical design but failed graph
extraction because Python support was absent; its failed status is preserved.
The corrected runner uses Tcl/OpenDB and completed a second physical-design run.

| Check | Observed result |
|---|---|
| Functional RTL checks | Seven concrete bounded SAT transactions passed |
| Physical flow | Synthesis, floorplan, placement, CTS, global/detailed routing, extraction and final reports completed |
| Early graph | 646 instances, including physical instances; 517 signal-connected instances; 552 signal nets |
| Final layout artifacts | GDSII, DEF, ODB, netlist, SDC and extracted SPEF produced |
| Worst setup slack | +16.2104 ns under the declared 20 ns clock |
| WNS / TNS | 0 ns / 0 ns |
| Global-route summary | Resource 6744, demand 1291, usage 19.14%, reported total congestion 0 |
| Repository tests | Four artifact/label tests passed; existing test placeholders contain no tests |
| Spatial congestion maps / ML training | Not implemented in this checkpoint |

The two physical runs produced the same reported scalar timing/congestion
values. Timestamped files are not expected to be byte-identical. This is an
uncongested smoke test, not a useful corpus for learning risk or evaluating a
model. No separate foundry DRC/LVS qualification was performed.

## Run

From `hybrid_dtco`, using the managed Docker daemon:

```sh
bash scripts/prepare_reference_toolchain.sh
python scripts/run_reference_flow.py --output /workspace/experiments/sky130-gcd/my-run
```

Choose a new output directory for each run. The runner refuses existing paths
and paths inside the project. Keep the source checkout and output directories
on the same machine as the managed Docker daemon. A task command sandbox may
require approved access to the Docker socket.

The runner limits each container to two CPUs and 8 GiB RAM, disables container
networking, mounts source read-only, and runs under the caller’s UID/GID.
The batch is local; it does not publish a web service or environment.

## Toolchain identity and storage

Upstream image:

```text
openroad/orfs@sha256:5849e1dde67ba70b36194cf90a172d6c0e4cb2cf5502d6e0dd7c1d251a6d4584
```

The setup script exports that exact image filesystem using crane 0.20.6 and
imports it as `dtco/orfs:reference-5849e1dde67b`. Crane’s download has a pinned
SHA-256; registry content digests and TLS verification remain enabled. The
compact image avoids excessive layer duplication under Docker’s `vfs` driver.
Compaction changes the local image ID; the runner records both that ID and
the upstream source digest. The upstream working directory/default command
are set explicitly; required tools are selected by absolute path or `env.sh`.

The compressed filesystem and checksum/source sidecars are retained under
`/workspace/.tools` for reuse. Do not commit these large third-party assets.
On an ordinary machine the initial export requires GitHub release assets and
Docker Hub registry/auth/blob destinations. Container execution itself is offline.

## Design and information boundary

- Source: `examples/gcd/gcd.v`, original project RTL under Apache-2.0.
- Constraints: 20 ns clock, 0.2 ns uncertainty, 2 ns input/output delays.
- Platform: the pinned image’s `sky130hd` subset and its default typical corner.
- Early input: `3_3_place_gp.odb`, immediately after global placement.
- Later targets: global-route congestion and post-route extracted timing.

The graph extractor reads **only** the early ODB. It preserves signal-net
hyperedges with pin directions and external ports, instance geometry in
micrometres, and the core bounding box. Power/ground nets are excluded. This
initial schema is an extraction artifact; it is not yet the final training
dataset, rasterizer, graph encoder or CNN–GNN implementation.

Downstream changes to buffers or net names mean timing endpoints must not be
silently joined to early nodes by array position. Design-level timing targets
can be used first; node-level supervision needs an explicit correspondence map.

## Evidence

Each run writes `manifest.json`, stage logs, functional-check records, original
ORFS logs/reports/results, and `early-graph.json`. The manifest records source
hashes, image identity, stage exit codes, elapsed time and output hashes.
Failures remain visible; a nonzero flow exit does not become a passing sample.

Functional checks use Yosys bounded SAT for seven concrete transactions,
including zero inputs, equal inputs, and swapped operands. They check the
expected result and idle state after 24 cycles. This is useful arithmetic
coverage, not exhaustive functional equivalence or full protocol verification.

Check current-run reports for timing constraints, routing status, parasitic
source and numerical target values before admitting a sample into a dataset.
No timing closure, DRC/LVS, foundry sign-off, ML accuracy or TRL qualification
claim follows from a successful flow exit alone. A tiny uncongested GCD sample
is a pipeline smoke test and cannot establish generalization.

## Next gate

Validate stage-specific label extraction and spatial raster alignment, then
build a corpus of independent designs with grouped splits. Train a simple
baseline before implementing and comparing the hybrid model.
