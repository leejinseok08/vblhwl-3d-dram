#!/bin/bash
# arch_remove.sh <manifest.md5> <dir> <copy checked: yes> : the second half of moving a folder off the server. Takes away exactly
# the files of the manifest (written by tools/arch_manifest.sh, paths relative to the parent of <dir>) and then the directories
# that are left empty, never anything under a path that contains "/codex_" (those belong to Codex). Refuses unless the third
# argument is the word yes: it is given only after the copy off the server was compared with the manifest file by file.
m=$1; d=$2; [ "${3:-}" = yes ] || { echo "not confirmed: nothing removed"; exit 1; }
cd "$(dirname "$d")" || exit 1; b=$(basename "$d")
n=0; while IFS= read -r line; do f=${line:34}; case "$f" in "$b"/codex_*) echo "skipped (Codex): $f"; continue;; "$b"/*) ;; *) echo "outside $b: $f"; continue;; esac
  [ -f "$f" ] && rm -f -- "$f" && n=$((n + 1)); done < "$m"
find "$b" -depth -type d -empty -not -path "$b/codex_*" -delete
echo "removed $n files of $(wc -l < "$m") in the manifest; left in $b: $(find "$b" -type f | wc -l) files, $(du -sm "$b" | cut -f1) MB"
