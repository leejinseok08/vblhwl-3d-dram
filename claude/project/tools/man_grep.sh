#!/bin/bash
# man_grep.sh <pattern> [lines after] [lines before] - search the Sentaurus Device user guide of the installed release.
# The PDF is converted to text once (pdftotext) and kept in ~/.cache/sdevice_ug.txt. Extended regular expression.
txt=~/.cache/sdevice_ug.txt
if [ ! -s $txt ]; then
  mkdir -p ~/.cache
  root=$(dirname $(dirname $(dirname $(readlink -f $(which sdevice)))))
  pdf=$(find $root -name 'sdevice_ug.pdf' 2>/dev/null | head -1)
  [ -z "$pdf" ] && pdf=$(find $(dirname $root) -name 'sdevice_ug.pdf' 2>/dev/null | head -1)
  [ -z "$pdf" ] && { echo "sdevice_ug.pdf not found under $root"; exit 1; }
  which pdftotext > /dev/null 2>&1 || { echo "no pdftotext; manual at $pdf"; exit 1; }
  pdftotext -layout "$pdf" $txt || exit 1
  echo "converted $pdf"
fi
grep -n -E -A ${2:-8} -B ${3:-2} -- "$1" $txt | cut -c1-200 | head -${MAXL:-120}
