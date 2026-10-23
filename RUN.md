# Local run guide

Requirements: Python 3.12 or newer. No additional packages or compilation are needed.
Open a terminal in this folder and run:

```sh
python tools/run.py --setup
python tools/run.py --check
python tests/test_solution.py
python tests/benchmark.py
```

Example requests are in `tests/my_cases.jsonl`:

```sh
python tools/run.py --input tests/my_cases.jsonl
```

On Windows, `py -3` may replace `python` if it points to Python 3.12+.

Main source: `src/Python/algorithms.py`.
Detailed explanation and actual benchmark: `ANALYSIS.md`.
Test results: `tests/own_test_results.json`, `tests/public_checks.txt`.
Original task: <https://github.com/RZhaniya/daa-assignment-3-graphs>.

Repository: <https://github.com/anuarmaksut711-dotcom/algorithm>.
Moodle requires the exact commit URL. The separate Assignment 3 defence quiz
is completed in Moodle.
