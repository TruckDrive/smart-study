# -*- coding: utf-8 -*-
"""Ad and tracker blocking for the Smart Study browser with uBlock Origin's
default filter lists (uBlock filters, EasyList, EasyPrivacy).

The lists are downloaded when the browser first opens and refreshed weekly
into SmartStudy_Data/adblock; adblock_engine.py evaluates them.  Requests are
refused before they leave the computer, ad slots on a site are hidden with
the lists' element-hiding filters, and on YouTube a small script of our own
skips video ads (uBlock Origin does that with its scriptlets, which are not
used here).
"""
from __future__ import annotations

import os
import pickle
import time
import urllib.request
from typing import Dict, Optional

from .adblock_engine import FilterEngine

LISTS = {
    "ubo-filters": "https://ublockorigin.github.io/uAssets/filters/filters.min.txt",
    "ubo-privacy": "https://ublockorigin.github.io/uAssets/filters/privacy.min.txt",
    "ubo-badware": "https://ublockorigin.github.io/uAssets/filters/badware.min.txt",
    "ubo-quick-fixes": "https://ublockorigin.github.io/uAssets/filters/quick-fixes.min.txt",
    "ubo-unbreak": "https://ublockorigin.github.io/uAssets/filters/unbreak.min.txt",
    "easylist": "https://ublockorigin.github.io/uAssets/thirdparties/easylist.txt",
    "easyprivacy": "https://ublockorigin.github.io/uAssets/thirdparties/easyprivacy.txt",
}
MAX_AGE = 7 * 24 * 3600
# Bump when adblock_engine's classes change, so an old cache is not loaded.
CACHE_NAME = "engine-v1.pickle"

YOUTUBE_SKIPPER = r"""
(function () {
  if (window.__smartstudyAdSkip) return;
  window.__smartstudyAdSkip = true;
  function tick(player) {
    var video = player.querySelector('video');
    if (player.classList.contains('ad-showing')) {
      if (video && isFinite(video.duration) && video.duration > 0) {
        if (!video.muted) { video.muted = true; video.__smartstudyMuted = true; }
        video.currentTime = video.duration;
      }
      var skip = player.querySelector('.ytp-skip-ad-button, .ytp-ad-skip-button, .ytp-ad-skip-button-modern');
      if (skip) skip.click();
    } else if (video && video.__smartstudyMuted) {
      video.muted = false;
      video.__smartstudyMuted = false;
    }
  }
  // Wait for the player once, then watch only its class attribute.
  var finder = setInterval(function () {
    var player = document.getElementById('movie_player');
    if (!player) return;
    clearInterval(finder);
    tick(player);
    new MutationObserver(function () { tick(player); })
      .observe(player, {attributes: true, attributeFilter: ['class']});
  }, 1000);
})();
"""

# Like uBlock Origin's json-prune filter for YouTube: drop the ad data from
# YouTube's player responses before the player reads them, so ads are not
# even requested.  Runs in the page's own world at document creation; the
# Proxy keeps JSON.parse looking native to the page.  %s = sites switched off.
YOUTUBE_PRUNER = r"""
(function (off) {
  var host = location.hostname;
  if (!/(^|\.)(youtube\.com|youtube-nocookie\.com)$/.test(host)) return;
  if (off.indexOf(host) >= 0 || window.__smartstudyAdPrune) return;
  window.__smartstudyAdPrune = true;
  var KEYS = ['adPlacements', 'playerAds', 'adSlots', 'adBreakHeartbeatParams'];
  function prune(value) {
    if (value && typeof value === 'object') {
      [value, value.playerResponse].forEach(function (target) {
        if (target && typeof target === 'object') {
          KEYS.forEach(function (key) { if (key in target) delete target[key]; });
          // "Ad blockers are not allowed / Allow YouTube ads?" comes in the data.
          var ui = target.auxiliaryUi && target.auxiliaryUi.messageRenderers;
          if (ui && ui.enforcementMessageViewModel) delete ui.enforcementMessageViewModel;
        }
      });
    }
    return value;
  }
  // Should the message still appear: remove it and let the video play on.
  function dropWall() {
    var walls = document.querySelectorAll('ytd-enforcement-message-view-model');
    if (!walls.length) return;
    walls.forEach(function (wall) {
      var dialog = wall.closest('tp-yt-paper-dialog, ytd-popup-container > *') || wall;
      dialog.remove();
    });
    document.querySelectorAll('tp-yt-iron-overlay-backdrop').forEach(function (b) { b.remove(); });
    document.body && document.body.style.removeProperty('overflow');
    var video = document.querySelector('video');
    if (video && video.paused && !video.ended) video.play().catch(function () {});
  }
  new MutationObserver(function () { dropWall(); })
    .observe(document, {childList: true, subtree: true});
  JSON.parse = new Proxy(JSON.parse, {
    apply: function (target, self, args) { return prune(Reflect.apply(target, self, args)); }
  });
  Response.prototype.json = new Proxy(Response.prototype.json, {
    apply: function (target, self, args) { return Reflect.apply(target, self, args).then(prune); }
  });
  // The first video's data comes as "var ytInitialPlayerResponse = {…}".
  var initial;
  try {
    Object.defineProperty(window, 'ytInitialPlayerResponse', {
      configurable: true,
      get: function () { return initial; },
      set: function (value) { initial = prune(value); }
    });
  } catch (e) {}
})(%s);
"""
PRUNER_NAME = "smartstudy-youtube-ads"


def install_youtube_pruner(profile, enabled: bool, off_sites=()) -> None:
    """(Re)place the profile-wide YouTube ad pruner.  Profile scripts reach
    the very first page load, unlike scripts added during a navigation."""
    import json
    from PyQt6.QtWebEngineCore import QWebEngineScript
    scripts = profile.scripts()
    for old in scripts.find(PRUNER_NAME):
        scripts.remove(old)
    if not enabled:
        return
    script = QWebEngineScript()
    script.setName(PRUNER_NAME)
    script.setSourceCode(YOUTUBE_PRUNER % json.dumps(sorted(off_sites)))
    script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
    script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
    script.setRunsOnSubFrames(True)   # embedded videos
    scripts.insert(script)


_STYLE_INJECTOR = r"""
(function (css) {
  if (window.__smartstudyAdCss) return;
  window.__smartstudyAdCss = true;
  function add() {
    var style = document.createElement('style');
    style.textContent = css;
    (document.head || document.documentElement).appendChild(style);
  }
  if (document.documentElement) add();
  else new MutationObserver(function (_m, observer) {
    if (document.documentElement) { observer.disconnect(); add(); }
  }).observe(document, {childList: true});
})(%s);
"""


def _list_paths(folder: str) -> Dict[str, str]:
    return {name: os.path.join(folder, name + ".txt") for name in LISTS}


def _outdated(folder: str) -> bool:
    try:
        oldest = min(os.path.getmtime(p) for p in _list_paths(folder).values())
    except (OSError, ValueError):
        return True
    return time.time() - oldest > MAX_AGE


def _build(folder: str) -> Optional[FilterEngine]:
    """Engine from the saved lists, through the cache when it is current."""
    paths = [p for p in _list_paths(folder).values() if os.path.exists(p)]
    if not paths:
        return None
    cache = os.path.join(folder, CACHE_NAME)
    try:
        if os.path.getmtime(cache) >= max(os.path.getmtime(p) for p in paths):
            with open(cache, "rb") as f:
                engine = pickle.load(f)
            if isinstance(engine, FilterEngine):
                return engine
    except Exception:
        pass  # missing, stale or from another add-on version: rebuild
    texts = []
    for path in paths:
        with open(path, encoding="utf-8", errors="replace") as f:
            texts.append(f.read())
    engine = FilterEngine().add_lists(texts)
    try:
        tmp = cache + ".tmp"
        with open(tmp, "wb") as f:
            pickle.dump(engine, f, protocol=pickle.HIGHEST_PROTOCOL)
        os.replace(tmp, cache)
    except OSError:
        pass
    return engine


def _download(folder: str) -> None:
    for name, path in _list_paths(folder).items():
        request = urllib.request.Request(LISTS[name], headers={"User-Agent": "Smart Study"})
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
        if len(data) < 1000:
            raise ValueError(f"filter list {name} looks incomplete")
        tmp = path + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, path)


try:
    from PyQt6.QtWebEngineCore import (QWebEnginePage, QWebEngineScript,
                                       QWebEngineUrlRequestInfo,
                                       QWebEngineUrlRequestInterceptor)

    _Type = QWebEngineUrlRequestInfo.ResourceType
    _RESOURCE_TYPES = {
        "ResourceTypeSubFrame": "subdocument", "ResourceTypeStylesheet": "stylesheet",
        "ResourceTypeScript": "script", "ResourceTypeImage": "image",
        "ResourceTypeFavicon": "image", "ResourceTypeFontResource": "font",
        "ResourceTypeObject": "object", "ResourceTypePluginResource": "object",
        "ResourceTypeMedia": "media", "ResourceTypeXhr": "xhr",
        "ResourceTypePing": "ping", "ResourceTypeWebSocket": "websocket",
    }
    _TYPE_NAMES = {getattr(_Type, name): kind for name, kind in _RESOURCE_TYPES.items()
                   if hasattr(_Type, name)}

    class AdBlocker(QWebEngineUrlRequestInterceptor):
        """interceptRequest runs on Chromium's IO thread; it only reads."""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.enabled = True
            self.engine: Optional[FilterEngine] = None
            self.allowed_sites: set = set()      # hosts where the user turned it off
            self.blocked: Dict[str, int] = {}    # page host → requests blocked

        def active_on(self, host: str) -> bool:
            return self.enabled and self.engine is not None and host not in self.allowed_sites

        def interceptRequest(self, info):
            engine = self.engine
            if not self.enabled or engine is None:
                return
            kind = info.resourceType()
            # Never block a page the user opens on purpose.
            if kind == _Type.ResourceTypeMainFrame:
                return
            page_host = info.firstPartyUrl().host()
            if page_host in self.allowed_sites:
                return
            url = info.requestUrl()
            if engine.should_block(url.toString(), url.host(), page_host,
                                   _TYPE_NAMES.get(kind, "other")):
                info.block(True)
                self.blocked[page_host] = self.blocked.get(page_host, 0) + 1

        def start(self, folder: str) -> None:
            """Load the saved lists in the background, then refresh old ones."""
            from aqt import mw
            folder = os.path.join(folder, "adblock")
            os.makedirs(folder, exist_ok=True)

            def loaded(future):
                try:
                    self.engine = future.result() or self.engine
                except Exception as e:
                    print(f"Smart Study browser: ad-block lists not loaded: {e}")
                if _outdated(folder):
                    mw.taskman.run_in_background(lambda: (_download(folder), _build(folder))[1],
                                                 refreshed)

            def refreshed(future):
                try:
                    self.engine = future.result() or self.engine
                except Exception as e:
                    print(f"Smart Study browser: ad-block lists not updated: {e}")

            mw.taskman.run_in_background(lambda: _build(folder), loaded)

        def prepare_page(self, page, url) -> str:
            """Element hiding (and the YouTube ad skipper) for the next page;
            returns the script source ("" for none)."""
            scripts = page.scripts()
            for old in scripts.find("smartstudy-adblock"):
                scripts.remove(old)
            host = url.host()
            self.blocked[host] = 0
            if not self.active_on(host):
                return ""
            source = ""
            css = self.engine.css_for(host)
            if css:
                import json
                source += _STYLE_INJECTOR % json.dumps(css)
            if host == "youtube.com" or host.endswith(".youtube.com"):
                source += YOUTUBE_SKIPPER
            if not source:
                return ""
            script = QWebEngineScript()
            script.setName("smartstudy-adblock")
            script.setSourceCode(source)
            script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
            script.setWorldId(QWebEngineScript.ScriptWorldId.ApplicationWorld)
            script.setRunsOnSubFrames(False)
            scripts.insert(script)
            return source

    class FilteringPage(QWebEnginePage):
        """Browser page that gets its element-hiding script per navigation."""

        def __init__(self, profile, parent, blocker: Optional[AdBlocker]):
            super().__init__(profile, parent)
            self.blocker = blocker
            self.adblock_source = ""
            # A script inserted while a navigation is under way only reaches
            # the documents after it (cross-site loads start a new renderer),
            # so also run it on commit and on load; the scripts guard against
            # running twice.
            self.urlChanged.connect(self._run_adblock_script)
            self.loadFinished.connect(self._run_adblock_script)

        def acceptNavigationRequest(self, url, nav_type, is_main_frame):
            if is_main_frame and self.blocker is not None:
                try:
                    self.adblock_source = self.blocker.prepare_page(self, url)
                except Exception as e:
                    self.adblock_source = ""
                    print(f"Smart Study browser: element hiding skipped: {e}")
            return super().acceptNavigationRequest(url, nav_type, is_main_frame)

        def _run_adblock_script(self, *_args):
            if self.adblock_source:
                self.runJavaScript(self.adblock_source,
                                   QWebEngineScript.ScriptWorldId.ApplicationWorld)

except ImportError:  # pragma: no cover
    AdBlocker = None  # type: ignore
    FilteringPage = None  # type: ignore
