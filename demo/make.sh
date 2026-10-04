#!/bin/sh
# Rebuilds demo/pies.gif. Needs agg (asciinema gif generator), ffmpeg and python3.
set -e

python3 "$(dirname "$0")/demo.py"
