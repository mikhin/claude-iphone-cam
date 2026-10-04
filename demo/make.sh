#!/bin/sh
# Rebuilds demo/demo.gif from drawn frames. Needs agg (asciinema gif generator) and python3.
set -e

root=$(cd "$(dirname "$0")/.." && pwd)

python3 "$root/demo/demo.py" "$root/demo/demo.cast"

agg \
  --font-size 20 \
  --theme 1e1e2e,cdd6f4,45475a,f38ba8,a6e3a1,f9e2af,89b4fa,f5c2e7,94e2d5,bac2de,585b70,f38ba8,a6e3a1,f9e2af,89b4fa,f5c2e7,94e2d5,a6adc8 \
  --idle-time-limit 4 \
  "$root/demo/demo.cast" "$root/demo.gif"

rm -f "$root/demo/demo.cast"

echo "demo.gif"
