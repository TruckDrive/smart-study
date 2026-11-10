# Where the PDFs of a plan are on *this* device.
#
# A plan travels to every device with the AnkiWeb sync, but a path like
# /home/me/Desktop/Book.pdf only exists on the computer where it was chosen.
# So each device keeps its own paths in user_files/file_paths.json (never
# synced), and the synced plan only carries the file's name and size. When a
# path is missing, the file is looked for by name (first next to the plan's
# other PDFs, then in the home folder); if that fails, the plan asks the user.
import json
import os
import re
import time

from . import store

LOCAL = os.path.join(store.DIR, "file_paths.json")  # {plan id: {source id: path}}
SKIP_DIRS = {"node_modules", "__pycache__", "site-packages", "AppData", "Library", "snap", "venv", ".venv"}
MAX_DEPTH = 6
MAX_SECONDS = 3.0


def _load():
    try:
        with open(LOCAL, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(data):
    os.makedirs(os.path.dirname(LOCAL), exist_ok=True)
    tmp = LOCAL + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    os.replace(tmp, LOCAL)


def base_name(path):
    """File name of a path from any system (a Windows path read on Linux too)."""
    return re.split(r"[\\/]", str(path or "").strip())[-1]


def _ok(path):
    return bool(path) and os.path.isfile(os.path.expanduser(path))


def _size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return None


def describe(src, path):
    """Stores name and size in the (synced) source, so other devices can find the file."""
    src["fileName"] = base_name(path)
    size = _size(path)
    if size:
        src["fileSize"] = size


def remember(pid, sid, path):
    path = os.path.abspath(os.path.expanduser(path))
    data = _load()
    if data.get(pid, {}).get(sid) != path:
        data.setdefault(pid, {})[sid] = path
        _save(data)


def local(pid):
    """{source id: path} remembered on this device."""
    return dict(_load().get(pid) or {})


def known(plan, src):
    """The path on this device without searching, or ''."""
    for p in (local(plan["id"]).get(src["id"]), src.get("file")):
        if _ok(p):
            return os.path.expanduser(p)
    return ""


def _roots(plan):
    """Folders to search first: around the plan's other PDFs on this device."""
    out = []
    for p in local(plan["id"]).values():
        d = os.path.dirname(os.path.expanduser(p))
        for _ in range(2):  # the folder itself and its parent (e.g. "Course/1 Book/x.pdf")
            if d and os.path.isdir(d) and d not in out:
                out.append(d)
            d = os.path.dirname(d)
    home = os.path.expanduser("~")
    if home not in out:
        out.append(home)
    return out


def search(name, size=None, roots=(), deadline=None):
    """Looks for a file by name (case-insensitive) below *roots*. With several
    matches, the one with the same size wins, else the newest."""
    want = name.lower()
    deadline = deadline or time.monotonic() + MAX_SECONDS
    found, seen = [], set()
    for root in roots:
        base_depth = root.rstrip(os.sep).count(os.sep)
        for cur, dirs, names in os.walk(root):
            if time.monotonic() > deadline:
                break
            real = os.path.realpath(cur)
            if real in seen:
                dirs[:] = []
                continue
            seen.add(real)
            if cur.count(os.sep) - base_depth >= MAX_DEPTH:
                dirs[:] = []
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in SKIP_DIRS]
            for n in names:
                if n.lower() == want:
                    found.append(os.path.join(cur, n))
        if found:
            break
    if not found:
        return ""
    if size:
        same = [p for p in found if _size(p) == size]
        if same:
            found = same
    return max(found, key=lambda p: os.path.getmtime(p) if os.path.exists(p) else 0)


def resolve(plan, src):
    """Path of the source's PDF on this device: remembered, the plan's own path,
    or found by name. Remembers what it found. '' if nothing."""
    path = known(plan, src)
    if not path:
        name = src.get("fileName") or base_name(src.get("file"))
        if name:
            path = search(name, src.get("fileSize"), _roots(plan))
    if path:
        remember(plan["id"], src["id"], path)
    return path


def update_sources(plan):
    """After the user edited the sources: remember the chosen paths here and
    describe the files for the other devices. Returns True if the plan changed."""
    changed = False
    for src in plan.get("sources") or []:
        if src.get("type") != "pages" or not _ok(src.get("file")):
            continue
        path = os.path.expanduser(src["file"])
        remember(plan["id"], src["id"], path)
        before = (src.get("fileName"), src.get("fileSize"))
        describe(src, path)
        changed |= before != (src.get("fileName"), src.get("fileSize"))
    return changed
