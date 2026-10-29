#!/usr/bin/env bash
# Builds dist/smart_study.ankiaddon from addon/ (without personal plans, caches and meta.json).
# Before every release: bump ADDON_VERSION in addon/constants.py and human_version in addon/manifest.json.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/dist"
cd "$ROOT/addon"
python -I - "$ROOT/dist/smart_study.ankiaddon" <<'PY'
import os, sys, zipfile
# Personal data lives in these user_files folders; theme/user_files holds the
# bundled theme CSS and must be shipped.
skip_paths = {"./user_files", "./plan/user_files"}
files = []
for root, dirs, names in os.walk("."):
    dirs[:] = sorted(d for d in dirs if d != "__pycache__" and os.path.join(root, d) not in skip_paths)
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
