# python -I tests/test_suggested.py  – which former built-in add-ons are suggested after the update, without Anki
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("suggested", os.path.join(ROOT, "addon", "integrations", "suggested.py"))
sg = importlib.util.module_from_spec(spec)
sys.modules["suggested"] = sg  # dataclasses look the module up
spec.loader.exec_module(sg)


def main():
    assert [s.key for s in sg.SUGGESTED] == ["heatmap", "lifedrain"]
    assert sg.SUGGESTED_BY_KEY["heatmap"].url == "https://ankiweb.net/shared/info/1771074083"
    assert sg.SUGGESTED_BY_KEY["lifedrain"].code == "715575551"
    print("suggestions and AnkiWeb pages ok")

    # Never switched: the heatmap was on by default, Life Drain off.
    assert sg.to_offer({}, {}) == [("heatmap", "install")]
    assert sg.to_offer({"enabled": {}, "choice": {}}, {"contanki": True}) == [("heatmap", "install")]
    assert sg.to_offer({"enabled": {"heatmap": False, "lifedrain": True}}, {}) == [("lifedrain", "install")]
    assert sg.to_offer({"enabled": {"heatmap": True, "lifedrain": True}}, {}) == [("heatmap", "install"), ("lifedrain", "install")]
    assert sg.to_offer({"enabled": "broken"}, {}) == [("heatmap", "install")], "damaged state does not raise"
    print("built-in copies that were on are offered ok")

    # A separately installed copy (any known folder name) means nothing to install.
    assert sg.to_offer({}, {"1771074083": True}) == []
    assert sg.to_offer({}, {"review_heatmap": True}) == []
    assert sg.to_offer({"enabled": {"lifedrain": True}}, {"723520343": True, "anki-lifedrain": True}) == []
    # Switched off when the user chose the built-in copy: offered to switch it back on.
    assert sg.to_offer({}, {"1771074083": False}) == [("heatmap", "enable")]
    assert sg.to_offer({}, {"1771074083": False, "review_heatmap": True}) == [], "an enabled copy wins"
    print("installed copies are respected ok")

    # Asked once per device.
    assert sg.to_offer({sg.ASKED_KEY: True}, {}) == []
    assert sg.startup_plan({sg.ASKED_KEY: True}, {}, True, False) == ([], False)
    print("never asked twice ok")

    # New users (setup wizard on this start) are never asked, but remembered.
    assert sg.startup_plan({}, {}, onboarded=False, first_start=True) == ([], True)
    assert sg.startup_plan({}, {}, onboarded=True, first_start=True) == ([], True)
    # A profile that did not finish the setup: not now, not remembered.
    assert sg.startup_plan({}, {}, onboarded=False, first_start=False) == ([], False)
    # Updating user: offered; nothing to offer counts as done.
    assert sg.startup_plan({}, {}, onboarded=True, first_start=False) == ([("heatmap", "install")], False)
    assert sg.startup_plan({"enabled": {"heatmap": False}}, {}, True, False) == ([], True)
    print("startup plan ok")

    # The installed-copy check reports the folder and whether it is on.
    hm = sg.SUGGESTED_BY_KEY["heatmap"]
    assert sg.installed_copy(hm, {}) is None
    assert sg.installed_copy(hm, {"review-heatmap": False}) == ("review-heatmap", False)
    assert sg.installed_copy(hm, {"review-heatmap": False, "1771074083": True}) == ("1771074083", True)
    print("installed copy ok")


if __name__ == "__main__":
    main()
