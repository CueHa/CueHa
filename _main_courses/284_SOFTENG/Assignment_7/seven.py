#!/usr/bin/env python3
"""
Directed girth of a digraph
- For each input digraph, output the length of the shortest directed cycle.
- Output 0 if the digraph has no directed cycle.
- Input ends with a single line containing 0.
- Each digraph:
    line 1: n  (number of nodes, labeled 0..n-1)
    next n lines: adjacency list for node 0, then 1, ..., n-1
        - zero or more space-separated integers
        - an empty line means no outgoing edges
"""

import sys
from collections import deque


def read_all_lines():
    # Keep raw lines, do not strip globally to preserve empty adjacency lines
    return [ln.rstrip("\n") for ln in sys.stdin.readlines()]


def next_nonblank_as_n(lines, i):
    """Advance index i to the next non-empty line, return (value, new_i).
    Returns (None, i) on EOF."""
    m = len(lines)
    while i < m and lines[i].strip() == "":
        i += 1
    if i >= m:
        return None, i
    return lines[i].strip(), i + 1


def parse_graphs(lines):
    """Yield adjacency lists for each graph in the stream."""
    i = 0
    m = len(lines)
    while True:
        token, i = next_nonblank_as_n(lines, i)
        if token is None:
            break
        if token == "0":
            break

        try:
            n = int(token)
        except ValueError:
            raise ValueError(
                f"Expected an integer number of nodes, got: {token!r}")

        adj = [[] for _ in range(n)]
        for v in range(n):
            if i >= m:
                line = ""                  # tolerate truncated file, treat as no edges
            else:
                line = lines[i].strip()
                i += 1
            if line == "":
                neighbors = []
            else:
                parts = [t for t in line.split() if t != ""]
                try:
                    neighbors = [int(t) for t in parts]
                except ValueError:
                    raise ValueError(
                        f"Adjacency line {v} contains a non-integer: {line!r}")
            adj[v] = neighbors
        yield adj


def directed_girth(adj):
    n = len(adj)
    INF = 10**18
    best = INF

    # Fast path: any self-loop gives girth 1
    for v in range(n):
        if v in adj[v]:
            return 1

    for s in range(n):
        if best == 2:
            return 2  # cannot do better

        dist = [-1] * n
        q = deque([s])
        dist[s] = 0

        while q:
            u = q.popleft()

            # Prune if even the shortest possible closing edge would not beat best
            if dist[u] + 1 >= best:
                continue

            for w in adj[u]:
                if w == s:
                    # Found a directed cycle that returns to s
                    cand = dist[u] + 1
                    if cand < best:
                        best = cand
                    # do not return yet; a different branch may be shorter
                    continue
                if dist[w] == -1:
                    dist[w] = dist[u] + 1
                    q.append(w)

    return 0 if best == INF else best


def main():
    lines = read_all_lines()
    out_lines = []
    for adj in parse_graphs(lines):
        g = directed_girth(adj)
        out_lines.append(str(g))
    sys.stdout.write("\n".join(out_lines))


if __name__ == "__main__":
    main()
