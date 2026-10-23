"""Own cases, semantic witness checks, route calls and full-limit tests."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src" / "Python"))
sys.path.insert(0, str(ROOT / "tools"))
import algorithms
from public_validate import check

TESTS = ROOT / "tests"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def write_lines(path, values):
    path.write_text("".join(json.dumps(value, separators=(",", ":")) + "\n" for value in values), encoding="utf-8")


def cases():
    result = []
    def add(name, request, expected, reason):
        result.append({"name": name, "input": request, "output": expected, "reason": reason})

    add("empty dsu", {"task": "dsu", "n": 0, "operations": []}, {"states": []}, "No vertices and no operations produce no states.")
    add("repeated and self unions", {"task": "dsu", "n": 5, "operations": [[0, 0], [0, 1], [1, 0], [2, 3], [1, 3], [4, 4]]}, {"states": [[5, 1], [4, 2], [4, 2], [3, 2], [2, 4], [2, 4]]}, "The first and repeated/self unions change nothing; the merged four-vertex group leaves vertex 4 isolated.")
    for task in ("kruskal", "prim"):
        add(task + " empty", {"task": task, "n": 0, "edges": []}, {"cost": 0, "components": 0}, "The empty forest has zero cost and components.")
        add(task + " isolates", {"task": task, "n": 4, "edges": []}, {"cost": 0, "components": 4}, "Every isolated vertex is one component.")
        add(task + " negative parallel loops", {"task": task, "n": 5, "edges": [[0, 0, -100], [0, 1, 4], [0, 1, -3], [1, 2, 2], [0, 2, 2], [3, 3, -8]]}, {"cost": -1, "components": 3}, "Component {0,1,2} needs the -3 edge and one edge of weight 2; loops are unusable and vertices 3/4 are separate.")
        add(task + " 64 bit cost", {"task": task, "n": 5, "edges": [[0, 1, 1000000000], [1, 2, 1000000000], [2, 3, 1000000000], [3, 4, 1000000000]]}, {"cost": 4000000000, "components": 1}, "The graph is already a tree with four edges of weight one billion.")
        add(task + " tied forest", {"task": task, "n": 3, "edges": [[0, 1, 1], [1, 2, 1], [0, 2, 1], [0, 1, 1]]}, {"cost": 2, "components": 1}, "Any two distinct edges connecting all three vertices form a minimum tree.")
    add("empty scc", {"task": "scc", "n": 0, "edges": []}, {"component": []}, "There are no components or condensation edges.")
    add("scc duplicates and isolate", {"task": "scc", "n": 6, "edges": [[0, 1], [1, 0], [1, 2], [0, 2], [1, 2], [2, 3], [3, 2], [3, 4], [4, 4]]}, {"component": [0, 0, 1, 1, 2, 3]}, "Mutually reachable pairs are {0,1} and {2,3}; {4} and isolated {5} are singleton SCCs. Condensation is A->B->C.")
    add("empty topo", {"task": "topo", "n": 0, "edges": []}, {"acyclic": True}, "The empty graph is acyclic.")
    add("topo cross edge and disconnected", {"task": "topo", "n": 6, "edges": [[0, 2], [1, 2], [2, 3], [0, 3], [0, 2]]}, {"acyclic": True}, "All edges go from levels {0,1} to {2} to {3}; vertices 4/5 are free.")
    add("topo outside component cycle", {"task": "topo", "n": 5, "edges": [[0, 1], [2, 3], [3, 2]]}, {"acyclic": False}, "Vertices 2 and 3 form a cycle, even though the first component is acyclic.")
    add("topo self loop", {"task": "topo", "n": 2, "edges": [[1, 1]]}, {"acyclic": False}, "A vertex cannot precede itself.")
    add("dag single vertex", {"task": "dag", "n": 1, "source": 0, "edges": []}, {"acyclic": True, "distance": [0]}, "Only the source exists.")
    add("dag negative unreachable", {"task": "dag", "n": 5, "source": 0, "edges": [[0, 1, 3], [0, 2, 8], [1, 2, -7], [2, 3, 4]]}, {"acyclic": True, "distance": [0, 3, -4, 0, None]}, "The best route 0->1->2->3 costs 3-7+4=0; vertex 4 is unreachable.")
    add("dag nonzero source", {"task": "dag", "n": 4, "source": 2, "edges": [[0, 1, -9], [2, 3, -1], [1, 3, -20]]}, {"acyclic": True, "distance": [None, None, 0, -1]}, "Edges from unreachable vertices must never be relaxed, and -1 is a finite distance.")
    add("dag tied parallel", {"task": "dag", "n": 4, "source": 0, "edges": [[0, 1, 2], [0, 1, 2], [0, 2, 1], [2, 1, 1], [1, 3, 3], [2, 3, 4]]}, {"acyclic": True, "distance": [0, 2, 1, 5]}, "Parallel edges and the route via 2 tie at vertex 1; two routes to 3 cost 5.")
    add("dag cycle outside source reachability", {"task": "dag", "n": 5, "source": 0, "edges": [[0, 1, 1], [2, 3, -1], [3, 2, 1]]}, {"acyclic": False}, "The disconnected 2->3->2 cycle makes the whole request cyclic.")
    add("dag self loop", {"task": "dag", "n": 1, "source": 0, "edges": [[0, 0, 0]]}, {"acyclic": False}, "A zero-weight self-loop is still a cycle.")
    add("dag 64 bit distance", {"task": "dag", "n": 5, "source": 0, "edges": [[0, 1, -1000000000], [1, 2, -1000000000], [2, 3, -1000000000], [3, 4, -1000000000]]}, {"acyclic": True, "distance": [0, -1000000000, -2000000000, -3000000000, -4000000000]}, "A unique chain accumulates costs below the signed 32-bit minimum.")
    return result


def run_process(requests):
    text = "".join(json.dumps(request, separators=(",", ":")) + "\n" for request in requests)
    started = time.perf_counter()
    result = subprocess.run([sys.executable, str(ROOT / "src" / "Python" / "main.py")], input=text, capture_output=True, text=True, encoding="utf-8", timeout=20, check=True)
    seconds = time.perf_counter() - started
    assert not result.stderr, result.stderr
    answers = [json.loads(line) for line in result.stdout.splitlines()]
    assert len(answers) == len(requests)
    return answers, seconds


def route_tests():
    request = next(case["input"] for case in cases() if case["name"] == "dag negative unreachable")
    answer = algorithms.dag(request)
    records = []
    for target, expected in [(3, [0, 1, 2, 3]), (0, [0]), (4, [])]:
        route = algorithms.reconstruct_route(0, target, request["edges"], answer["parent_edge"])
        assert route == expected
        chosen = []
        current = target
        while route and current != request["source"]:
            edge_id = answer["parent_edge"][current]
            first, second, weight = request["edges"][edge_id]
            assert second == current
            chosen.append(edge_id)
            current = first
        chosen.reverse()
        cost = sum(request["edges"][edge_id][2] for edge_id in chosen) if route else None
        assert cost == answer["distance"][target]
        records.append({"case": "negative unreachable", "source": 0, "target": target, "parent_edge": answer["parent_edge"], "selected_edge_ids": chosen, "route": route, "cost": cost})
    request = next(case["input"] for case in cases() if case["name"] == "dag tied parallel")
    answer = algorithms.dag(request)
    route = algorithms.reconstruct_route(0, 3, request["edges"], answer["parent_edge"])
    ids = []
    current = 3
    while current != 0:
        edge_id = answer["parent_edge"][current]
        first, second, weight = request["edges"][edge_id]
        assert second == current
        ids.append(edge_id)
        current = first
    ids.reverse()
    assert sum(request["edges"][edge_id][2] for edge_id in ids) == 5
    assert route == [0] + [request["edges"][edge_id][1] for edge_id in ids]
    records.append({"case": "tied parallel", "source": 0, "target": 3, "parent_edge": answer["parent_edge"], "selected_edge_ids": ids, "route": route, "cost": 5})
    return records


def witness_tests():
    records = []
    examples = [
        ({"task": "kruskal", "n": 3, "edges": [[0, 1, 1], [1, 2, 1], [0, 2, 1]]}, {"cost": 2, "components": 1}, {"cost": 2, "components": 1, "edge_ids": [0, 2]}, {"cost": 2, "components": 1, "edge_ids": [0, 0]}),
        ({"task": "scc", "n": 3, "edges": [[0, 1], [1, 0], [1, 2]]}, {"component": [0, 0, 1]}, {"component": [8, 8, 20], "condensation": [[8, 20]]}, {"component": [8, 8, 20], "condensation": []}),
        ({"task": "topo", "n": 3, "edges": [[0, 2], [1, 2]]}, {"acyclic": True}, {"acyclic": True, "order": [1, 0, 2]}, {"acyclic": True, "order": [0, 2, 1]}),
        ({"task": "dag", "n": 2, "source": 0, "edges": [[0, 1, 2], [0, 1, 2]]}, {"acyclic": True, "distance": [0, 2]}, {"acyclic": True, "distance": [0, 2], "parent_edge": [-1, 1]}, {"acyclic": True, "distance": [0, 2], "parent_edge": [-1, -1]}),
    ]
    for request, expected, alternative, invalid in examples:
        assert check(request, alternative, expected)
        assert not check(request, invalid, expected)
        records.append({"input": request, "expected": expected, "alternative_accepted": alternative, "invalid_rejected": invalid})
    return records


def large_tests():
    n = 100000
    m = 250000
    chain = [[i, i + 1] for i in range(n - 1)]
    pairs = chain + [chain[i % len(chain)] for i in range(m - len(chain))]
    weighted = [[u, v, 1000000000] for u, v in pairs]
    records = []
    for task in ("dsu", "kruskal", "prim", "scc", "topo", "dag"):
        request = {"task": task, "n": n}
        if task == "dsu":
            request["operations"] = pairs
            expected = {"states": [[n - i - 1, i + 2] if i < n - 1 else [1, n] for i in range(m)]}
        elif task in ("kruskal", "prim"):
            request["edges"] = weighted
            expected = {"cost": (n - 1) * 1000000000, "components": 1}
        elif task == "scc":
            request["edges"] = pairs
            expected = {"component": list(range(n))}
        elif task == "topo":
            request["edges"] = pairs
            expected = {"acyclic": True}
        else:
            request["source"] = 0
            request["edges"] = [[u, v, -1000000000] for u, v in pairs]
            expected = {"acyclic": True, "distance": [-i * 1000000000 for i in range(n)]}
        answers, seconds = run_process([request])
        assert check(request, answers[0], expected), task
        serialized = json.dumps(answers[0], separators=(",", ":")).encode()
        records.append({"task": task, "n": n, "m_or_q": m, "seconds_including_process_and_json": seconds, "status": "PASS", "output_bytes": len(serialized), "output_sha256": hashlib.sha256(serialized).hexdigest(), "expected_reason": "A repeated directed/undirected chain has a unique forest, singleton SCCs, a forward order and chain distances; DSU merges vertices in order."})
    cycle_pairs = pairs[:-1] + [[n - 1, 0]]
    for task in ("scc", "topo", "dag"):
        request = {"task": task, "n": n, "edges": cycle_pairs}
        if task == "scc":
            expected = {"component": [0] * n}
        elif task == "topo":
            expected = {"acyclic": False}
        else:
            request["source"] = 0
            request["edges"] = [[u, v, 1] for u, v in cycle_pairs]
            expected = {"acyclic": False}
        answers, seconds = run_process([request])
        assert check(request, answers[0], expected), task
        serialized = json.dumps(answers[0], separators=(",", ":")).encode()
        records.append({"task": task + " deep cycle", "n": n, "m_or_q": m, "seconds_including_process_and_json": seconds, "status": "PASS", "output_bytes": len(serialized), "output_sha256": hashlib.sha256(serialized).hexdigest(), "expected_reason": "A closing edge turns the full chain into one directed cycle: one SCC, no topological order and no DAG answer."})
    return records


def main():
    all_cases = cases()
    inputs = [case["input"] for case in all_cases]
    answers, seconds = run_process(inputs + inputs + [{"task": "ping"}])
    for case, answer in zip(all_cases + all_cases, answers):
        assert check(case["input"], answer, case["output"]), case["name"]
    assert answers[-1] == {"status": "ready"}
    write_lines(TESTS / "my_cases.jsonl", inputs)
    write_json(TESTS / "expected_cases.json", all_cases)
    write_lines(TESTS / "actual_outputs.jsonl", answers[:len(inputs)])
    write_json(TESTS / "route_results.json", route_tests())
    write_json(TESTS / "witness_results.json", witness_tests())
    large = large_tests()
    write_json(TESTS / "large_results.json", large)
    report = {"small_cases": len(all_cases), "mixed_requests_in_one_process": len(answers), "mixed_process_seconds": seconds, "route_checks": 4, "alternative_witness_checks": 4, "invalid_witness_checks": 4, "full_limit_cases": len(large), "status": "PASS"}
    write_json(TESTS / "own_test_results.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
