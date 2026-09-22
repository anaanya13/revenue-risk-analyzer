#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
if [ ! -x .venv/bin/python ]; then
    echo "The Python environment is missing. Follow 'If setup is missing' in START_HERE.md."
    exit 1
fi
if ! .venv/bin/python -c 'import streamlit, pandas, openpyxl, plotly, duckdb' >/dev/null 2>&1; then
    echo "Some packages are missing. Run: .venv/bin/python -m pip install -r requirements.txt"
    exit 1
fi
echo "Starting your app. Leave this Terminal window open. Press Control+C to stop."
exec .venv/bin/python -m streamlit run app.py --server.address localhost "$@"
