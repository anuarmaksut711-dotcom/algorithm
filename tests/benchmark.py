"""Compare Kruskal and Prim on the same reproducible graphs."""

import csv
import json
import platform
from pathlib import Path
import random
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "Python"))
sys.path.insert(0, str(ROOT / "tools"))
import algorithms
from public_validate import check


def make_graph(n, m, seed):
    randomizer = random.Random(seed)
    edges = [[i, i + 1, 1] for i in range(n - 1)]
    while len(edges) < m:
        first = randomizer.randrange(n)
        second = randomizer.randrange(n)
        edges.append([first, second, randomizer.randint(2, 1000000000)])
    return {"n": n, "edges": edges}


def main():
    rows = []
    for n, m in [(1000, 5000), (10000, 50000), (50000, 250000)]:
        seed = 20261021 + n
        graph = make_graph(n, m, seed)
        expected = {"cost": n - 1, "components": 1}
        for name, method in [("kruskal", algorithms.kruskal), ("prim", algorithms.prim)]:
            request = dict(graph, task=name)
            # Validate forest and the independently known optimum before timing.
            answer = method(request)
            assert check(request, answer, expected)
            # One complete warm-up call per method and size.
            method(request)
        durations = {"kruskal": [], "prim": []}
        for iteration in range(5):
            for name, method in [("kruskal", algorithms.kruskal), ("prim", algorithms.prim)]:
                request = dict(graph, task=name)
                started = time.perf_counter()
                answer = method(request)
                elapsed = time.perf_counter() - started
                durations[name].append(elapsed)
                assert check(request, answer, expected)
        rows.append({"n": n, "m": m, "seed": seed, "known_optimum": n - 1, "components": 1, "kruskal_seconds": durations["kruskal"], "prim_seconds": durations["prim"], "kruskal_median_seconds": statistics.median(durations["kruskal"]), "prim_median_seconds": statistics.median(durations["prim"])})
    report = {"python": sys.version, "platform": platform.platform(), "machine": platform.machine(), "processor": platform.processor(), "timer": "time.perf_counter", "warmup_calls_per_method_per_size": 1, "repetitions": 5, "boundary": "Only the algorithm call is timed, including internal adjacency/DSU/heap construction and result construction. Graph generation, request construction, JSON parsing, process start, printing, validation, and compilation are excluded for both algorithms.", "rows": rows}
    (ROOT / "tests" / "benchmark_results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    with (ROOT / "tests" / "benchmark_results.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["n", "m", "seed", "method", "run1_seconds", "run2_seconds", "run3_seconds", "run4_seconds", "run5_seconds", "median_seconds"])
        for row in rows:
            for name in ("kruskal", "prim"):
                writer.writerow([row["n"], row["m"], row["seed"], name, *row[name + "_seconds"], row[name + "_median_seconds"]])
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
