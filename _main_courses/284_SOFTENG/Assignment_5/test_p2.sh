#!/usr/bin/env bash
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Usage: $0 path/to/p2.py"
  exit 1
fi

SOL="$1"
if [ ! -f "$SOL" ]; then
  echo "Solution not found: $SOL"
  exit 1
fi

tmpdir="$(mktemp -d)"
pass=0
fail=0

run_case () {
  local name="$1"
  local input="$2"
  local expected="$3"

  local infile="$tmpdir/$name.in"
  local expfile="$tmpdir/$name.exp"
  local outfile="$tmpdir/$name.out"
  local errfile="$tmpdir/$name.err"

  # Write inputs/expected exactly, and force a trailing newline (EOF) on both
  printf '%s' "$input"   > "$infile";  printf '\n' >> "$infile"
  printf '%s' "$expected" > "$expfile"; printf '\n' >> "$expfile"


  if ! python3 "$SOL" < "$infile" > "$outfile" 2>"$errfile"; then
    echo "[FAIL] $name (runtime error)"
    sed -n '1,200p' "$errfile"
    ((fail++))
    return
  fi

  if diff -u "$expfile" "$outfile"; then
    echo "[PASS] $name"
    ((pass++))
  else
    echo "[FAIL] $name (output mismatch)"
    echo "Input:"
    nl -ba "$infile" | sed -n '1,200p'
    echo "Expected:"
    cat "$expfile"
    echo "Got:"
    cat "$outfile"
    ((fail++))
  fi
}

########################################
# Define test cases (inputs/expecteds)
########################################

INPUT_CHAIN=$(
cat <<'EOF'
4
1
2
3

0
EOF
)
EXP_CHAIN=$(
cat <<'EOF'
3 0
EOF
)

INPUT_FORK_CROSS=$(
cat <<'EOF'
3
1 2

1
0
EOF
)
EXP_FORK_CROSS=$(
cat <<'EOF'
2 1
EOF
)

INPUT_SINGLE_EMPTY=$(
cat <<'EOF'
1

0
EOF
)
EXP_SINGLE_EMPTY=$(
cat <<'EOF'
0 0
EOF
)

INPUT_CYCLE3=$(
cat <<'EOF'
3
1
2
0
0
EOF
)
EXP_CYCLE3=$(
cat <<'EOF'
2 0
EOF
)

INPUT_SELF_LOOP=$(
cat <<'EOF'
1
0
0
EOF
)
EXP_SELF_LOOP=$(
cat <<'EOF'
0 0
EOF
)

# 4 nodes totally disconnected from 0 (only start from 0)
INPUT_DISCONNECTED=$(
cat <<'EOF'
4



 
0
EOF
)
EXP_DISCONNECTED=$(
cat <<'EOF'
0 0
EOF
)

########################################
# Run cases
########################################
run_case "chain"         "$INPUT_CHAIN"         "$EXP_CHAIN"
run_case "fork_cross"    "$INPUT_FORK_CROSS"    "$EXP_FORK_CROSS"
run_case "single_empty"  "$INPUT_SINGLE_EMPTY"  "$EXP_SINGLE_EMPTY"
run_case "cycle3"        "$INPUT_CYCLE3"        "$EXP_CYCLE3"
run_case "self_loop"     "$INPUT_SELF_LOOP"     "$EXP_SELF_LOOP"
run_case "disconnected"  "$INPUT_DISCONNECTED"  "$EXP_DISCONNECTED"

echo
echo "Summary: PASS=$pass FAIL=$fail"
[ "$fail" -eq 0 ] || exit 1
