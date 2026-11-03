export DESIGN_NAME = gcd
export PLATFORM = sky130hd
export VERILOG_FILES = /project/examples/gcd/gcd.v
export SDC_FILE = /project/examples/gcd/constraints.sdc.in
export CORE_UTILIZATION = 38
export PLACE_DENSITY = 0.60
export TNS_END_PERCENT = 100
export SYNTH_REPEATABLE_BUILD = 1
# Use ordinary arithmetic cells for this small reference design.
export ADDER_MAP_FILE :=
