# GCD reference design

Original Apache-2.0 RTL implementing the unsigned Euclidean subtraction
algorithm, with synchronous active-high reset. Accept `start` for one cycle
when `busy` is low; keep operands stable for that acceptance edge. Requests
while busy are ignored. `done` pulses for one cycle and `result` remains stable
until the next completed calculation or reset. GCD(0, 0) returns zero.

This small design checks the physical-design/data-extraction pipeline. It is
not a representative training corpus or evidence of model generalization.
The 20 ns timing constraint is a declared experimental setting, not a measured
achievable performance claim. The supplied Sky130 platform subset is used for
research; this example does not establish foundry-qualified sign-off.
