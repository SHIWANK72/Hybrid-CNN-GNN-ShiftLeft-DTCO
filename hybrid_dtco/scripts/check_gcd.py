"""Check concrete GCD transactions using Yosys bounded SAT, without a simulator."""

import argparse
import json
import math
import subprocess
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--yosys", required=True)
    parser.add_argument("--rtl", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    cases = [(0, 0), (0, 7), (7, 0), (48, 18), (18, 48), (255, 255), (21, 13)]
    results = []
    for a, b in cases:
        # Subtraction steps for these vectors fit well within 24 cycles.
        script = (
            f'read_verilog "{args.rtl}"; prep -top gcd -flatten; '
            f"sat -seq 24 -set-init-zero -set-def-inputs "
            f"-set reset 0 -set start 0 -set a_in {a} -set b_in {b} "
            "-set-at 1 reset 1 -set-at 2 start 1 "
            f"-prove result {math.gcd(a, b)} -prove busy 0 "
            "-prove-skip 23 -verify"
        )
        command_file = args.output / f"gcd_{a}_{b}.ys"
        command_file.write_text(script + "\n")
        run = subprocess.run(
            [args.yosys, "-s", str(command_file)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        (args.output / f"gcd_{a}_{b}.log").write_text(run.stdout + run.stderr)
        passed = run.returncode == 0 and "SUCCESS" in run.stdout
        results.append({"a": a, "b": b, "expected": math.gcd(a, b), "passed": passed})
        if not passed:
            raise RuntimeError(f"GCD SAT check failed for {a}, {b}; see {args.output}")
    (args.output / "functional-checks.json").write_text(
        json.dumps(results, indent=2) + "\n"
    )
    print(
        f"PASS: {len(results)} bounded GCD transaction checks (not exhaustive equivalence)."
    )


if __name__ == "__main__":
    main()
