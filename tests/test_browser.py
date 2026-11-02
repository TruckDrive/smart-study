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

sys.modules.setdefault("PyQt6", None)  # the Qt part is optional
adblock = load("browser_adblock")
hosts = adblock.parse_hosts([
    "# comment", "127.0.0.1 localhost", "0.0.0.0 0.0.0.0",
    "0.0.0.0 ads.example.com  # trailing", "0.0.0.0 Tracker.NET other.org", "1.2.3.4 not-blocking.com",
])
assert hosts == {"ads.example.com", "tracker.net", "other.org"}, hosts
assert adblock.is_blocked("ads.example.com", hosts)
assert adblock.is_blocked("x.y.ads.example.com.", hosts)
assert not adblock.is_blocked("example.com", hosts)
assert not adblock.is_blocked("badads.example.com", hosts)
print("ALL TESTS OK")
