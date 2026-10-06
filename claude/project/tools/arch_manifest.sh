#!/bin/bash
# arch_manifest.sh <dir> <out.md5> [excluded sub-path ...] : md5 of every file under <dir> (paths relative to its parent, sorted),
# leaving out the named sub-paths. Used before a folder is moved off the server: the copy is held against this list file by
# file, and only the files of the list are taken away afterwards (tools/arch_remove.sh).
d=$1; o=$2; shift 2; ex=(); for e in "$@"; do ex+=( -not -path "$e/*" ); done
cd "$(dirname "$d")" || exit 1
find "$(basename "$d")" -type f "${ex[@]}" -print0 | sort -z | xargs -0 md5sum > "$o"
echo "files: $(wc -l < "$o"), $(du -sm "$(basename "$d")" | cut -f1) MB in the whole folder"
