# Assignment 3 - Graph Algorithms

Python 3.12 or newer. Standard library only.

## Implementation

`src/Python/algorithms.py` contains DSU, Kruskal, Prim, Kosaraju SCC, DFS topological ordering, DAG shortest paths and route reconstruction.
`submission.json` selects Python. The entry point reads one JSON request per line and writes one JSON result per line.

## Run and test

Run from this folder with Python 3.12+:

```sh
python tools/run.py --setup
python tools/run.py --check
python tests/test_solution.py
python tests/benchmark.py
```

Use `python tools/run.py --input tests/my_cases.jsonl` for sample inputs.

## Documentation

- `ANALYSIS.md`: algorithms, correctness, complexity and measured benchmark.
- `RUN.md`: local run instructions.
- `tests/README.md`: cases, expectations and actual results.

Task specification and original template: <https://github.com/RZhaniya/daa-assignment-3-graphs>.

Repository: <https://github.com/anuarmaksut711-dotcom/algorithm>.
For Moodle, use the exact commit URL. The separate defence quiz is completed in Moodle.
