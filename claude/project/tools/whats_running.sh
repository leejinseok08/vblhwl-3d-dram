#!/bin/bash
# whats_running.sh [-s] - the sdevice jobs of the calling user (elapsed time, working directory, deck) and the batch
# scripts still alive. -s: only the number of sdevice jobs per run folder. Read-only: use it before starting or
# stopping anything, another session may be running jobs.
if [ "${1:-}" = "-s" ]; then
  for p in $(pgrep -u "$USER" -x sdevice); do readlink /proc/$p/cwd; done | sed -e 's#/[^/]*$##' | sort | uniq -c
  uptime
  exit 0
fi
for p in $(pgrep -u "$USER" -f 'sdevice|run_[a-z0-9_]*\.sh|xargs -P'); do
  [ -d /proc/$p ] || continue
  printf '%s  %s  %s\n    %s\n' "$p" "$(ps -o etime= -p $p)" "$(readlink /proc/$p/cwd)" "$(tr '\0' ' ' < /proc/$p/cmdline | cut -c1-160)"
done
