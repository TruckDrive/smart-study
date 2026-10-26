#!/usr/bin/env bash
# Builds dist/smart_study_plan.ankiaddon from addon/ (without personal plans and meta.json).
# Before every release: bump VERSION in addon/__init__.py.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/dist"
cd "$ROOT/addon"
python -I - "$ROOT/dist/smart_study_plan.ankiaddon" <<'PY'
import glob, json, sys, zipfile
files = sorted(glob.glob("*.py") + glob.glob("web/*"))
with zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(f)
    # used when installing from the file (AnkiWeb ignores it)
    z.writestr("manifest.json", json.dumps({"package": "smart_study_plan", "name": "Smart Study Plan"}))
print(f"{sys.argv[1]}: {len(files)} files")
PY
grep -o 'VERSION = "[^"]*"' __init__.py
