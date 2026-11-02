"""Search engines for the Smart Study browser. Pure helpers, no Qt."""
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
