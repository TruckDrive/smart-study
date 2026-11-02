# -*- coding: utf-8 -*-
"""A small filter engine for uBlock Origin / EasyList filter lists. No Qt.

Supported: network filters (``||host^``, URL patterns with ``*``, ``^`` and
``|`` anchors, ``/regex/``), their common options (resource types,
first/third party, ``domain=``, ``important``, ``badfilter``), exception
filters (``@@``, including ``$document`` for whole sites), hosts-file lines,
and element hiding for specific sites (``example.com##.ad``,
``example.com#@#.ad``).  Filters needing uBlock Origin's own machinery
(scriptlets ``##+js``, procedural ``:has-text`` …, redirects, ``removeparam``,
``csp`` …) are skipped, as is generic element hiding (cost on every page).

Like uBlock Origin, URL filters are indexed by one token each, so a request
is only compared with the few filters that share a token with its URL.
"""
from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional, Set, Tuple

_TOKEN = re.compile(r"[a-z0-9%]{2,}")
_HOSTS_LINE = re.compile(r"^(?:0\.0\.0\.0|127\.0\.0\.1)\s+([^\s#]+)")
_PLAIN_HOST = re.compile(r"^\|\|([a-z0-9.\-]+)\^?$")
_IGNORED_HOSTS = {"localhost", "localhost.localdomain", "local", "broadcasthost",
                  "0.0.0.0", "ip6-localhost", "ip6-loopback"}
# Selectors that only uBlock Origin understands, or need a newer CSS engine.
_UBO_PSEUDO = re.compile(
    r":(?:has-text|upward|xpath|matches-(?:css|path|attr|prop|media)|min-text-length|"
    r"watch-attr|remove|style|others|shadow|if|if-not|-abp-|contains|nth-ancestor|spath)\b")

_TYPE_ALIASES = {
    "script": "script", "image": "image", "img": "image", "stylesheet": "stylesheet",
    "css": "stylesheet", "object": "object", "xmlhttprequest": "xhr", "xhr": "xhr",
    "subdocument": "subdocument", "frame": "subdocument", "ping": "ping",
    "beacon": "ping", "websocket": "websocket", "font": "font", "media": "media",
    "other": "other",
}
_IGNORED_OPTIONS = {"match-case", "all", "important"}
_NONE: frozenset = frozenset()


class _Rule:
    __slots__ = ("pattern", "regex", "types", "not_types", "party",
                 "domains", "not_domains", "important")

    def __init__(self, pattern: str):
        self.pattern = pattern          # regex source, compiled on first use
        self.regex = None
        # Shared empty sets until an option fills them: ~40,000 rules.
        self.types = None               # None = every type
        self.not_types = _NONE
        self.party: Optional[str] = None    # "1p", "3p" or None
        self.domains = _NONE
        self.not_domains = _NONE
        self.important = False

    def search(self, url: str) -> bool:
        if self.regex is None:
            try:
                self.regex = re.compile(self.pattern)
            except re.error:
                self.regex = re.compile(r"(?!)")
        return self.regex.search(url) is not None

    def applies(self, rtype: str, third: bool, page_names: Set[str]) -> bool:
        if self.types is not None and rtype not in self.types:
            return False
        if rtype in self.not_types:
            return False
        if self.party == "3p" and not third or self.party == "1p" and third:
            return False
        if self.not_domains and not page_names.isdisjoint(self.not_domains):
            return False
        if self.domains and page_names.isdisjoint(self.domains):
            return False
        return True


def parents(host: str) -> List[str]:
    """www.ads.example.com → itself, ads.example.com, example.com, com."""
    host = host.lower().rstrip(".")
    out = []
    while host:
        out.append(host)
        host = host.partition(".")[2]
    return out


def _with_entities(host: str) -> Set[str]:
    """Parent domains plus "entity" forms used by filters (google.* for google.de)."""
    names = set(parents(host))
    for name in list(names):
        if "." in name:
            names.add(name.rsplit(".", 1)[0] + ".*")
    return names


def site(host: str) -> str:
    """Rough registrable domain, enough to tell first from third party."""
    labels = host.lower().rstrip(".").split(".")
    if len(labels) > 2 and len(labels[-2]) <= 3 and len(labels[-1]) == 2:
        return ".".join(labels[-3:])    # example.co.uk, example.com.au
    return ".".join(labels[-2:])


def _without_badfilter(line: str) -> str:
    """The filter that a "…$badfilter" line switches off."""
    body, _sep, options = line.rpartition("$")
    rest = [o for o in options.split(",") if o.strip() != "badfilter"]
    return body + ("$" + ",".join(rest) if rest else "")


def _pattern_to_regex(text: str) -> str:
    out = []
    if text.startswith("||"):
        out.append(r"^[a-z][a-z0-9+.\-]*://(?:[^/?#]*\.)?")
        text = text[2:]
    elif text.startswith("|"):
        out.append("^")
        text = text[1:]
    end = text.endswith("|")
    if end:
        text = text[:-1]
    for char in text:
        if char == "*":
            out.append(".*")
        elif char == "^":
            out.append(r"(?:[^a-z0-9_\-.%]|$)")
        else:
            out.append(re.escape(char))
    if end:
        out.append("$")
    return "".join(out)


def _best_token(text: str) -> str:
    """The longest token that must appear as a whole token in a matching URL."""
    anchored = text.startswith("|")
    body = text.lstrip("|")
    best = ""
    for match in _TOKEN.finditer(body.rstrip("|")):
        start, end = match.span()
        before = body[start - 1] if start else ("|" if anchored else "")
        after = body[end] if end < len(body) else ("|" if text.endswith("|") else "")
        if before in ("", "*") or after in ("", "*"):
            continue
        if before.isalnum() or before == "%" or after.isalnum() or after == "%":
            continue
        if len(match.group()) > len(best):
            best = match.group()
    return best


class FilterEngine:
    def __init__(self) -> None:
        self.hosts: Set[str] = set()                    # plain ||host^ / hosts files
        self.block: Dict[str, List[_Rule]] = {}         # token → rules
        self.allow: Dict[str, List[_Rule]] = {}
        self.allow_documents: List[_Rule] = []          # @@…$document
        self.hide: Dict[str, Set[str]] = {}             # domain → selectors
        self.unhide: Dict[str, Set[str]] = {}
        self.count = 0

    # ── Loading ───────────────────────────────────────────────────────────

    def add_lists(self, texts: Iterable[str]) -> "FilterEngine":
        lines = [line.strip() for text in texts for line in text.splitlines()]
        bad = {_without_badfilter(line) for line in lines if "badfilter" in line}
        for line in lines:
            if line and line not in bad and "badfilter" not in line:
                self._add(line)
        return self

    def _add(self, line: str) -> None:
        if line[0] == "!" or line[0] == "[":
            return
        hosts_line = _HOSTS_LINE.match(line)
        if hosts_line:
            host = hosts_line.group(1).lower()
            if host not in _IGNORED_HOSTS:
                self.hosts.add(host)
                self.count += 1
            return
        if line[0] == "#" and not line.startswith("##") and not line.startswith("#@#"):
            return  # a comment in hosts files
        for marker in ("#@#", "##"):
            index = line.find(marker)
            if index >= 0:
                self._add_cosmetic(line[:index], line[index + len(marker):], marker == "#@#")
                return
        if "#?#" in line or "#$#" in line or "#@$#" in line or "#@?#" in line:
            return
        self._add_network(line)

    def _add_cosmetic(self, domains: str, selector: str, exception: bool) -> None:
        if not domains or selector[:1] in ("+", "^") or _UBO_PSEUDO.search(selector):
            return  # generic, scriptlet, HTML filter or uBO-only syntax
        names = [d.strip().lower() for d in domains.split(",") if d.strip()]
        if not any(not n.startswith("~") for n in names):
            return
        target = self.unhide if exception else self.hide
        for name in names:
            if name.startswith("~"):
                self.unhide.setdefault(name[1:], set()).add(selector)
            else:
                target.setdefault(name, set()).add(selector)
        self.count += 1

    def _add_network(self, line: str) -> None:
        exception = line.startswith("@@")
        if exception:
            line = line[2:]
        options = ""
        if "$" in line and not (line.startswith("/") and line.endswith("/")):
            line, _sep, options = line.rpartition("$")
            if not line:
                return
        rule_opts = options.split(",") if options else []
        plain = _PLAIN_HOST.match(line)
        if plain and not rule_opts and not exception:
            self.hosts.add(plain.group(1))
            self.count += 1
            return
        if line.startswith("/") and line.endswith("/") and len(line) > 2:
            rule, token = _Rule(line[1:-1]), ""
        else:
            if len(line.strip("*|^")) < 3:
                return  # too broad
            rule, token = _Rule(_pattern_to_regex(line.lower())), _best_token(line.lower())
        document = False
        for option in rule_opts:
            option = option.strip().lower()
            negated = option.startswith("~")
            name, _eq, value = option.lstrip("~").partition("=")
            if name in _TYPE_ALIASES:
                kind = _TYPE_ALIASES[name]
                if negated:
                    rule.not_types = rule.not_types | {kind}
                else:
                    rule.types = (rule.types or _NONE) | {kind}
            elif name in ("third-party", "3p", "strict3p"):
                rule.party = "1p" if negated else "3p"
            elif name in ("first-party", "1p", "strict1p"):
                rule.party = "3p" if negated else "1p"
            elif name in ("domain", "from"):
                names = [d for d in value.split("|") if d]
                rule.not_domains = frozenset(d[1:] for d in names if d.startswith("~")) or _NONE
                rule.domains = frozenset(d for d in names if not d.startswith("~")) or _NONE
            elif name == "important":
                rule.important = True
            elif name in ("document", "doc") and exception:
                document = True
            elif name in ("elemhide", "ehide", "generichide", "ghide", "specifichide", "shide") and exception:
                return  # cosmetic exceptions; generic hiding is not used anyway
            elif name not in _IGNORED_OPTIONS:
                return  # redirect, removeparam, csp, popup, … need uBlock Origin itself
        if not token and not document and not rule.domains:
            # Without a token this filter would be tried on every request of
            # every page; uBlock Origin pays that with its own regex engine.
            return
        self.count += 1
        if document:
            self.allow_documents.append(rule)
        else:
            (self.allow if exception else self.block).setdefault(token, []).append(rule)

    # ── Matching ──────────────────────────────────────────────────────────

    def should_block(self, url: str, host: str, first_host: str, rtype: str) -> bool:
        url = url.lower()
        third = bool(first_host) and site(host) != site(first_host)
        page = _with_entities(first_host) if first_host else set()
        tokens = set(_TOKEN.findall(url))
        tokens.add("")
        blocked = any(name in self.hosts for name in parents(host))
        important = False
        if not blocked:
            rule = self._match(self.block, tokens, url, rtype, third, page)
            if rule is None:
                return False
            important = rule.important
        else:
            important = self._match(self.block, tokens, url, rtype, third, page,
                                    important_only=True) is not None
        if important:
            return True
        if self._match(self.allow, tokens, url, rtype, third, page) is not None:
            return False
        return not self.document_allowed(first_host)

    def document_allowed(self, first_host: str) -> bool:
        if not first_host or not self.allow_documents:
            return False
        page = "https://" + first_host + "/"
        return any(rule.search(page) for rule in self.allow_documents)

    @staticmethod
    def _match(index, tokens, url, rtype, third, page, important_only=False):
        for token in tokens:
            for rule in index.get(token, ()):
                if important_only and not rule.important:
                    continue
                if rule.applies(rtype, third, page) and rule.search(url):
                    return rule
        return None

    def css_for(self, host: str) -> str:
        """Element-hiding style sheet for a page on this host."""
        names = _with_entities(host)
        selectors: Set[str] = set()
        for name in names:
            selectors |= self.hide.get(name, set())
        for name in names:
            selectors -= self.unhide.get(name, set())
        # One rule per selector: an invalid selector then costs only itself.
        return "\n".join(sorted(s + "{display:none!important}" for s in selectors))

