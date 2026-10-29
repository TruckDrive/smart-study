# python -I tests/test_addon_sync.py  – the add-on list logic, without Anki
import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("addon_sync", os.path.join(ROOT, "addon", "addon_sync.py"))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def main():
    pc = {"111": "Image Occlusion", "222": "Hierarchical Tags"}
    shared = sync.merge({}, pc, [])
    assert shared == pc
    laptop = {"333": "Speed Focus"}
    shared = sync.merge(shared, laptop, [])
    assert shared == {"111": "Image Occlusion", "222": "Hierarchical Tags", "333": "Speed Focus"}
    print("both devices add their add-ons ok")

    assert sync.missing(shared, laptop, []) == {"111": "Image Occlusion", "222": "Hierarchical Tags"}
    assert sync.missing(shared, laptop, ["222"]) == {"111": "Image Occlusion"}, "skipped add-ons are not offered"
    assert sync.missing({"1726163334": "Smart Study"}, [], []) == {}, "Smart Study itself is never offered"
    print("missing add-ons offered, skipped ones not ok")

    shared = sync.merge(shared, {"111": "Image Occlusion"}, known=list(pc))
    assert "222" not in shared, "removed on the pc, so removed from the list"
    assert "333" in shared, "the laptop's add-on stays: the pc never had it"
    print("an uninstalled add-on leaves the list ok")

    assert sync.valid_code(" 1084228676 ") == "1084228676"
    assert sync.valid_code("abc") is None and sync.valid_code("") is None and sync.valid_code("1" * 20) is None
    print("code check ok")


if __name__ == "__main__":
    main()
