"""Search engines for the Smart Study browser. Pure helpers, no Qt."""
import os
import re
from pathlib import Path
from urllib.parse import urlencode

DEFAULT_ENGINE = "duckduckgo"

# key: (name, home page, search URL without the query, query parameter)
ENGINES = {
    "duckduckgo": ("DuckDuckGo", "https://duckduckgo.com/", "https://duckduckgo.com/", "q"),
    "google": ("Google", "https://www.google.com/", "https://www.google.com/search", "q"),
    "brave": ("Brave Search", "https://search.brave.com/", "https://search.brave.com/search", "q"),
    "startpage": ("Startpage", "https://www.startpage.com/", "https://www.startpage.com/sp/search", "query"),
    "ecosia": ("Ecosia", "https://www.ecosia.org/", "https://www.ecosia.org/search", "q"),
    "bing": ("Bing", "https://www.bing.com/", "https://www.bing.com/search", "q"),
}


def engine_key(key):
    return key if key in ENGINES else DEFAULT_ENGINE


def home_url(key):
    return ENGINES[engine_key(key)][1]


def search_url(key, text):
    _name, _home, base, param = ENGINES[engine_key(key)]
    return base + "?" + urlencode({param: text})


_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)
_HOST = re.compile(r"^(localhost|\d{1,3}(\.\d{1,3}){3}|[^\s/:?#]+\.[a-z]{2,63})(:\d{1,5})?([/?#]\S*)?$", re.I)


def address_target(text, key):
    """What the address bar opens for *text*: a web address, a local PDF
    (path or file:// link) or a search with the chosen engine."""
    text = (text or "").strip()
    if not text:
        return ""
    if _SCHEME.match(text):
        return text
    if text.startswith(("~", "/", "\\")) or re.match(r"^[a-z]:[\\/]", text, re.I):
        path = os.path.expanduser(text)
        if path.lower().endswith(".pdf") and os.path.isfile(path):
            return Path(path).resolve().as_uri()
    if " " not in text and _HOST.match(text):
        return ("http://" if text.lower().startswith("localhost") else "https://") + text
    return search_url(key, text)
