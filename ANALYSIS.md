# Assignment 3: analysis

Language: Python 3.12+. The selected implementation is `src/Python/algorithms.py`.
The supplied JSON Lines entry point and public checker were kept unchanged.

## Running and checking

Run these commands from this directory with Python 3.12 or newer:

```sh
python tools/run.py --setup
python tools/run.py --check
python tools/run.py --input tests/my_cases.jsonl
python tests/test_solution.py
python tests/benchmark.py
```

There is no compilation step and no third-party package is needed. The main program
can also read JSON Lines directly with `python src/Python/main.py`. Only JSON results
go to standard output. `python tests/run_public.py` saves actual setup/check output
to `tests/public_checks.txt`.

## DSU

`DisjointSet` starts with one parent and size entry per vertex. `find` follows parent
links and compresses the path by making each visited node point to its grandparent.
`union` finds both roots, attaches the smaller tree below the larger one, updates
its size, decreases the number of components and updates the largest size. A
repeated connection or a self-union returns without changing these counts.

Invariant: roots identify the current partition, each root's size equals the number
of vertices in that set, and `components` is the number of roots. Initially this is
true for singleton sets. Joining two distinct roots merges exactly those two sets,
so their sizes add and the component count falls by one. Path compression changes
only the representation, not membership. Therefore each appended state gives the
correct component count and largest size after that operation.

An empty request has no states and largest size zero. A nonempty graph starts with
largest size one; no initial state is emitted. Time is `O(n + q alpha(n))` amortized,
using path compression and union by size. Memory is `O(n+q)` including all returned
states (`O(n)` working memory).

## Kruskal

The method sorts the original edge IDs by edge weight. It tests edges in that order
and accepts one only if its endpoints belong to different DSU sets. Using IDs rather
than replacing the input list preserves the original ID of every selected edge.

Invariant: accepted edges form a forest and can be extended to a minimum spanning
forest. An edge joining two current trees is a minimum-weight edge across a cut
between them, so the cut property permits adding it to an optimum forest. Edges
within one tree would make a cycle and are skipped. After all edges, each input
component is spanned, isolates remain separate, and there are `n-components` edges.
This proves both feasibility and minimum total cost.

Loops fail the different-root test. Parallel/tied edges may produce different valid
optima; negative weights are sorted normally. Python integers preserve totals beyond
32 bits. For `n=0`, the result is zero cost, no IDs and zero components.
Time is `O(n + m log(m+1))`, with DSU operations absorbed in this bound. Memory is
`O(n+m)` including sorted IDs and the returned forest.

## Prim

The method builds an undirected adjacency list containing weights, original edge
IDs and neighbours. It visits a starting vertex, places its incident edges in a lazy
min-heap, and repeatedly takes the lightest edge leading to an unvisited vertex.
It adds that vertex's outgoing candidate edges. A new unvisited start is selected
when the current component's heap becomes empty.

Invariant: the selected vertices in the current component are joined by the selected
tree, and each selected edge is safe for a minimum tree. The smallest available edge
to an unvisited vertex is a light edge crossing the visited/unvisited cut; the cut
property proves the invariant inductively. Discarding an edge whose target is already
visited avoids cycles. When the heap empties, all vertices reachable from the start
are visited. Restarting consequently finds one minimum tree per component, including
isolates, and their union is a minimum spanning forest.

Negative, parallel and tied edges are valid heap items. A loop points to an already
visited vertex and is never selected. Empty graphs return an empty forest.
The lazy heap may contain `O(m)` entries, so time is `O(n + m log(m+1))`, not an
indexed-heap `O((n+m) log n)` claim. Memory is `O(n+m)` including adjacency, heap and
output.

## Kosaraju SCC

The first DFS records vertices when they finish. The second pass visits the
transposed graph in decreasing first-pass finish order. Every second-pass search
gets one new component label. The method then scans original directed edges and
inserts each cross-component label pair into a set, returning each pair once.

The first-pass finish order puts a suitable source SCC of the remaining original
condensation before the others in the second pass. In the transpose, that SCC
cannot reach any other unassigned SCC. Its vertices can all reach each other, so the
second DFS labels exactly that SCC. Removing it and repeating proves the partition
by induction. Internal edges are excluded; a set ensures exact condensation pairs
without duplicates.

Both passes are iterative, so a chain of 100,000 vertices does not use Python call
stack recursion. In the first pass, a stack frame stores `(vertex, next_neighbour)`;
this resumes suspended traversal rather than rescanning the adjacency list. The
second pass needs only a vertex stack and marks vertices when pushing them.
Isolates become singleton SCCs; loops and parallel edges do not affect correctness.
Empty graphs return empty arrays. Time is `O(n+m)` expected with hash-set
condensation deduplication; memory is `O(n+m)` including both graphs and output.

## DFS topological ordering

`finish_order` uses three states: unvisited, active and finished. An unvisited vertex
is marked active when pushed; after all outgoing neighbours it becomes finished.
An edge to an active vertex reveals a back edge, so the result is cyclic. An edge
to a finished vertex is allowed. DFS starts from every unvisited vertex.

Invariant: active stack frames form the current DFS path and each frame retains the
next outgoing neighbour to inspect. Thus an edge to an active vertex closes a directed
cycle. Conversely every directed cycle gives a back edge during a complete DFS.
If none occurs, for every edge `u->v`, vertex `v` finishes before `u` (unless it was
already finished), so reversing finish order places `u` before `v`. All vertices
appear once, including disconnected vertices. A cycle anywhere returns `false` and
an empty order. A self-loop is a back edge; `n=0` is acyclic.
Each vertex is pushed once and each edge inspected once, so time and total memory
are `O(n+m)`.

## DAG shortest paths and routes

The method builds outgoing original edge IDs and runs the same whole-graph DFS
cycle check. It returns two empty arrays on any cycle, including one unreachable
from the source. Otherwise it starts with source distance zero and `None` elsewhere,
and relaxes edges from reachable vertices in topological order. On improvement it
records the original incoming edge ID, not the predecessor vertex.

Invariant: when processing vertex `v`, every path to `v` has its final predecessor
earlier in the order, so all candidates have already been considered. Its current
distance is therefore the shortest distance. Relaxation sends that optimum forward;
induction over the order proves all finite distances. Negative weights are safe
because the order prevents cycles. No edge from an unreachable vertex is relaxed.
Parent edges obey `distance[u]+weight=distance[v]`, end at the child vertex, and point
backwards in topological order, so following them reaches the source. The source and
unreachable vertices retain parent ID `-1`. Distance `-1` is allowed as a finite
value; JSON `null` alone represents an unreachable distance. Python integers avoid
32-bit overflow.

`reconstruct_route(source, target, edges, parent_edge)` follows selected incoming
edges backwards, collects vertices and reverses the list. Its input parents are a
valid acyclic result from `dag`. It returns `[source]` for the source and `[]` for an
unreachable target. DAG computation is `O(n+m)` time and memory. A route containing
`L` vertices costs `O(L)` time and output space.

### Actual helper calls

The calls below are executed directly in `tests/test_solution.py`, which also checks
each selected edge's direction and sum. Full results are in `tests/route_results.json`.

For `edges=[[0,1,3],[0,2,8],[1,2,-7],[2,3,4]]`, source `0`, the returned
`parent_edge` is `[-1,0,2,3,-1]` and distances are `[0,3,-4,0,null]`.

| Helper call | Route | Selected original edge IDs | Weight |
|---|---|---|---:|
| `reconstruct_route(0,3,edges,parents)` | `[0,1,2,3]` | `[0,2,3]` | `3-7+4=0` |
| `reconstruct_route(0,0,edges,parents)` | `[0]` | `[]` | `0` |
| `reconstruct_route(0,4,edges,parents)` | `[]` | `[]` | No route (`null` distance) |

The tied/parallel test uses
`edges=[[0,1,2],[0,1,2],[0,2,1],[2,1,1],[1,3,3],[2,3,4]]`.
It returns parents `[-1,0,2,5]` and distances `[0,2,1,5]`.
`reconstruct_route(0,3,edges,parents)` returns `[0,2,3]`, using original IDs `[2,5]`
with weights `1+4=5`. Edge `0` and parallel edge `1` tie for vertex `1`; the tests
also supply a valid answer choosing the second parallel edge and require the semantic
checker to accept it.

## State reset and test evidence

Each request creates its own DSU, adjacency, visited/state arrays, heap, labels and
distance arrays. There is no mutable module-level algorithm state. The supplied
adapter preserves `ping` and handles several JSON requests in one process.

Executed checks:

- Setup ping: PASS.
- All 36 unchanged public cases: PASS.
- Two complete public batches in one persistent process: PASS.
- 25 own cases, repeated twice plus ping in one process (51 requests): PASS.
- Four direct route-helper calls: PASS.
- Four alternative-witness acceptance and four invalid-witness rejection tests: PASS.
- Nine full-limit process tests with `n=100000`, `m/q=250000`: PASS.

`tests/my_cases.jsonl` stores own inputs, `expected_cases.json` stores independently
justified expectations and `actual_outputs.jsonl` stores actual results. Expected
costs are proved using the displayed trees/edge weights; SCC partitions are justified
by mutual reachability; cycle and distance explanations accompany their cases.
The unchanged public validator checks witness semantics rather than comparing a
single chosen optimum. `witness_results.json` explicitly shows another valid forest,
renamed SCC labels, a different topological order and a different parallel parent
edge being accepted, and invalid witnesses being rejected.

The full-limit generator is in `large_tests()` in `tests/test_solution.py`. It makes
a chain of 99,999 links, then repeats links until 250,000 edges/operations. Positive
weighted copies have weight one billion; DAG copies have weight minus one billion.
This gives known chain costs/distances of magnitude 99,999,000,000,000, a unique
underlying tree, singleton SCCs and a forward order. Three extra tests replace one
repeated edge by the closing edge `99999->0`, creating a 100,000-deep cycle: SCC
must be one component and topo/DAG must reject. All nine actual outputs are checked;
`large_results.json` saves durations, output sizes and SHA-256 hashes. The large
inputs are regenerated instead of storing bulky copies. These runs also verify
processing and JSON output inside the supplied 20-second per-batch bound.

## Kruskal-Prim benchmark

Command: `python tests/benchmark.py`. Results were measured on 21 October 2026.
Environment: Python 3.12.14, Windows 11 build 26200, AMD64, AMD Ryzen 7 250 with Radeon
780M Graphics, 8 physical cores / 16 logical processors, 16,435,761,152 bytes RAM
(about 15.31 GiB). Both implementations are single-threaded. Timer:
`time.perf_counter()` in seconds. No compilation is involved.

The reproducible generator `make_graph(n,m,seed)` starts with the chain edges of
weight 1 and adds random endpoint pairs with integer weights 2 through 1,000,000,000,
allowing loops and duplicates. The seed is `20261021+n`. Every graph is connected;
every spanning tree has `n-1` edges of weight at least 1, while the chain achieves
cost `n-1`. This proves the expected optimum independently. Before timing, both
results are checked for that cost, connectedness and a valid acyclic spanning
witness. There is one additional full warm-up call per method and size. Every timed
result is validated too, outside the timing interval.

Both methods receive the identical edge-list object at each size. The timed interval
contains only the algorithm call: its internal sorting/DSU or adjacency/heap
construction, algorithm work and result construction. Graph generation, request
construction, JSON parsing, process start, printing and checking are excluded for
both. Five iterations run Kruskal first, then Prim. All measurements and medians:

| n | m | Seed | Method | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | Median |
|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 1,000 | 5,000 | 20262021 | Kruskal | 0.004232 | 0.003169 | 0.002953 | 0.003064 | 0.002884 | 0.003064 |
| 1,000 | 5,000 | 20262021 | Prim | 0.007375 | 0.008092 | 0.007528 | 0.012488 | 0.011415 | 0.008092 |
| 10,000 | 50,000 | 20271021 | Kruskal | 0.066828 | 0.053857 | 0.058742 | 0.062128 | 0.036966 | 0.058742 |
| 10,000 | 50,000 | 20271021 | Prim | 0.168215 | 0.159501 | 0.188765 | 0.107917 | 0.097555 | 0.159501 |
| 50,000 | 250,000 | 20311021 | Kruskal | 0.355617 | 0.359443 | 0.353262 | 0.361382 | 0.378107 | 0.359443 |
| 50,000 | 250,000 | 20311021 | Prim | 0.985156 | 0.944523 | 1.198698 | 1.012091 | 0.959778 | 0.985156 |

`tests/benchmark_results.json` and `.csv` contain unrounded timings. On these inputs,
Kruskal has a lower measured median at all sizes. Prim builds an adjacency list and
manages many heap tuples, while Kruskal uses Python's built-in sort and a simple DSU.
This is a description of these measurements, not a proof that Kruskal is always
faster. Both implementations have `O(n+m log(m+1))` bounds.

Limitations: the generator deliberately includes a cheap chain and only heavier
extra edges; it does not model arbitrary MST weight distributions, disconnected
networks or dense graphs of many densities. The fixed Kruskal-first order can bias
cache and scheduling effects. This was a normal desktop run with possible background
load, no CPU isolation or frequency control, and five samples per size. Parsing and
process costs are excluded. More graph families and randomized method order would
be needed for broader performance conclusions. Full-limit and correctness tests
cover additional edge cases separately from this benchmark.

## Sources and submission

The official task specification, language stubs, JSON adapter, public cases and
semantic validator come from
<https://github.com/RZhaniya/daa-assignment-3-graphs>, template commit
`76c1d91daa90ceadcb225f5408d54d4bfcf397f9`. The original task specifications remain available in that repository. The algorithm implementation, own cases,
route checks and benchmark are in the selected Python source and `tests/`.

Repository: <https://github.com/anuarmaksut711-dotcom/algorithm>.
The Moodle submission requires the exact commit URL. Public checks are pass/fail,
not a calculated practical grade. The separate Moodle defence quiz is completed
in Moodle.
