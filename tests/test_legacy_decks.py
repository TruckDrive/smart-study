# python -I tests/test_legacy_decks.py <empty folder>  – uses a throwaway collection
import importlib.util
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from anki.collection import Collection  # noqa: E402


def load_ankidata():
    pkg = types.ModuleType("plan")
    pkg.__path__ = [os.path.join(ROOT, "addon", "plan")]
    sys.modules["plan"] = pkg
    spec = importlib.util.spec_from_file_location("plan.ankidata", os.path.join(ROOT, "addon", "plan", "ankidata.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules["plan.ankidata"] = module
    spec.loader.exec_module(module)
    return module


def filtered(col, name):
    did = col.decks.new_filtered(name)
    return did


def main(base):
    ankidata = load_ankidata()
    col = Collection(os.path.join(base, "a.anki2"))
    col.decks.id("Study Plan")
    filtered(col, "Study Plan::Exam · study now")
    col.decks.id("Lernplan")
    filtered(col, "Lernplan::Exam · study now")
    assert ankidata.rename_legacy_decks(col)
    names = sorted(n.name for n in col.decks.all_names_and_ids())
    assert "Study Plan" not in names and "Lernplan" not in names, names
    assert "Smart Study system data::Exam · study now" in names, names
    assert "Smart Study system data::Exam · study now (2)" in names, names
    assert not ankidata.rename_legacy_decks(col), "second run changes nothing"
    print("legacy parents renamed and merged ok")
    col.close()

    col = Collection(os.path.join(base, "b.anki2"))
    did = col.decks.id("Study Plan")
    note = col.new_note(col.models.by_name("Basic"))
    note["Front"] = "x"
    col.add_note(note, did)
    assert not ankidata.rename_legacy_decks(col)
    assert col.decks.id_for_name("Study Plan"), "a user's own deck with cards stays"
    col.decks.id("Lernplan::Normal subdeck")
    assert not ankidata.rename_legacy_decks(col)
    assert col.decks.id_for_name("Lernplan"), "a parent with a normal subdeck stays"
    print("user decks untouched ok")
    col.close()


if __name__ == "__main__":
    main(sys.argv[1])
