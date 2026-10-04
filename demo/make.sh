#!/bin/sh
# Rebuilds demo/pie.gif. Needs agg (asciinema gif generator), ffmpeg and python3.
set -e

python3 "$(dirname "$0")/demo.py"
