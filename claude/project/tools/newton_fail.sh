#!/bin/bash
# newton_fail.sh <run> [n] - for the last n (default 3) Newton failures of a run: the step, and which
# equation had the largest error (and where) in the last iteration before sdevice gave up.
cd "$(dirname "$0")/../runs" || exit 1
r=$1; n=${2:-3}
awk -v n="$n" '
  /^Computing step from/ { step = $0; k = 0 }
  /^ *(poisson|electron|hole|eQuantumPot):/ { last[$1] = $0 }
  /^ *[0-9]+ +[0-9.e+-]+ +[0-9.e+-]+ +[0-9.e+-]+ +[0-9.e+-]+/ { it = $0 }
  /didn.t converge/ { c++; S[c] = step; I[c] = it; A[c] = last["poisson:"]; B[c] = last["electron:"]; C[c] = last["hole:"]; D[c] = last["eQuantumPot:"] }
  END { for (i = (c > n ? c - n + 1 : 1); i <= c; i++) { print S[i]; print "  last iteration: " I[i]; print "  " A[i]; print "  " B[i]; print "  " C[i]; print "  " D[i] } }
' "$r/$r.out" | cut -c1-150
