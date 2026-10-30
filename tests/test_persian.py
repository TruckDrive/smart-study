# Persian: every catalogued string is translated, placeholders survive, Anki's repaired file renders.
# Run: python3 -I tests/test_persian.py
import ast
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON = os.path.join(ROOT, "addon")
sys.path.insert(0, ADDON)
import locales  # noqa: E402

spec = importlib.util.spec_from_file_location("anki_persian", os.path.join(ADDON, "anki_persian.py"))
anki_persian = importlib.util.module_from_spec(spec)
spec.loader.exec_module(anki_persian)

fa = locales.PERSIAN_TRANSLATIONS
keys = set()
for catalog in (locales.TRANSLATIONS, locales.WEB_TRANSLATIONS, locales.SUPPLEMENTAL_TRANSLATIONS, locales.WORKSPACE_TRANSLATIONS):
    keys |= set(catalog)
for node in ast.parse(open(os.path.join(ADDON, "web_i18n.py"), encoding="utf-8").read()).body:
    if isinstance(node, ast.AnnAssign) and getattr(node.target, "id", "") == "SURFACE_SOURCES":
        for sources in ast.literal_eval(node.value).values():
            keys |= set(sources)
missing = sorted(k for k in keys if k.strip() and k not in fa)
assert not missing, missing[:10]

placeholder = re.compile(r"\{[^{}\s]*\}|%s|%d")
for source, text in fa.items():
    assert sorted(placeholder.findall(source)) == sorted(placeholder.findall(text)), source

locales.USER_LANG = "fa"
assert locales.is_rtl() and locales._("Settings") == fa["Settings"]
locales.USER_LANG = "de"
assert not locales.is_rtl() and locales._("Settings") != fa["Settings"]

ftl = open(os.path.join(ADDON, "anki_fa.ftl"), encoding="utf-8").read()
assert "\\u{" not in ftl
messages = anki_persian.parse_messages(ftl)
assert messages["actions-add"] == "افزودن"
assert "{" not in anki_persian.render(messages["errors-standard-popup"], {}, messages)
assert "help.ankiweb.net" in anki_persian.render(messages["errors-standard-popup"], {}, messages)
assert "{{" in anki_persian.render('a { "{{" } b', {}, messages)
nested = "{ $a ->\n    [one] x { $b ->\n        [one] y\n       *[other] z\n    }\n   *[other] w\n}"
assert anki_persian.render(nested, {"a": 1, "b": 5}, messages) == "x z"
assert anki_persian.render(nested, {"a": 5, "b": 1}, messages) == "w"
print("ALL TESTS OK")
