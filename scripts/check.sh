#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
if [ ! -x .venv/bin/python ]; then
    echo "The Python environment is missing. Follow START_HERE.md."
    exit 1
fi
exec .venv/bin/python -m unittest discover -s tests -v
