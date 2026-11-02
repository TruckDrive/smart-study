"""Search engines and the ad-block list of the Smart Study browser (no Anki needed)."""
import importlib.util
import os
import sys

ADDON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "addon")


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ADDON, name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


search = load("browser_search")
assert search.home_url(None) == "https://duckduckgo.com/"
assert search.home_url("nonsense") == "https://duckduckgo.com/"
assert search.search_url("google", "Plexus brachialis") == "https://www.google.com/search?q=Plexus+brachialis"
assert search.search_url("brave", "a&b") == "https://search.brave.com/search?q=a%26b"
assert search.search_url("startpage", "x") == "https://www.startpage.com/sp/search?query=x"

engine_module = load("adblock_engine")
engine = engine_module.FilterEngine().add_lists(["""
! comment
0.0.0.0 hosts-file.example
||ads.example.com^
||tracker.net^$third-party
||cdn.example.org/ads/*$script,domain=news.com|~sub.news.com
/banner/*/img^
@@||cdn.example.org/ads/allowed.js
||important.example^$important
@@||important.example^
||broken.example^
||broken.example^$badfilter
@@||trusted.org^$document
news.com,google.*##.ad-slot
news.com#@#.ad-slot
~other.com,shop.com##.sponsor
youtube.com##+js(json-prune, adPlacements)
example.com##div:has-text(Ad)
"""])
block = engine.should_block
assert block("https://ads.example.com/x.js", "ads.example.com", "site.com", "script")
assert block("https://x.ads.example.com/x.js", "x.ads.example.com", "site.com", "script")
assert block("http://hosts-file.example/a", "hosts-file.example", "site.com", "image")
assert not block("https://badads.example.com/x.js", "badads.example.com", "site.com", "script")
assert block("https://tracker.net/t.gif", "tracker.net", "site.com", "image")
assert not block("https://tracker.net/t.gif", "tracker.net", "www.tracker.net", "image"), "first party"
assert block("https://cdn.example.org/ads/a.js", "cdn.example.org", "www.news.com", "script")
assert not block("https://cdn.example.org/ads/a.js", "cdn.example.org", "sub.news.com", "script")
assert not block("https://cdn.example.org/ads/a.js", "cdn.example.org", "www.news.com", "image")
assert not block("https://cdn.example.org/ads/a.js", "cdn.example.org", "other.com", "script")
assert not block("https://cdn.example.org/ads/allowed.js", "cdn.example.org", "news.com", "script")
assert block("https://site.com/banner/top/img?id=1", "site.com", "site.com", "image")
assert not block("https://site.com/banners/top/img?id=1", "site.com", "site.com", "image")
assert block("https://important.example/a", "important.example", "site.com", "script")
assert not block("https://broken.example/a", "broken.example", "site.com", "script"), "badfilter"
assert not block("https://ads.example.com/x.js", "ads.example.com", "www.trusted.org", "script"), "$document"
assert engine.css_for("www.google.de") == ".ad-slot{display:none!important}"
assert engine.css_for("news.com") == ""
assert engine.css_for("shop.com") == ".sponsor{display:none!important}"
assert engine.css_for("youtube.com") == "" and engine.css_for("example.com") == ""
print("ALL TESTS OK")
