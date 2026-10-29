#!/usr/bin/env bash
# Builds dist/smart_study.ankiaddon from addon/ (without personal plans, caches and meta.json).
# Before every release: bump ADDON_VERSION in addon/constants.py and human_version in addon/manifest.json.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/dist"
cd "$ROOT/addon"
python -I - "$ROOT/dist/smart_study.ankiaddon" <<'PY'
import os, sys, zipfile
skip_dirs = {"__pycache__", "user_files"}
files = []
for root, dirs, names in os.walk("."):
    dirs[:] = sorted(d for d in dirs if d not in skip_dirs)
    for n in sorted(names):
        if n == "meta.json" or n.endswith((".pyc", ".tmp")):
            continue
        files.append(os.path.normpath(os.path.join(root, n)))
with zipfile.ZipFile(sys.argv[1], "w", zipfile.ZIP_DEFLATED) as z:
    for f in files:
        z.write(f)
print(f"{sys.argv[1]}: {len(files)} files")
PY
grep -o 'ADDON_VERSION = "[^"]*"' constants.py
