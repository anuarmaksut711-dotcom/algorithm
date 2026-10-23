"""Graph algorithms for Assignment 3."""

import heapq


class DisjointSet:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n
        self.largest = 1 if n else 0

    def find(self, vertex):
        while self.parent[vertex] != vertex:
            self.parent[vertex] = self.parent[self.parent[vertex]]
            vertex = self.parent[vertex]
        return vertex

    def union(self, first, second):
        first = self.find(first)
        second = self.find(second)
        if first == second:
            return False
        if self.size[first] < self.size[second]:
            first, second = second, first
        self.parent[second] = first
        self.size[first] += self.size[second]
        self.components -= 1
        self.largest = max(self.largest, self.size[first])
        return True


def dsu(request):
    groups = DisjointSet(request["n"])
    states = []
    for first, second in request["operations"]:
        groups.union(first, second)
        states.append([groups.components, groups.largest])
    return {"states": states}


def kruskal(request):
    edges = request["edges"]
    groups = DisjointSet(request["n"])
    edge_ids = []
    cost = 0
    # Sort IDs, so each chosen ID still refers to the original edge list.
    for edge_id in sorted(range(len(edges)), key=lambda i: edges[i][2]):
        first, second, weight = edges[edge_id]
        if groups.union(first, second):
            edge_ids.append(edge_id)
            cost += weight
    return {"cost": cost, "edge_ids": edge_ids, "components": groups.components}


def prim(request):
    n = request["n"]
    adjacency = [[] for _ in range(n)]
    for edge_id, (first, second, weight) in enumerate(request["edges"]):
        adjacency[first].append((weight, edge_id, second))
        adjacency[second].append((weight, edge_id, first))

    visited = [False] * n
    edge_ids = []
    cost = 0
    components = 0
    for start in range(n):
        if visited[start]:
            continue
        components += 1
        visited[start] = True
        heap = list(adjacency[start])
        heapq.heapify(heap)
        while heap:
            weight, edge_id, vertex = heapq.heappop(heap)
            if visited[vertex]:
                continue
            visited[vertex] = True
            edge_ids.append(edge_id)
            cost += weight
            for next_weight, next_id, neighbour in adjacency[vertex]:
                if not visited[neighbour]:
                    heapq.heappush(heap, (next_weight, next_id, neighbour))
    return {"cost": cost, "edge_ids": edge_ids, "components": components}


def finish_order(adjacency, check_cycles=False):
    """Return DFS finish order, or None if a cycle check finds a back edge."""
    state = [0] * len(adjacency)
    order = []
    for start in range(len(adjacency)):
        if state[start] != 0:
            continue
        state[start] = 1
        stack = [(start, 0)]
        while stack:
            vertex, index = stack[-1]
            if index == len(adjacency[vertex]):
                stack.pop()
                state[vertex] = 2
                order.append(vertex)
                continue
            neighbour = adjacency[vertex][index]
            stack[-1] = (vertex, index + 1)
            if state[neighbour] == 0:
                state[neighbour] = 1
                stack.append((neighbour, 0))
            elif check_cycles and state[neighbour] == 1:
                return None
    return order


def scc(request):
    n = request["n"]
    adjacency = [[] for _ in range(n)]
    transpose = [[] for _ in range(n)]
    for first, second in request["edges"]:
        adjacency[first].append(second)
        transpose[second].append(first)

    order = finish_order(adjacency)
    component = [-1] * n
    label = 0
    for start in reversed(order):
        if component[start] != -1:
            continue
        component[start] = label
        stack = [start]
        while stack:
            vertex = stack.pop()
            for neighbour in transpose[vertex]:
                if component[neighbour] == -1:
                    component[neighbour] = label
                    stack.append(neighbour)
        label += 1

    pairs = set()
    for first, second in request["edges"]:
        if component[first] != component[second]:
            pairs.add((component[first], component[second]))
    return {"component": component, "condensation": [list(pair) for pair in pairs]}


def topo(request):
    adjacency = [[] for _ in range(request["n"])]
    for first, second in request["edges"]:
        adjacency[first].append(second)
    order = finish_order(adjacency, check_cycles=True)
    if order is None:
        return {"acyclic": False, "order": []}
    order.reverse()
    return {"acyclic": True, "order": order}


def dag(request):
    n = request["n"]
    source = request["source"]
    edges = request["edges"]
    adjacency = [[] for _ in range(n)]
    outgoing_ids = [[] for _ in range(n)]
    for edge_id, (first, second, weight) in enumerate(edges):
        adjacency[first].append(second)
        outgoing_ids[first].append(edge_id)

    order = finish_order(adjacency, check_cycles=True)
    if order is None:
        return {"acyclic": False, "distance": [], "parent_edge": []}

    distance = [None] * n
    parent_edge = [-1] * n
    distance[source] = 0
    for vertex in reversed(order):
        if distance[vertex] is None:
            continue
        for edge_id in outgoing_ids[vertex]:
            first, second, weight = edges[edge_id]
            candidate = distance[first] + weight
            if distance[second] is None or candidate < distance[second]:
                distance[second] = candidate
                parent_edge[second] = edge_id
    return {"acyclic": True, "distance": distance, "parent_edge": parent_edge}


def reconstruct_route(source, target, edges, parent_edge):
    """Return source-to-target vertices; an unreachable target returns []."""
    if target == source:
        return [source]
    if parent_edge[target] == -1:
        return []
    route = [target]
    while target != source:
        edge_id = parent_edge[target]
        target = edges[edge_id][0]
        route.append(target)
    route.reverse()
    return route
