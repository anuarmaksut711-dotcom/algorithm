# Own tests

Run from the repository root using Python 3.12+:

```sh
python tests/run_public.py
python tests/test_solution.py
python tests/benchmark.py
python tools/run.py --input tests/my_cases.jsonl
```

- `run_public.py`: runs the original setup and all public checks; saves actual output
  in `public_checks.txt`.
- `test_solution.py`: runs 25 own small cases twice plus ping in one process, directly
  calls the route helper four times, checks valid alternatives/invalid witnesses, and
  runs nine full-limit process tests. Every failure raises an assertion.
- `benchmark.py`: validates both forests against a mathematically known optimum,
  then measures each method five times on identical graphs at three sizes.

`my_cases.jsonl` and `actual_outputs.jsonl` contain the small inputs and actual output
lines. `expected_cases.json` includes the expected optimum/partition/cycle/distance
and a reason for every case. Non-unique witnesses are checked semantically by the
unchanged official validator, rather than by exact edge-ID or label equality.
`witness_results.json` records valid alternatives and invalid witnesses.
`route_results.json` records actual helper calls, selected IDs, routes and costs.
`large_results.json` records full-limit status, elapsed time and actual-output hashes;
large inputs are reproduced by `large_tests()` instead of storing bulky input files.
`own_test_results.json` is the overall own-test result.

Large inputs use 100,000 vertices and 250,000 edges/operations, including a deep
chain and a closing-edge deep cycle. Expected results follow directly from their
construction. Small cases cover empty and disconnected graphs, isolates, duplicate
and self unions, loops, parallel/tied edges, negative weights, totals beyond 32 bits,
unreachable vertices, and cycles outside source reachability.

For raw benchmark measurements use `benchmark_results.json` or
`benchmark_results.csv`; the root `ANALYSIS.md` explains invariants, correctness,
complexity, test expectations, benchmark boundaries and limitations.
