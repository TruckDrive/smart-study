"""Saved passwords for the Smart Study browser.

When a login form is sent, the browser offers to remember the user name and
password for that site. Next time the login page opens, both fields are filled
in – the user still clicks "Log in" themselves (nothing is sent automatically).

Passwords never land in the add-on's files: they live in the system keyring –
Linux: Secret Service via `secret-tool` (KWallet, GNOME Keyring, KeePassXC …),
macOS: the login keychain, Windows: the Credential Manager. Without one the
feature stays off.

The page scripts run in an isolated JavaScript world, so the site's own
scripts cannot see or call them.
"""
from __future__ import annotations

import json
import secrets
import shutil
import subprocess
import sys
from typing import Dict, Optional, Tuple

from aqt import mw
from aqt.qt import QMessageBox, QTimer

try:
    from PyQt6.QtWebEngineCore import QWebEngineScript
    _WORLD = QWebEngineScript.ScriptWorldId.ApplicationWorld
except Exception:  # pragma: no cover
    _WORLD = 1

try:
    from .locales import _
except ImportError:  # pragma: no cover
    def _(text):  # type: ignore
        return text

APP = "smart-study"
_NONCE = "ss-pw-" + secrets.token_hex(12) + ":"
_cache: Dict[str, Optional[Tuple[str, str]]] = {}  # host → (user, password) / None
_asking: set = set()


def _ws():
    from . import website_sidebar
    return website_sidebar


def available() -> bool:
    if sys.platform.startswith("win"):
        return True
    if sys.platform == "darwin":
        return shutil.which("security") is not None
    return shutil.which("secret-tool") is not None


def _state() -> Dict:
    value = _ws()._load_website_state().get("passwords")
    return value if isinstance(value, dict) else {}


def _save_state(value: Dict) -> None:
    ws = _ws()
    state = ws._load_website_state()
    state["passwords"] = value
    ws._save_website_state(state)


def enabled() -> bool:
    return available() and _state().get("enabled", True)


def set_enabled(on: bool) -> None:
    value = _state()
    value["enabled"] = bool(on)
    _save_state(value)


def _never(host: str) -> bool:
    return host in (_state().get("never") or [])


def _add_never(host: str) -> None:
    value = _state()
    never = [h for h in (value.get("never") or []) if h != host]
    value["never"] = never + [host]
    _save_state(value)


# ── System keyring ────────────────────────────────────────────────────────
# Linux: Secret Service via secret-tool (KWallet, GNOME Keyring, KeePassXC …)
# macOS: login keychain via `security`
# Windows: Credential Manager via advapi32
# The secret is {"u": user, "p": password} as JSON, one entry per host.

def _decode(text: str) -> Optional[Tuple[str, str]]:
    try:
        data = json.loads(text)
        return str(data.get("u", "")), str(data["p"])
    except Exception:
        return None


def _run(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, timeout=60, **kw)


class _WinCred:
    """Windows Credential Manager (generic credentials named smart-study:<host>)."""

    def __init__(self):
        import ctypes
        from ctypes import wintypes
        self.ctypes = ctypes

        class CREDENTIAL(ctypes.Structure):
            _fields_ = [("Flags", wintypes.DWORD), ("Type", wintypes.DWORD),
                        ("TargetName", wintypes.LPWSTR), ("Comment", wintypes.LPWSTR),
                        ("LastWritten", wintypes.FILETIME), ("CredentialBlobSize", wintypes.DWORD),
                        ("CredentialBlob", ctypes.POINTER(ctypes.c_ubyte)), ("Persist", wintypes.DWORD),
                        ("AttributeCount", wintypes.DWORD), ("Attributes", ctypes.c_void_p),
                        ("TargetAlias", wintypes.LPWSTR), ("UserName", wintypes.LPWSTR)]
        self.CREDENTIAL = CREDENTIAL
        self.api = ctypes.WinDLL("advapi32", use_last_error=True)
        self.api.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                                       ctypes.POINTER(ctypes.POINTER(CREDENTIAL))]
        self.api.CredWriteW.argtypes = [ctypes.POINTER(CREDENTIAL), wintypes.DWORD]
        self.api.CredDeleteW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
        self.api.CredEnumerateW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
                                            ctypes.POINTER(ctypes.POINTER(ctypes.POINTER(CREDENTIAL)))]
        self.api.CredFree.argtypes = [ctypes.c_void_p]

    def read(self, target):
        ctypes = self.ctypes
        pcred = ctypes.POINTER(self.CREDENTIAL)()
        if not self.api.CredReadW(target, 1, 0, ctypes.byref(pcred)):
            return None
        try:
            cred = pcred.contents
            return ctypes.string_at(cred.CredentialBlob, cred.CredentialBlobSize).decode("utf-8")
        finally:
            self.api.CredFree(pcred)

    def write(self, target, secret):
        ctypes = self.ctypes
        blob = secret.encode("utf-8")
        buf = (ctypes.c_ubyte * len(blob)).from_buffer_copy(blob)
        cred = self.CREDENTIAL()
        cred.Type = 1  # CRED_TYPE_GENERIC
        cred.TargetName = target
        cred.CredentialBlobSize = len(blob)
        cred.CredentialBlob = ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte))
        cred.Persist = 2  # CRED_PERSIST_LOCAL_MACHINE
        cred.UserName = "Smart Study"
        return bool(self.api.CredWriteW(ctypes.byref(cred), 0))

    def delete(self, target):
        self.api.CredDeleteW(target, 1, 0)

    def delete_all(self, prefix):
        ctypes = self.ctypes
        from ctypes import wintypes
        count = wintypes.DWORD()
        creds = ctypes.POINTER(ctypes.POINTER(self.CREDENTIAL))()
        if not self.api.CredEnumerateW(prefix + "*", 0, ctypes.byref(count), ctypes.byref(creds)):
            return
        try:
            names = [creds[i].contents.TargetName for i in range(count.value)]
        finally:
            self.api.CredFree(creds)
        for name in names:
            self.delete(name)


def _lookup(host: str) -> Optional[Tuple[str, str]]:
    try:
        if sys.platform.startswith("win"):
            text = _WinCred().read(f"{APP}:{host}")
            return _decode(text) if text else None
        if sys.platform == "darwin":
            out = _run(["security", "find-generic-password", "-s", APP, "-a", host, "-w"])
        else:
            out = _run(["secret-tool", "lookup", "app", APP, "host", host])
    except Exception as e:
        print(f"Smart Study passwords: keyring not reached: {e}")
        return None
    if out.returncode != 0 or not out.stdout:
        return None
    return _decode(out.stdout.strip())


def _store(host: str, user: str, password: str) -> bool:
    secret = json.dumps({"u": user, "p": password})
    try:
        if sys.platform.startswith("win"):
            return _WinCred().write(f"{APP}:{host}", secret)
        if sys.platform == "darwin":
            # -U updates an existing entry. The secret is passed as an argument
            # (the only way `security` takes it), visible to `ps` for a moment.
            return _run(["security", "add-generic-password", "-U", "-s", APP, "-a", host,
                         "-l", f"Smart Study: {host}", "-w", secret]).returncode == 0
        _run(["secret-tool", "clear", "app", APP, "host", host])
        return _run(["secret-tool", "store", f"--label=Smart Study: {host}", "app", APP, "host", host],
                    input=secret).returncode == 0
    except Exception as e:
        print(f"Smart Study passwords: could not save: {e}")
        return False


def forget_all() -> None:
    _cache.clear()
    try:
        if sys.platform.startswith("win"):
            _WinCred().delete_all(f"{APP}:")
        elif sys.platform == "darwin":
            for _i in range(500):
                if _run(["security", "delete-generic-password", "-s", APP]).returncode != 0:
                    break
        else:
            _run(["secret-tool", "clear", "app", APP])
    except Exception as e:
        print(f"Smart Study passwords: could not delete: {e}")
    value = _state()
    value["never"] = []
    _save_state(value)


def _credentials(host: str, done) -> None:
    """done(creds or None), from the cache or the keyring (in the background)."""
    if host in _cache:
        done(_cache[host])
        return

    def fetched(future):
        try:
            creds = future.result()
        except Exception:
            creds = None
        _cache[host] = creds
        done(creds)
    mw.taskman.run_in_background(lambda: _lookup(host), fetched)


# ── Page scripts (isolated world) ─────────────────────────────────────────

_FIND = r"""
function ssVis(e){return e&&e.getClientRects().length>0&&!e.disabled&&!e.readOnly;}
function ssFind(){
  var p=Array.prototype.find.call(document.querySelectorAll('input[type=password]'),ssVis);
  if(!p)return null;
  var scope=p.form||document;
  var users=Array.prototype.filter.call(scope.querySelectorAll('input'),function(e){
    return e!==p&&ssVis(e)&&/^(text|email|tel|)$/i.test(e.getAttribute('type')||'')&&
      (e.compareDocumentPosition(p)&Node.DOCUMENT_POSITION_FOLLOWING);});
  return {p:p,u:users.length?users[users.length-1]:null};
}
"""

# Reports a sent login once per page: on submit, Enter in a field, or a click
# on the form's button (some sites send it with script, without "submit").
_WATCH = _FIND + r"""
(function(nonce){
  if(window.__ssPwWatch)return !!ssFind();
  window.__ssPwWatch=true;
  var sent=false;
  function report(){
    if(sent)return;var f=ssFind();if(!f||!f.p.value)return;
    sent=true;console.log(nonce+JSON.stringify({u:f.u?f.u.value:'',p:f.p.value}));
    setTimeout(function(){sent=false;},3000);
  }
  document.addEventListener('submit',report,true);
  document.addEventListener('keydown',function(e){if(e.key==='Enter'&&e.target&&e.target.tagName==='INPUT')report();},true);
  document.addEventListener('click',function(e){
    var b=e.target&&e.target.closest&&e.target.closest('button,input[type=submit],input[type=button],[role=button]');
    if(b)report();},true);
  return !!ssFind();
})(%s)
"""

_FILL = _FIND + r"""
(function(user,pw){
  var f=ssFind();if(!f)return false;
  var setter=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
  function put(e,v){setter.call(e,v);e.dispatchEvent(new Event('input',{bubbles:true}));
    e.dispatchEvent(new Event('change',{bubbles:true}));}
  if(f.u&&user&&!f.u.value)put(f.u,user);
  if(!f.p.value)put(f.p,pw);
  return true;
})(%s,%s)
"""


def _host(view) -> str:
    url = view.url()
    if url.scheme() != "https":
        return ""
    return (url.host() or "").lower()


def page_loaded(view) -> None:
    """Called after a page finished loading: watch its login form and fill it."""
    if not enabled():
        return
    host = _host(view)
    if not host:
        return
    page = view.page()
    tries = [0]

    def watched(has_form):
        if not has_form:
            if tries[0] < 2:  # forms built by script appear a little later
                tries[0] += 1
                QTimer.singleShot(1500, lambda: _alive(view) and _host(view) == host and page.runJavaScript(
                    _WATCH % json.dumps(_NONCE), _WORLD, watched))
            return
        if _never(host):
            return

        def fill(creds):
            if creds and _alive(view) and _host(view) == host:
                page.runJavaScript(_FILL % (json.dumps(creds[0]), json.dumps(creds[1])), _WORLD, lambda _ok: None)
        _credentials(host, fill)
    page.runJavaScript(_WATCH % json.dumps(_NONCE), _WORLD, watched)


def _alive(view) -> bool:
    from .browser_features import _alive as alive
    return alive(view)


def console_message(page, message: str) -> bool:
    """True when the message was a sent login from our page script."""
    if not message.startswith(_NONCE):
        return False
    try:
        data = json.loads(message[len(_NONCE):])
        user, password = str(data.get("u", "")), str(data["p"])
    except Exception:
        return True
    view = getattr(page, "_ss_view", None)
    host = _host(view) if view is not None else ""
    if not host or not password or not enabled() or _never(host) or host in _asking:
        return True

    def check(creds):
        if creds == (user, password):
            return
        QTimer.singleShot(0, lambda: _offer(host, user, password, update=creds is not None))
    _credentials(host, check)
    return True


def _offer(host: str, user: str, password: str, update: bool) -> None:
    _asking.add(host)
    try:
        box = QMessageBox(mw)
        box.setWindowTitle(_("Save password?"))
        text = (_("Update the saved password for {}?") if update else _("Save the password for {}?")).format(host)
        if user:
            text += "\n" + _("User name: {}").format(user)
        box.setText(text)
        box.setInformativeText(_("It is stored in your system keyring (e.g. KWallet, GNOME Keyring, macOS Keychain, Windows Credential Manager). Next time the login page "
                                 "is filled in for you – you only click “Log in”."))
        save = box.addButton(_("Save"), QMessageBox.ButtonRole.AcceptRole)
        never = box.addButton(_("Never for this site"), QMessageBox.ButtonRole.DestructiveRole)
        box.addButton(_("Not now"), QMessageBox.ButtonRole.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked is save:
            def stored(future):
                try:
                    ok = future.result()
                except Exception:
                    ok = False
                if ok:
                    _cache[host] = (user, password)
                else:
                    from aqt.utils import tooltip
                    tooltip(_("Could not save the password (system keyring not reachable)."))
            mw.taskman.run_in_background(lambda: _store(host, user, password), stored)
        elif clicked is never:
            _add_never(host)
    finally:
        _asking.discard(host)


def menu_entries(menu) -> None:
    """Entries for the browser's ⚙ menu."""
    menu.addSeparator()
    fill = menu.addAction(_("Save and fill in passwords"))
    fill.setCheckable(True)
    fill.setChecked(enabled())
    if not available():
        fill.setEnabled(False)
        fill.setToolTip(_("Needs a system keyring (on Linux: secret-tool with KWallet, GNOME Keyring or KeePassXC)."))
    fill.toggled.connect(set_enabled)
    forget = menu.addAction(_("Delete saved passwords…"))
    forget.setEnabled(available())

    def ask():
        if QMessageBox.question(mw, _("Delete saved passwords…").rstrip("…"),
                                _("Delete all passwords saved by the Smart Study browser?")) \
                == QMessageBox.StandardButton.Yes:
            forget_all()
    forget.triggered.connect(lambda: QTimer.singleShot(0, ask))
