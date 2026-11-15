"""Colour tokens: text on the accent must stay readable (no Anki needed)."""
import importlib.util
import os

ADDON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "addon")
spec = importlib.util.spec_from_file_location("design", os.path.join(ADDON, "design.py"))
design = importlib.util.module_from_spec(spec)
spec.loader.exec_module(design)


def contrast(a, b):
    def lum(c):
        c = c.lstrip("#")
        v = [int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        r, g, b = (x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in v)
        return .2126 * r + .7152 * g + .0722 * b
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + .05) / (lo + .05)


assert design.on_accent("#FFFFFF") == "#14100E"
assert design.on_accent("#000") == "#FFFFFF"
assert design.on_accent("nonsense") == "#FFFFFF"
# every accent of the presets (light and dark) plus extreme colours of one's own
for accent in ("#0071D3", "#4FACFE", "#E95ACC", "#FCABEC", "#619971", "#84CC99", "#7961A9", "#987AD2", "#6183A9",
               "#7FABDC", "#5A9491", "#7CCDC9", "#D97757", "#F0A285", "#FFEB3B", "#101010", "#1A1A40"):
    assert contrast(accent, design.on_accent(accent)) >= 4.5, accent
# petrol keeps its own pair
assert design.tokens(True)["accent"] == "#56BAC6" and design.tokens(False)["on_accent"] == "#FFFFFF"
print("design ok")
