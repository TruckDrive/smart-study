# -*- coding: utf-8 -*-
"""Makes Anki's own Persian translation work.

Anki ships a Persian file, but five lines contain ``\\u{202b}``, which is not
valid Fluent syntax. Its backend then rejects the whole file and Anki shows
English with a right-to-left layout. ``anki_fa.ftl`` is the same file with those
lines repaired; it is applied here to Anki's Python windows and web pages. Text
produced inside the backend itself cannot be reached and stays English.

Nothing is changed when Anki's language is not Persian, or once a future Anki
loads its own file correctly.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

_PLACEABLE_VAR = re.compile(r"^\s*\$([\w-]+)\s*$")
_PLACEABLE_STR = re.compile(r'^\s*"((?:[^"\\]|\\.)*)"\s*$')
_PLACEABLE_REF = re.compile(r"^\s*(-?[a-zA-Z][\w-]*)\s*$")
_VARIANT = re.compile(r"^\s*(\*?)\[([^\]]+)\]\s?(.*)$")


def parse_messages(text: str) -> Dict[str, str]:
    """Return message id → raw pattern; comments and blank lines are dropped."""
    messages: Dict[str, List[str]] = {}
    current = None
    for line in text.splitlines():
        if line.startswith("#"):
            current = None
        elif re.match(r"^-?[a-zA-Z][\w-]* =", line):
            key, value = line.split(" =", 1)
            current = messages.setdefault(key, [])
            current.clear()
            current.append(value.strip())
        elif current is not None and line[:1] in (" ", "\t"):
            current.append(line.strip() if not _VARIANT.match(line) else line)
        elif not line.strip():
            continue
        else:
            current = None
    return {key: "\n".join(part for part in lines if part) for key, lines in messages.items()}


def _split(pattern: str) -> List[Tuple[bool, str]]:
    """Split a pattern into (is_placeable, text) parts."""
    parts: List[Tuple[bool, str]] = []
    start = depth = 0
    quoted = False
    for index, char in enumerate(pattern):
        if quoted:
            quoted = char != '"' or pattern[index - 1] == "\\"
        elif char == '"' and depth:
            quoted = True
        elif char == "{":
            if depth == 0:
                parts.append((False, pattern[start:index]))
                start = index + 1
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0:
                parts.append((True, pattern[start:index]))
                start = index + 1
    parts.append((False, pattern[start:]))
    return parts


def _open_placeables(line: str) -> int:
    depth = 0
    quoted = False
    for index, char in enumerate(line):
        if quoted:
            quoted = char != '"' or line[index - 1] == "\\"
        elif char == '"' and depth:
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
    return depth


def _select(body: str, args: Dict[str, Any], messages: Dict[str, str]) -> str:
    head, rest = body.split("->", 1)
    value = args.get(head.strip().lstrip("$"), "")
    variants: List[Tuple[str, bool, List[str]]] = []
    depth = 0
    for line in rest.splitlines():
        match = _VARIANT.match(line) if depth == 0 else None
        if match:
            variants.append((match[2].strip(), bool(match[1]), [match[3]]))
            depth += _open_placeables(match[3])
        elif variants and line.strip():
            variants[-1][2].append(line.strip())
            depth += _open_placeables(line)
    try:
        category = "one" if float(value) in (0, 1) else "other"
    except (TypeError, ValueError):
        category = "other"
    for wanted in (str(value), category):
        for key, _default, lines in variants:
            if key == wanted:
                return render("\n".join(lines), args, messages)
    for _key, default, lines in variants:
        if default:
            return render("\n".join(lines), args, messages)
    return ""


def render(pattern: str, args: Dict[str, Any], messages: Dict[str, str] = {}) -> str:
    out = []
    for is_placeable, text in _split(pattern):
        if not is_placeable:
            out.append(text)
            continue
        literal = _PLACEABLE_STR.match(text)
        variable = _PLACEABLE_VAR.match(text)
        reference = _PLACEABLE_REF.match(text)
        if literal:
            out.append(literal[1])
        elif "->" in text:
            out.append(_select(text, args, messages))
        elif variable:
            out.append(str(args.get(variable[1], "")))
        elif reference:
            out.append(render(messages.get(reference[1], ""), args, messages))
    return "".join(out)


class _ArgumentReader:
    """Stands in for ``self`` so a generated method hands over its Fluent arguments."""

    def _translate(self, _module: int, _message: int, args: dict) -> dict:
        return args


def _patch_translations(messages: Dict[str, str]) -> None:
    from anki._fluent import GeneratedTranslations

    def method(original, pattern: str):
        def translate(self, *args, **kwargs):
            return render(pattern, original(_ArgumentReader(), *args, **kwargs), messages)
        return translate

    for key, pattern in messages.items():
        name = key.replace("-", "_")
        original = getattr(GeneratedTranslations, name, None)
        if original is not None and pattern:
            setattr(GeneratedTranslations, name, method(original, pattern))


def _patch_web_pages(ftl: str) -> None:
    import aqt.mediasrv as mediasrv
    from anki import generic_pb2
    original = mediasrv.post_handlers["i18nResources"]

    def i18n_resources() -> bytes:
        message = generic_pb2.Json()
        message.ParseFromString(original())
        payload = json.loads(message.json)
        payload["langs"] = ["fa"] + payload.get("langs", [])
        payload["resources"] = [ftl] + payload.get("resources", [])
        message.json = json.dumps(payload).encode("utf-8")
        return message.SerializeToString()

    mediasrv.post_handlers["i18nResources"] = i18n_resources


def apply() -> None:
    """Call once while the add-on loads; the main window's menus are redone too."""
    import anki.lang
    if not (anki.lang.current_lang or "").startswith("fa"):
        return
    if anki.lang.tr_legacyglobal.actions_add() != "Add":
        return
    ftl = Path(__file__).with_name("anki_fa.ftl").read_text(encoding="utf-8")
    _patch_translations(parse_messages(ftl))
    _patch_web_pages(ftl)
    from aqt import mw
    if mw is not None and getattr(mw, "form", None) is not None:
        mw.form.retranslateUi(mw)
