#!/usr/bin/env python3
# SE284 A5 Q2: Count tree and cross arcs in a DFS (start at node 0)
# No libraries beyond the standard library. Prints "<tree> <cross>" per digraph.

import sys

# ---------- Input handling (robust to blank lines between graphs) ----------

def _read_stripped_line():
    """Read one line, strip surrounding whitespace. Return None on EOF."""
    line = sys.stdin.readline()
    if line == "":
        return None
    return line.strip()

def read_graphs():
    """
    Yield (n, adj) for each input graph until a line equal to "0".
    Adjacency lines: consume exactly n lines after n, allowing empty lines.
    Between graphs or before the final 0: skip blank lines only at header time.
    """
    while True:
        header = _read_stripped_line()
        while header == "":
            header = _read_stripped_line()

        if header is None:
            break
        if header == "0":
            break

        try:
            n = int(header)
        except ValueError:
            raise SystemExit("Expected integer n, got %r" % header)
        if n < 1:
            raise SystemExit("n must be >= 1")

        adj = []
        for _ in range(n):
            line = sys.stdin.readline()
            if line == "":
                raise SystemExit("Unexpected EOF while reading adjacency lines")
            line = line.strip()
            if line == "":
                adj.append([])
            else:
                try:
                    nums = [int(tok) for tok in line.split()]
                except ValueError:
                    raise SystemExit("Adjacency line must contain integers: %r" % line)
                nums.sort()  # lists are specified to be sorted; keep it deterministic
                adj.append(nums)

        yield n, adj

# ---------- Core: DFS classification (tree vs cross) ----------

def count_tree_and_cross(n, adj):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = [WHITE] * n
    disc  = [-1] * n   # discovery time
    fin   = [-1] * n   # finish time

    time = 0
    tree_count = 0
    edges_to_black = []  # collect (u,v) seen where color[v] == BLACK

    # DFS forest: start at 0, then 1, 2, ... for any remaining WHITE vertices
    for s in range(n):
        if color[s] != WHITE:
            continue

        color[s] = GRAY
        disc[s] = time; time += 1
        stack = [[s, 0]]  # [node, next-neighbor-index]

        while stack:
            u, i = stack[-1]

            if i < len(adj[u]):
                v = adj[u][i]
                stack[-1][1] = i + 1  # advance neighbor pointer

                if color[v] == WHITE:
                    tree_count += 1
                    color[v] = GRAY
                    disc[v] = time; time += 1
                    stack.append([v, 0])
                elif color[v] == BLACK:
                    # forward or cross; disambiguate later using (disc, fin)
                    edges_to_black.append((u, v))
                else:
                    # GRAY => back edge; not counted
                    pass
            else:
                # done with u
                stack.pop()
                color[u] = BLACK
                fin[u] = time; time += 1

    # Classify BLACK-target edges: forward if v is a descendant of u, else cross.
    cross_count = 0
    for (u, v) in edges_to_black:
        # v is a descendant of u iff disc[u] < disc[v] and fin[v] < fin[u]
        if disc[u] < disc[v] and fin[v] < fin[u]:
            # forward edge, ignore
            pass
        else:
            cross_count += 1

    return tree_count, cross_count

# ---------- Driver ----------

def main():
    out = sys.stdout
    for n, adj in read_graphs():
        tree, cross = count_tree_and_cross(n, adj)
        out.write(f"{tree} {cross}\n")

if __name__ == "__main__":
    main()
