# python -I tests/test_history.py <empty folder>  – address-field suggestions, no Anki needed
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("browser_history", os.path.join(ROOT, "addon", "browser_history.py"))
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)

base = sys.argv[1]
H.set_folder(base)
now = 1_800_000_000.0
for _ in range(12):
    H.add("https://www.youtube.com/", "YouTube", now - 3600)
H.add("https://www.youtube.com/watch?v=abc", "Herz Anatomie – YouTube", now - 100)
H.add("https://moodle.example.ac.at/course/view.php?id=5", "PT EuL Kurs", now - 86400 * 20)
H.add("https://de.wikipedia.org/wiki/Herz", "Herz – Wikipedia", now - 86400)
H.add("file:///home/me/x.pdf")
H.add("about:blank")
H.add("https://x.example/" + "a" * 3000)
assert len(H._load()) == 4, "only web pages of a sane length are kept"

urls = lambda text, **k: [s["url"] for s in H.suggest(text, now=now, **k)]
assert urls("yo") == ["https://www.youtube.com/", "https://www.youtube.com/watch?v=abc"], "the site before its sub-page"
assert urls("https://www.yo")[0] == "https://www.youtube.com/", "typing the scheme does not matter"
assert urls("herz")[0] == "https://de.wikipedia.org/wiki/Herz", "in the address beats in the title"
assert urls("wiki herz") == ["https://de.wikipedia.org/wiki/Herz"], "every word has to match"
assert urls("   ") == [] and urls("zzz") == []
assert urls("kurs") == ["https://moodle.example.ac.at/course/view.php?id=5"], "found by its title"
fav = [{"url": "https://moodle.org", "title": "Moodle"}, {"url": "file:///x", "title": "no"}]
assert urls("moo", extra=fav)[0] == "https://moodle.org", "favourites and open tabs join in"
assert urls("moo", extra=fav, history=False) == ["https://moodle.org"], "history off: nothing from the history"
assert len(urls("e", limit=2)) == 2
print("ranking ok")

H.save()
H.set_folder(None)
H.set_folder(base)
assert len(H._load()) == 4, "survives a restart"
for i in range(H.MAX_ENTRIES + 20):
    H.add(f"https://site{i}.example/", "", now + i)
assert len(H._load()) <= H.MAX_ENTRIES and "https://www.youtube.com/" not in H._load(), "the oldest are forgotten"
H.set_folder(None)  # saves what is open
with open(os.path.join(base, "browser_history.json"), "w", encoding="utf-8") as f:
    f.write("{broken")
H.set_folder(base)
assert H._load() == {}, "a damaged file starts an empty history"
H.add("https://a.example/", "A", now)
H.clear()
assert H._load() == {} and os.path.getsize(os.path.join(base, "browser_history.json")) < 5
print("storage ok")

assert H.short("https://www.youtube.com/") == "youtube.com" and H.short("http://a.b/c/") == "a.b/c/"
assert H.icon_path("https://de.wikipedia.org/wiki/Herz").endswith(os.path.join("favicons", "de.wikipedia.org.png"))
assert H.icon_path("https://ex ample/") is None and H.icon_path("notaurl") is None
assert os.path.dirname(H.icon_path("https://a.b/../../etc/passwd")) == os.path.join(base, "favicons"), "an address cannot leave the folder"
print("ALL TESTS OK")
