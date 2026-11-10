# python -I tests/test_files.py <empty folder>  – two "devices" with their own home folders, never your real files
import importlib
import os
import shutil
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def device(name, base):
    """A copy of the plan package with its own user_files, as on a second computer."""
    folder = os.path.join(base, name, "addon")
    shutil.copytree(os.path.join(ROOT, "addon", "plan"), folder, ignore=shutil.ignore_patterns("__pycache__", "user_files"))
    pkg = types.ModuleType(name)
    pkg.__path__ = [folder]
    sys.modules[name] = pkg
    return importlib.import_module(name + ".files")


def write(path, data=b"%PDF-1.4 test"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)
    return path


def test(base):
    sys.modules["aqt"] = types.SimpleNamespace(mw=None)  # no collection: store works on files only
    pc, laptop = device("pc", base), device("laptop", base)
    home_pc, home_laptop = os.path.join(base, "home_pc"), os.path.join(base, "home_laptop")

    os.environ["HOME"] = home_pc
    book = write(os.path.join(home_pc, "Desktop", "Handbuch.pdf"))
    plan = {"id": "p1", "sources": [{"id": "hb", "type": "pages", "file": book},
                                    {"id": "g", "type": "pages", "file": os.path.join(home_pc, "Downloads", "Gelenke.pdf")}]}
    assert pc.update_sources(plan), "name and size are added for the other devices"
    assert plan["sources"][0]["fileName"] == "Handbuch.pdf" and plan["sources"][0]["fileSize"] > 0
    assert pc.resolve(plan, plan["sources"][0]) == book
    print("path on the device where it was chosen ok")

    # moved into a course folder: found by name, remembered
    moved = os.path.join(home_pc, "Desktop", "Kurs", "1 Buch", "Handbuch.pdf")
    os.makedirs(os.path.dirname(moved))
    os.replace(book, moved)
    assert pc.resolve(plan, plan["sources"][0]) == moved
    assert pc.local("p1")["hb"] == moved
    print("moved file found by name ok")

    # Gelenke.pdf lies next to it now: the search starts around the known PDFs
    g = write(os.path.join(home_pc, "Desktop", "Kurs", "3 Gelenke", "gelenke.PDF"))
    assert pc.resolve(plan, plan["sources"][1]) == g
    print("second file found next to the first, any case ok")

    # the synced plan on the laptop: other home, Windows-style path from elsewhere
    os.environ["HOME"] = home_laptop
    lap_book = write(os.path.join(home_laptop, "Documents", "Uni", "Handbuch.pdf"))
    write(os.path.join(home_laptop, "Old", "Handbuch.pdf"), b"other version, other size")
    src = dict(plan["sources"][0], file="C:\\Users\\me\\Desktop\\Handbuch.pdf")
    assert laptop.resolve(plan, src) == lap_book, "same size wins over another file with that name"
    assert laptop.local("p1") == {"hb": lap_book}
    print("other device finds its own copy ok")

    # nothing there: empty, so the plan asks
    assert laptop.resolve(plan, {"id": "x", "type": "pages", "file": "/nowhere/Missing.pdf"}) == ""
    print("missing file gives '' (the plan asks) ok")

    os.environ["HOME"] = home_pc
    assert pc.local("p1")["hb"] == moved, "each device keeps its own paths"
    print("devices keep separate paths ok")


if __name__ == "__main__":
    test(sys.argv[1])
    print("all ok")
