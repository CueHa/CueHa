#!/usr/bin/env python3
# Phases 0–3: I/O contract + IN0/OUT0 + duplicate node + required output formatting

import sys

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
        # Skip blank lines that may appear between graphs or before the final 0.
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
                nums.sort()
                adj.append(nums)

        yield n, adj

def process_graph(n, adj):
    """
    Phase 2: duplicate node 0's neighbourhood to a new node n.
      OUT0 = adj[0]
      IN0  = [u for u in range(n) if 0 in adj[u]]
      new_adj = deep copy of adj
      new_adj.append(copy of OUT0)   # new node n out-neighbours
      for u in IN0: new_adj[u].append(n)
      arcs_added = len(OUT0) + len(IN0)
    Returns (n+1, new_adj, arcs_added).
    """
    OUT0 = adj[0]
    IN0 = [u for u in range(n) if 0 in adj[u]]

    new_adj = [list(L) for L in adj]
    new_adj.append(list(OUT0))       # row for new node n

    for u in IN0:
        new_adj[u].append(n)         # n is the largest index, append keeps order

    arcs_added = len(OUT0) + len(IN0)
    return n + 1, new_adj, arcs_added

def write_graph(n, adj, arcs_added, out=sys.stdout):
    """
    Phase 3 output, exactly:
      1) print n
      2) print each of the n rows: empty line if row empty, else neighbors joined by a single space
      3) print arcs_added
    No extra blank lines before, between, or after graphs.
    """
    out.write(str(n) + "\n")
    for row in adj:
        if row:
            out.write(" ".join(str(x) for x in row) + "\n")
        else:
            out.write("\n")
    out.write(str(arcs_added) + "\n")

def main():
    for n, adj in read_graphs():
        n2, adj2, arcs = process_graph(n, adj)
        write_graph(n2, adj2, arcs)

if __name__ == "__main__":
    main()

# Last Try
