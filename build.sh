#!/usr/bin/env bash
# Baut dist/lernplan.ankiaddon aus addon/ (ohne persönliche Pläne und meta.json).
# Vor jedem Release: VERSION in addon/__init__.py hochzählen.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/dist"
cd "$ROOT/addon"
python -I - "$ROOT/dist/lernplan.ankiaddon" <<'PY'
import glob, sys, zipfile
files = sorted(glob.glob("*.py") + glob.glob("web/*"))
with zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(f)
print(f"{sys.argv[1]}: {len(files)} Dateien")
PY
grep -o 'VERSION = "[^"]*"' __init__.py
