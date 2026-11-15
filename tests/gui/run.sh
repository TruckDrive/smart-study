#!/usr/bin/env bash
# GUI smoke test: starts Anki without a window (offscreen) in a throwaway
# profile with the add-on from addon/ and checks what unit tests cannot see:
# the rail, the settings page, the study plan page and the focus mode.
#
#   tests/gui/run.sh [output folder]      needs Anki installed (python3 -c "import aqt")
#
# Your own Anki profile is never touched: the test uses its own base folder and
# its own instance key, so it also runs while your Anki is open.
# Exit code 0 = every check passed. Screenshots and run.log are in the output folder.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
OUT="${1:-$(mktemp -d)}"
BASE="$(mktemp -d)/base"
mkdir -p "$OUT" "$BASE/addons21"
cp -a "$ROOT/addon" "$BASE/addons21/smart_study_test"
find "$BASE/addons21/smart_study_test" -name __pycache__ -prune -exec rm -rf {} +
rm -rf "$BASE/addons21/smart_study_test/user_files" "$BASE/addons21/smart_study_test/plan/user_files" "$BASE/addons21/smart_study_test/meta.json"
cp -a "$HERE/helper" "$BASE/addons21/zz_smoke_helper"
# Past the setup wizard and the "What's new" window.
VERSION="$(grep -o 'ADDON_VERSION = "[^"]*"' "$ROOT/addon/constants.py" | cut -d'"' -f2)"
printf '{"onboarding_completed": true, "last_seen_version": "%s", "addon_sync_asked": true}\n' "$VERSION" \
  > "$BASE/addons21/smart_study_test/addon_settings.json"
mkdir -p "$BASE/addons21/smart_study_test/user_files/integrations"
echo '{"enabled": {}, "choice": {}, "suggested_after_unbundle": true}' > "$BASE/addons21/smart_study_test/user_files/integrations/state.json"

ANKI_SINGLE_INSTANCE_KEY="smart-study-smoke-$$" QT_QPA_PLATFORM=offscreen ANKI_WAYLAND=1 SS_SHOTS="$OUT" \
  timeout -k 3 "${SS_TIMEOUT:-170}" python3 "$HERE/launch.py" -b "$BASE" -l en > "$OUT/run.log" 2>&1

grep -E '^CHECK' "$OUT/run.log"
fail=0
grep -q '^SMOKE DONE' "$OUT/run.log" || { echo "FAIL: the run did not finish (see $OUT/run.log)"; fail=1; }
grep -q '^CHECK FAIL' "$OUT/run.log" && fail=1
if grep -E '^Traceback|^Smart Study: ignored' "$OUT/run.log"; then echo "FAIL: errors in $OUT/run.log"; fail=1; fi
[ $fail -eq 0 ] && echo "GUI smoke test passed ($OUT)" || echo "GUI smoke test FAILED ($OUT)"
exit $fail
