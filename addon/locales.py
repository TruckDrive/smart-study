# -*- coding: utf-8 -*-
"""
SmartStudy - Localization Module
================================

A lightweight in-code translation system for the SmartStudy add-on.

UI strings in the source code stay in English and are wrapped with ``_(...)``.
The :func:`_` function looks up the translated value in :data:`TRANSLATIONS`
for the currently active language.

The active language is controlled by :data:`USER_LANG`, which is set from
the ``language`` key of ``addon_settings.json`` (see ``__init__.py``).
Changing the value takes effect on the next ``_()`` call – no restart
needed. UI that has already been rendered (window titles, existing menu
entries, etc.) only updates the next time it is rebuilt.

Supported values for :data:`USER_LANG`:

* ``"auto"`` – detect from Anki's UI language (fallback: ``"en"``)
* ``"en"``   – English (source language; keys are returned as-is)
* ``"de"``   – Deutsch
* ``"es"``   – Español
* ``"ko"``   – 한국어
* ``"pt"``   – Português
* ``"fr"``   – Français
* ``"vi"``   – Tiếng Việt
* ``"zh"``   – 中文
* ``"hi"``   – हिन्दी
* ``"pl"``   – Polski
* ``"fa"``   – فارسی (right-to-left; its strings live in translations_fa.json)


Adding / editing translations
-----------------------------
* The **key** is the exact English source string that appears in the code.
* The **value** is a dict ``{"de": "...", "es": "...", "ko": "...", ...}`` with the
  translated strings. A missing or empty entry falls back to the key.
* Keep placeholder tokens (``{}``, ``{name}``, ``%s``, newlines, HTML
  tags …) identical across all languages so ``.format()`` keeps working.
"""

try:
    from .quiet import ignored as _ignored
except ImportError:  # the module is loaded on its own (tests)
    def _ignored(*_args):
        pass

from typing import Dict
import json
from pathlib import Path

# Supplemental catalog for newer features; loaded locally once.
SUPPLEMENTAL_TRANSLATIONS = json.loads(Path(__file__).with_name("translation_catalog.json").read_text(encoding="utf-8"))
WORKSPACE_TRANSLATIONS = json.loads(Path(__file__).with_name("workspace_translations.json").read_text(encoding="utf-8"))
PERSIAN_TRANSLATIONS = json.loads(Path(__file__).with_name("translations_fa.json").read_text(encoding="utf-8"))

try:
    from .web_translations import WEB_TRANSLATIONS
except ImportError:
    from web_translations import WEB_TRANSLATIONS  # type: ignore


# --------------------------------------------------------------------- #
# Active language
# --------------------------------------------------------------------- #
# Valid values: "auto", "en", "de", "es", "ko", "pt", "fr", "vi", "zh", "hi", "pl", "fa".
# Defaults to "auto" until ``on_profile_open()`` overwrites it from the
# user's settings.
USER_LANG: str = "auto"


# --------------------------------------------------------------------- #
# Language detection helpers
# --------------------------------------------------------------------- #
def _detect_anki_lang() -> str:
    """Best-effort detection of Anki's current UI language.

    Returns one of ``"en"``, ``"de"``, ``"es"``, ``"ko"``, ``"pt"``,
    ``"fr"``, ``"vi"``, ``"zh"``, ``"hi"``, ``"pl"``, ``"fa"``. Unknown Anki locales fall
    back to English.
    """
    raw = ""
    # Preferred API (modern Anki versions).
    try:
        from anki.lang import current_lang  # type: ignore
        raw = current_lang or ""
    except Exception:
        _ignored()
    # Fallback API name used on some older Anki versions.
    if not raw:
        try:
            from anki.lang import currentLang  # type: ignore
            raw = currentLang or ""
        except Exception:
            _ignored()
    # Last resort: read directly from the profile manager.
    if not raw:
        try:
            from aqt import mw  # type: ignore
            if mw is not None and getattr(mw, "pm", None) is not None:
                raw = mw.pm.meta.get("defaultLang", "") or ""
        except Exception:
            _ignored()

    raw = (raw or "").lower()
    if raw.startswith("de"):
        return "de"
    if raw.startswith("es"):
        return "es"
    if raw.startswith("ko"):
        return "ko"
    if raw.startswith("pt"):
        return "pt"
    if raw.startswith("fr"):
        return "fr"
    if raw.startswith("vi"):
        return "vi"
    if raw.startswith("zh"):
        return "zh"
    if raw.startswith("hi"):
        return "hi"
    if raw.startswith("pl"):
        return "pl"
    if raw.startswith("fa"):
        return "fa"
    return "en"


def _current_lang() -> str:
    """Resolve :data:`USER_LANG` to a concrete language code."""
    lang = USER_LANG
    if lang == "auto":
        return _detect_anki_lang()
    if lang in ("en", "de", "es", "ko", "pt", "fr", "vi", "zh", "hi", "pl", "fa"):
        return lang
    return "en"


def is_rtl() -> bool:
    """True when the active language is written right to left."""
    return _current_lang() == "fa"


# --------------------------------------------------------------------- #
# Public translation function
# --------------------------------------------------------------------- #
def _(text: str) -> str:
    """Return the translation of *text* for the current user language.

    If the key is missing or has no entry for the active language, the
    original English ``text`` is returned unchanged as a safe fallback.
    """
    return translate_for_language(text, _current_lang())


def translate_for_language(text: str, lang: str) -> str:
    """Translate without changing the active language (e.g. during onboarding)."""
    if lang == "en":
        return text
    if lang == "fa":
        return PERSIAN_TRANSLATIONS.get(text) or text
    for catalog in (TRANSLATIONS, WEB_TRANSLATIONS, SUPPLEMENTAL_TRANSLATIONS, WORKSPACE_TRANSLATIONS):
        translated = catalog.get(text, {}).get(lang)
        if translated:
            return translated
    return text


# --------------------------------------------------------------------- #
# Translations
# --------------------------------------------------------------------- #
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "Block on {}": {"de": "Auf {} blockieren"},
    "{} blocked on this page": {"de": "{} auf dieser Seite blockiert"},
    "Loading filter lists\u2026": {"de": "Filterlisten werden geladen …"},
    "Search engine": {"de": "Suchmaschine"},
    "Block ads and trackers": {"de": "Werbung und Tracker blockieren"},
    "Search engine and ad blocker": {"de": "Suchmaschine und Werbeblocker"},
    "Choose which celebrations appear on the dashboard. Changes are saved immediately.": {"de": "Wähle die Erfolgsmeldungen für dein Dashboard. Änderungen werden sofort gespeichert."},
    "Google is having trouble loading or requests verification. You can try DuckDuckGo instead. Home stays unchanged.": {"de": "Google lädt nicht richtig oder verlangt eine Sicherheitsprüfung. Du kannst stattdessen DuckDuckGo ausprobieren. Home bleibt unverändert."},
    "Try DuckDuckGo": {"de": "DuckDuckGo ausprobieren"},
    "Your Synapse level {} was carried over to Smart Study.": {"de": "Dein Synapse-Level {} wurde in Smart Study übernommen."},
    "Show celebrations on the dashboard.": {"de": "Erfolgsmeldungen auf dem Dashboard anzeigen."},
    "Celebration": {"de": "Erfolg"},
    "+{} XP claimed.": {"de": "+{} XP abgeholt."},
    "Goal achieved!": {"de": "Ziel erreicht!"},
    "Opening developer console...": {"de": "Entwicklerkonsole wird geöffnet..."},
    "Open developer console": {"de": "Entwicklerkonsole öffnen"},
    "Developer console unlocked": {"de": "Entwicklerkonsole freigeschaltet"},
    "Could not open the developer console: {}": {"de": "Die Entwicklerkonsole konnte nicht geöffnet werden: {}"},
    "Developer console": {"de": "Entwicklerkonsole"},
    "Badge: nearby goal": {"de": "Abzeichen: nahes Ziel"},
    "Badge: active comeback": {"de": "Abzeichen: laufender Wiedereinstieg"},
    "Badge: stage change": {"de": "Abzeichen: Stufenwechsel"},
    "Badge: all complete": {"de": "Abzeichen: alles vollständig"},
    "Badge gallery": {"de": "Abzeichenübersicht"},
    "Badge gallery: {}": {"de": "Abzeichenübersicht: {}"},
    "Badge stage": {"de": "Abzeichenstufe"},
    "Locked": {"de": "Gesperrt"},
    "Preview only. Your profile stays unchanged.": {"de": "Nur Vorschau. Dein Profil bleibt unverändert."},
    "Preview closed. Use Replay to show it again.": {"de": "Vorschau geschlossen. Mit Erneut abspielen kannst du sie wieder öffnen."},
    "Preview only. Celebration preferences will be connected when this design is adopted.": {"de": "Nur Vorschau. Die Meldungseinstellungen werden bei Übernahme des Designs verbunden."},
    "New rank unlocked": {"de": "Neuer Rang freigeschaltet"},
    "Your learning is paying off.": {"de": "Dein Lernen zahlt sich aus."},
    "Celebration settings": {"de": "Erfolgsmeldungen einstellen"},
    "Rank up": {"de": "Rangaufstieg"},
    "Level up": {"de": "Levelaufstieg"},
    "Also show a completed challenge": {"de": "Zusätzlich eine abgeschlossene Challenge anzeigen"},
    "Dark preview": {"de": "Dunkle Vorschau"},
    "Reduced motion": {"de": "Reduzierte Bewegung"},
    "Previous rank": {"de": "Vorheriger Rang"},
    "New rank": {"de": "Neuer Rang"},
    "Replay": {"de": "Erneut abspielen"},
    "Achievements": {"de": "Abzeichen"},
    "Study streak": {"de": "Lernserie"},
    "Reviews": {"de": "Wiederholungen"},
    "Study days": {"de": "Lerntage"},
    "Daily goals": {"de": "Tagesziele"},
    "Welcome back": {"de": "Wiedereinstieg"},
    "Earned": {"de": "Verdient"},
    "Bronze": {"de": "Bronze"},
    "Silver": {"de": "Silber"},
    "Gold": {"de": "Gold"},
    "Diamond": {"de": "Diamant"},
    "Select a badge to see your progress.": {"de": "Klicke auf ein Abzeichen, um deinen Fortschritt zu sehen."},
    "Not earned yet": {"de": "Noch nicht verdient"},
    "Recorded progress: {}": {"de": "Erfasster Fortschritt: {}"},
    "Next stage: {}": {"de": "Nächste Stufe: {}"},
    "Still needed: {}": {"de": "Noch benötigt: {}"},
    "All stages earned": {"de": "Alle Stufen verdient"},
    "This achievement is yours to keep.": {"de": "Dieses Abzeichen bleibt dir erhalten."},
    "Your next badge": {"de": "Dein nächstes Abzeichen"},
    "One more {} to reach {}.": {"de": "Noch 1 {} bis {}."},
    "{} more {} to reach {}.": {"de": "Noch {} {} bis {}."},
    "Earned on {}": {"de": "Erreicht am {}"},
    "Choose as favorite badge": {"de": "Als Lieblingsabzeichen wählen"},
    "Favorite badge": {"de": "Lieblingsabzeichen"},
    "streak day": {"de": "Serientag"},
    "streak days": {"de": "Serientage"},
    "review": {"de": "Wiederholung"},
    "reviews": {"de": "Wiederholungen"},
    "study day": {"de": "Lerntag"},
    "study days": {"de": "Lerntage"},
    "daily goal": {"de": "Tagesziel"},
    "daily goals": {"de": "Tagesziele"},
    "Study on consecutive Anki days. Your longest recorded streak counts, even after a break.": {"de": "Lerne an aufeinanderfolgenden Anki-Tagen. Deine längste erfasste Serie zählt, auch nach einer Pause."},
    "Answer cards. Repeated answers to the same card count; manual rescheduling does not.": {"de": "Beantworte Karten. Mehrere Antworten auf dieselbe Karte zählen mit. Manuelles Neuplanen zählt nicht."},
    "Study on different Anki days. One answer is enough for a day to count. Breaks are welcome.": {"de": "Lerne an verschiedenen Anki-Tagen. Eine Antwort genügt, damit ein Tag zählt. Pausen sind erlaubt."},
    "Complete daily challenges. Each day counts once, even without claiming XP. Counting starts with this feature.": {"de": "Schließe Tageschallenges ab. Jeder Tag zählt einmal, auch ohne die XP abzuholen. Die Zählung beginnt mit dieser Funktion."},
    "After at least seven full days without reviews, study on three consecutive Anki days. This is a one-time achievement.": {"de": "Lerne nach mindestens sieben vollen Tagen ohne Wiederholungen an drei aufeinanderfolgenden Anki-Tagen. Dieses Abzeichen wird einmalig vergeben."},
    'Simulated Preview': {"de": 'Simulierte Vorschau'},
    'Decks': {"de": 'Stapel'},
    'Example background. The result depends on your wallpaper. Blur is easier to see with lower surface opacity and a detailed image.': {"de": 'Beispielhintergrund. Das Ergebnis hängt von deinem Hintergrundbild ab. Bei geringerer Deckkraft und einem detailreichen Bild ist die Unschärfe deutlicher sichtbar.'},
    'This renderer does not support the glass effect. Normal transparency is shown.': {"de": 'Diese Darstellung unterstützt den Glaseffekt nicht. Es wird die normale Transparenz angezeigt.'},

    'Glass Effect': {"de": 'Glaseffekt'},
    'May cause severe performance issues. Smooth use and studying cannot be guaranteed while enabled.': {"de": 'Kann die Performance erheblich beeinträchtigen. Flüssige Bedienung und flüssiges Lernen können bei aktiviertem Effekt nicht garantiert werden.'},
    'Glass Strength': {"de": 'Stärke des Glaseffekts'},
    'Lower strength reduces rendering work. Set surface opacity below 100% to see the effect. Unsupported renderers keep normal transparency.': {"de": 'Eine geringere Stärke reduziert den Darstellungsaufwand. Stelle die Deckkraft unter 100 %, damit der Effekt sichtbar wird. Ohne technische Unterstützung bleibt die normale Transparenz erhalten.'},
    'Enable glass effect?': {"de": 'Glaseffekt aktivieren?'},
    'This effect may cause severe performance issues.': {"de": 'Dieser Effekt kann die Performance erheblich beeinträchtigen.'},
    'Blurring the background adds rendering work, especially with large windows and long deck lists. Smooth use and studying can no longer be guaranteed while this option is enabled.': {"de": 'Die Unschärfe im Hintergrund erzeugt zusätzlichen Darstellungsaufwand, besonders bei großen Fenstern und langen Decklisten. Solange diese Option aktiviert ist, können flüssige Bedienung und flüssiges Lernen nicht mehr garantiert werden.'},
    'You can reduce the strength or turn the effect off at any time. The effect is limited to the dashboard and does not change your learning data.': {"de": 'Du kannst die Stärke jederzeit reduzieren oder den Effekt ausschalten. Der Effekt ist auf das Dashboard begrenzt und verändert deine Lerndaten nicht.'},
    'Enable anyway': {"de": 'Trotzdem aktivieren'},

    'Dashboard Surfaces': {"de": 'Dashboard-Flächen'},
    'Surface Opacity': {"de": 'Deckkraft der Flächen'},
    'Applies to the side panel and the deck list. Text and controls stay fully visible.': {"de": 'Gilt für das Seitenpanel und die Deckliste. Texte und Bedienelemente bleiben vollständig sichtbar.'},

    'Save': {"de": 'Speichern'},


    'Widget Content': {"de": 'Widget-Inhalt'},
    'Show facts or open tasks on the home screen. Click the task widget to open your list.': {"de": 'Zeige Fakten oder offene Aufgaben auf dem Hauptbildschirm. Ein Klick auf das Aufgabenwidget öffnet deine Liste.'},
    'Facts': {"de": 'Fakten'},
    'Tasks': {"de": 'Aufgaben'},
    'Facts or Tasks Widget': {"de": 'Widget für Fakten oder Aufgaben'},
    'Show the selected content on your Anki home screen.': {"de": 'Zeige den ausgewählten Inhalt auf deinem Anki-Hauptbildschirm.'},


    'Not now': {"de": 'Jetzt nicht'},

    "Open in browser": {"de": "Im Browser öffnen"},
    "Search '{}' in browser": {"de": "'{}' im Browser suchen"},
    "Could not open the system browser.": {"de": "Der Standardbrowser konnte nicht geöffnet werden."},

    # browser tabs and extras (website_sidebar.py, browser_features.py)
    "Tab groups": {"de": "Tab-Gruppen"},
    "This video plays in picture in picture.": {"de": "Dieses Video läuft im Bild-im-Bild."},
    "Back to the browser": {"de": "Zurück in den Browser"},
    "Browser settings…": {"de": "Browser-Einstellungen…"},
    "No video in the Smart Study browser": {"de": "Kein Video im Smart-Study-Browser"},
    "Close picture in picture": {"de": "Bild-im-Bild schließen"},
    "Continuing at {}": {"de": "Weiter bei {}"},
    "✓ Video checked off in the study plan": {"de": "✓ Video im Lernplan abgehakt"},
    "The Add window already contains a note. Add or clear it first.": {"de": "Im Hinzufügen-Fenster ist schon eine Notiz. Füge sie erst hinzu oder leere sie."},
    "Select some text on the page first.": {"de": "Markiere zuerst Text auf der Seite."},
    "Could not copy the image.": {"de": "Das Bild konnte nicht kopiert werden."},
    "Image occlusion is not available in this Anki version.": {"de": "Bildverdeckung gibt es in dieser Anki-Version nicht."},
    "Create card from selection": {"de": "Karte aus Auswahl erstellen"},
    "Image occlusion from this image": {"de": "Bildverdeckung aus diesem Bild"},
    "Card at this point of the video": {"de": "Karte zu dieser Videostelle"},
    "Picture in picture": {"de": "Bild-im-Bild"},
    "Save open tabs as a group…": {"de": "Offene Tabs als Gruppe speichern…"},
    "Open instead of the open tabs": {"de": "Statt der offenen Tabs öffnen"},
    "Replace with the open tabs": {"de": "Durch die offenen Tabs ersetzen"},
    "Rename…": {"de": "Umbenennen…"},
    "Tab group": {"de": "Tab-Gruppe"},
    "Name of the group:": {"de": "Name der Gruppe:"},
    "Group “{}” saved ({} tabs)": {"de": "Gruppe „{}“ gespeichert ({} Tabs)"},
    "Focus mode": {"de": "Fokus-Modus"},
    "{} is blocked while you study. Change this under Smart Study → Settings → Browser.": {"de": "{} ist gesperrt, während du lernst. Ändern kannst du das unter Smart Study → Einstellungen → Browser."},
    "Skipped: {}": {"de": "Übersprungen: {}"},
    "Skipped": {"de": "Übersprungen"},
    "Browser": {"de": "Browser"},
    "Videos, tabs, shortcuts and focus in the Smart Study browser. Applies after saving.": {"de": "Videos, Tabs, Tastenkürzel und Fokus im Smart-Study-Browser. Gilt nach dem Speichern."},
    "Study videos": {"de": "Lernvideos"},
    "Tabs": {"de": "Tabs"},
    "Keyboard shortcuts": {"de": "Tastenkürzel"},
    "Video shortcuts work everywhere in Anki, also while you review. Click a shortcut and press the new keys; Backspace removes it, Esc cancels.": {"de": "Video-Kürzel funktionieren überall in Anki, auch beim Lernen der Karten. Klick auf ein Kürzel und drück die neuen Tasten; Rücktaste entfernt es, Esc bricht ab."},
    "Controller": {"de": "Controller"},
    "Video control with a controller": {"de": "Videosteuerung mit Controller"},
    "In the controller settings, the actions “Video Play/Pause”, “Video -10s”, “Video +10s”, “Video Slower”, “Video Faster”, “Video Picture-in-Picture”, “Video Card” and “Browser Next/Previous Tab” can be put on any button.": {"de": "In den Controller-Einstellungen kannst du die Aktionen „Video Play/Pause“, „Video -10s“, „Video +10s“, „Video Slower“, „Video Faster“, „Video Picture-in-Picture“, „Video Card“ und „Browser Next/Previous Tab“ auf jede Taste legen."},
    "Controller settings…": {"de": "Controller-Einstellungen…"},
    "SponsorBlock": {"de": "SponsorBlock"},
    "Skips parts of YouTube videos that other viewers marked (sponsor.ajay.app). Only the first characters of a hash of the video ID are sent, not which video you watch.": {"de": "Überspringt Teile von YouTube-Videos, die andere Zuschauer markiert haben (sponsor.ajay.app). Gesendet werden nur die ersten Zeichen eines Hashes der Video-ID, nicht welches Video du schaust."},
    "Video: play / pause": {"de": "Video: Abspielen / Pause"},
    "Video: 10 s back": {"de": "Video: 10 s zurück"},
    "Video: 10 s forward": {"de": "Video: 10 s vor"},
    "Video: slower": {"de": "Video: langsamer"},
    "Video: faster": {"de": "Video: schneller"},
    "Video: picture in picture": {"de": "Video: Bild-im-Bild"},
    "Card from selected text": {"de": "Karte aus markiertem Text"},
    "Next tab": {"de": "Nächster Tab"},
    "Previous tab": {"de": "Vorheriger Tab"},
    "Everywhere in Anki": {"de": "Überall in Anki"},
    "In the browser": {"de": "Im Browser"},
    "Press keys…": {"de": "Tasten drücken…"},
    "Already used for: ": {"de": "Schon belegt für: "},
    "Open study-plan videos and PDFs in your default browser": {"de": "Lernplan-Videos und -PDFs im Standardbrowser öffnen"},
    "On: videos open in your normal web browser and PDFs in your PDF app (at the right page). Off: both open in a Smart Study browser tab.": {"de": "An: Videos öffnen sich in deinem normalen Browser, PDFs in deinem PDF-Programm (auf der richtigen Seite). Aus: beides öffnet sich in einem Tab des Smart-Study-Browsers."},
    "Continue where you left off": {"de": "Dort weitermachen, wo du aufgehört hast"},
    "A study-plan video starts again at the point where you stopped.": {"de": "Ein Lernplan-Video startet wieder an der Stelle, an der du aufgehört hast."},
    "Check off in the study plan": {"de": "Im Lernplan abhaken"},
    "A study-plan video counts as done once you have watched this much of it.": {"de": "Ein Lernplan-Video gilt als erledigt, sobald du so viel davon gesehen hast."},
    "Restore tabs on start": {"de": "Tabs beim Start wiederherstellen"},
    "The tabs that were open come back after a restart (they load when you open them). Save tab groups with ▤ next to +.": {"de": "Die offenen Tabs sind nach einem Neustart wieder da (sie laden erst, wenn du sie öffnest). Tab-Gruppen speicherst du mit ▤ neben +."},
    "When": {"de": "Wann"},
    "Always": {"de": "Immer"},
    "Only during a Pomodoro study phase": {"de": "Nur während einer Pomodoro-Lernphase"},
    "Hide on YouTube": {"de": "Auf YouTube ausblenden"},
    "YouTube itself stays usable, also for music – only what you tick here disappears.": {"de": "YouTube selbst bleibt nutzbar, auch für Musik – nur was du hier anhakst, verschwindet."},
    "YouTube Shorts": {"de": "YouTube Shorts"},
    "Recommendations on the YouTube start page": {"de": "Vorschläge auf der YouTube-Startseite"},
    "Suggestions next to and after a video": {"de": "Vorschläge neben und nach einem Video"},
    "YouTube comments": {"de": "YouTube-Kommentare"},
    "Block these sites": {"de": "Diese Seiten sperren"},
    "More sites, e.g. 9gag.com, one per line": {"de": "Weitere Seiten, z. B. 9gag.com, eine pro Zeile"},
    "Skip marked parts of YouTube videos": {"de": "Markierte Teile von YouTube-Videos überspringen"},
    "What to skip": {"de": "Was übersprungen wird"},
    "Sponsors": {"de": "Sponsoren"},
    "Self-promotion": {"de": "Eigenwerbung"},
    "Reminders to like or subscribe": {"de": "Aufrufe zu Like oder Abo"},
    "Intros": {"de": "Intros"},
    "Outros and end cards": {"de": "Outros und Abspann"},
    "Non-music parts of music videos": {"de": "Nicht-Musik-Teile in Musikvideos"},
    "New tab": {"de": "Neuer Tab"},
    "Close tab": {"de": "Tab schließen"},
    "Save this page as a favourite": {"de": "Diese Seite als Favorit speichern"},
    "Add another address…": {"de": "Andere Adresse hinzufügen …"},
    "More favourites": {"de": "Weitere Favoriten"},
    "Rename favourite": {"de": "Favorit umbenennen"},
    "Suggest visited pages in the address field": {"de": "Besuchte Seiten im Adressfeld vorschlagen"},
    "Clear browsing history": {"de": "Verlauf löschen"},
    "Browsing history cleared.": {"de": "Verlauf gelöscht."},
    "Stop loading": {"de": "Laden abbrechen"},
    "Open in new tab": {"de": "In neuem Tab öffnen"},
    "Up to {} tabs": {"de": "Höchstens {} Tabs"},
    "Address bar": {"de": "Adresszeile"},
    "Search or enter address": {"de": "Suchen oder Adresse eingeben"},
    "Open PDF file…": {"de": "PDF-Datei öffnen…"},
    "Opening PDF…": {"de": "PDF wird geöffnet…"},
    "The PDF could not be downloaded.": {"de": "Die PDF konnte nicht geladen werden."},

    # ================================================================= #
    # __init__.py – tooltips & menu entries
    # ================================================================= #
    "Smart Study is ready!": {
        "de": "Smart Study ist bereit!",
        "es": "¡Smart Study está listo!",
        "ko": "Smart Study 준비 완료!",
        "pt": "Smart Study está pronto!",
        "fr": "Smart Study est prêt !",
        "vi": "Smart Study đã sẵn sàng!",
        "zh": "Smart Study 已就绪！",
        "hi": "Smart Study तैयार है!",
    },
    "Settings saved.": {
        "de": "Einstellungen gespeichert.",
        "es": "Ajustes guardados.",
        "ko": "설정이 저장되었습니다.",
        "pt": "Configurações salvas.",
        "fr": "Paramètres enregistrés.",
        "vi": "Đã lưu cài đặt.",
        "zh": "设置已保存。",
        "hi": "सेटिंग्स सहेजी गईं।",
    },
    "Settings...": {
        "de": "Einstellungen…",
        "es": "Ajustes…",
        "ko": "설정…",
        "pt": "Configurações…",
        "fr": "Paramètres…",
        "vi": "Cài đặt…",
        "zh": "设置…",
        "hi": "सेटिंग्स…",
    },
    "Toggle Gamification Sidebar": {
        "de": "Gamification-Sidebar ein-/ausblenden",
        "es": "Mostrar/ocultar barra de gamificación",
        "ko": "게임화 사이드바 토글",
        "pt": "Alternar barra de gamificação",
        "fr": "Afficher/masquer la barre de gamification",
        "vi": "Bật/tắt thanh gamification",
        "zh": "切换游戏化侧边栏",
        "hi": "गेमिफिकेशन साइडबार टॉगल करें",
    },

    # ================================================================= #
    # settings_dialog.py
    # ================================================================= #
    "Settings": {
        "de": "Einstellungen",
        "es": "Ajustes",
        "ko": "설정",
        "pt": "Configurações",
        "fr": "Paramètres",
        "vi": "Cài đặt",
        "zh": "设置",
        "hi": "सेटिंग्स",
    },
    "Version": {
        "de": "Version",
        "es": "Versión",
        "ko": "버전",
        "pt": "Versão",
        "fr": "Version",
        "vi": "Phiên bản",
        "zh": "版本",
        "hi": "संस्करण",
    },
    "Changelog": {
        "de": "Änderungen",
        "es": "Cambios",
        "ko": "변경 내역",
        "pt": "Registro de alterações",
        "fr": "Journal des modifications",
        "vi": "Nhật ký thay đổi",
        "zh": "更新日志",
        "hi": "बदलाव लॉग",
    },
    "News": {
        "de": "Neuigkeiten",
        "es": "Novedades",
        "ko": "소식",
        "pt": "Novidades",
        "fr": "Actualités",
        "vi": "Tin tức",
        "zh": "新闻",
        "hi": "समाचार",
    },
    "General Settings": {
        "de": "Allgemeine Einstellungen",
        "es": "Ajustes generales",
        "ko": "일반 설정",
        "pt": "Configurações gerais",
        "fr": "Paramètres généraux",
        "vi": "Cài đặt chung",
        "zh": "常规设置",
        "hi": "सामान्य सेटिंग्स",
    },
    "Auto": {
        "de": "Automatisch",
        "es": "Automático",
        "ko": "자동",
        "pt": "Automático",
        "fr": "Automatique",
        "vi": "Tự động",
        "zh": "自动",
        "hi": "स्वचालित",
    },
    "Medical": {
        "de": "Medizin",
        "es": "Medicina",
        "ko": "의학",
        "pt": "Medicina",
        "fr": "Médecine",
        "vi": "Y học",
        "zh": "医学",
        "hi": "चिकित्सा",
    },
    "Law": {
        "de": "Recht",
        "es": "Derecho",
        "ko": "법률",
        "pt": "Direito",
        "fr": "Droit",
        "vi": "Pháp luật",
        "zh": "法律",
        "hi": "कानून",
    },
    "General": {
        "de": "Allgemein",
        "es": "General",
        "ko": "일반",
        "pt": "Geral",
        "fr": "Général",
        "vi": "Chung",
        "zh": "常规",
        "hi": "सामान्य",
    },
    "Countries": {
        "de": "Länder",
        "es": "Países",
        "ko": "국가",
        "pt": "Países",
        "fr": "Pays",
        "vi": "Quốc gia",
        "zh": "国家",
        "hi": "देश",
    },
    "Background Color:": {
        "de": "Hintergrundfarbe:",
        "es": "Color de fondo:",
        "ko": "배경색:",
        "pt": "Cor de fundo:",
        "fr": "Couleur d'arrière-plan :",
        "vi": "Màu nền:",
        "zh": "背景颜色：",
        "hi": "पृष्ठभूमि रंग:",
    },
    "Statistics Time Range:": {
        "de": "Statistik-Zeitraum:",
        "es": "Rango de estadísticas:",
        "ko": "통계 기간:",
        "pt": "Período das estatísticas:",
        "fr": "Plage des statistiques :",
        "vi": "Khoảng thời gian thống kê:",
        "zh": "统计时间范围：",
        "hi": "सांख्यिकी समय सीमा:",
    },
    "Last 24 Hours": {
        "de": "Letzte 24 Stunden",
        "es": "Últimas 24 horas",
        "ko": "최근 24시간",
        "pt": "Últimas 24 horas",
        "fr": "24 dernières heures",
        "vi": "24 giờ qua",
        "zh": "过去24小时",
        "hi": "पिछले 24 घंटे",
    },
    "Last 7 Days (Week)": {
        "de": "Letzte 7 Tage (Woche)",
        "es": "Últimos 7 días (semana)",
        "ko": "최근 7일 (주)",
        "pt": "Últimos 7 dias (semana)",
        "fr": "7 derniers jours (semaine)",
        "vi": "7 ngày qua (tuần)",
        "zh": "过去7天（周）",
        "hi": "पिछले 7 दिन (सप्ताह)",
    },
    "Last 30 Days (Month)": {
        "de": "Letzte 30 Tage (Monat)",
        "es": "Últimos 30 días (mes)",
        "ko": "최근 30일 (월)",
        "pt": "Últimos 30 dias (mês)",
        "fr": "30 derniers jours (mois)",
        "vi": "30 ngày qua (tháng)",
        "zh": "过去30天（月）",
        "hi": "पिछले 30 दिन (महीना)",
    },
    "Sidebar Visibility:": {
        "de": "Sidebar-Sichtbarkeit:",
        "es": "Visibilidad de la barra lateral:",
        "ko": "사이드바 표시:",
        "pt": "Visibilidade da barra lateral:",
        "fr": "Visibilité de la barre latérale :",
        "vi": "Hiển thị thanh bên:",
        "zh": "侧边栏可见性：",
        "hi": "साइडबार दृश्यता:",
    },
    "Always Show": {
        "de": "Immer anzeigen",
        "es": "Siempre visible",
        "ko": "항상 표시",
        "pt": "Sempre mostrar",
        "fr": "Toujours afficher",
        "vi": "Luôn hiển thị",
        "zh": "始终显示",
        "hi": "हमेशा दिखाएं",
    },
    "Focus mode while reviewing": {
        "de": "Fokus-Modus beim Lernen",
        "es": "Modo de concentración al repasar",
        "ko": "복습 중 집중 모드",
        "pt": "Modo foco durante a revisão",
        "fr": "Mode concentration pendant la révision",
        "vi": "Chế độ tập trung khi ôn tập",
        "zh": "复习时专注模式",
        "hi": "समीक्षा के दौरान फ़ोकस मोड",
    },
    "Focus mode: while you review, only the card is shown. The left bar and Anki's top bar are hidden; shortcuts, the timer and all tools keep working.": {
        "de": "Fokus-Modus: Beim Lernen ist nur die Karte zu sehen. Die linke Leiste und Ankis obere Leiste sind ausgeblendet; Tastenkürzel, Timer und alle Werkzeuge funktionieren weiter.",
        "es": "Modo de concentración: mientras repasas solo se muestra la tarjeta. La barra izquierda y la barra superior de Anki se ocultan; los atajos, el temporizador y todas las herramientas siguen funcionando.",
        "ko": "집중 모드: 복습 중에는 카드만 표시됩니다. 왼쪽 막대와 Anki의 상단 막대는 숨겨지며, 단축키와 타이머, 모든 도구는 계속 작동합니다.",
        "pt": "Modo foco: durante a revisão só o cartão é mostrado. A barra esquerda e a barra superior do Anki ficam ocultas; atalhos, temporizador e todas as ferramentas continuam funcionando.",
        "fr": "Mode concentration : pendant la révision, seule la carte est affichée. La barre de gauche et la barre supérieure d'Anki sont masquées ; les raccourcis, le minuteur et tous les outils continuent de fonctionner.",
        "vi": "Chế độ tập trung: khi ôn tập chỉ hiển thị thẻ. Thanh bên trái và thanh trên cùng của Anki được ẩn; phím tắt, đồng hồ và mọi công cụ vẫn hoạt động.",
        "zh": "专注模式：复习时只显示卡片。左侧栏和 Anki 的顶部栏会隐藏；快捷键、计时器和所有工具仍可使用。",
        "hi": "फ़ोकस मोड: समीक्षा के दौरान केवल कार्ड दिखता है। बायाँ बार और Anki का ऊपरी बार छिप जाते हैं; शॉर्टकट, टाइमर और सभी टूल काम करते रहते हैं।",
    },
    "Hide while Reviewing": {
        "de": "Beim Lernen ausblenden",
        "es": "Ocultar durante el repaso",
        "ko": "복습 중 숨기기",
        "pt": "Ocultar durante a revisão",
        "fr": "Masquer pendant la révision",
        "vi": "Ẩn khi ôn tập",
        "zh": "复习时隐藏",
        "hi": "समीक्षा के दौरान छिपाएं",
    },
    "Enjoying the add-on? Please leave a <b>Thumbs Up</b> on AnkiWeb – it supports me the most!": {
        "de": "Gefällt dir das Add-on? Bitte hinterlasse einen <b>Daumen hoch</b> auf AnkiWeb – damit unterstützt du mich am meisten!",
        "es": "¿Te gusta el complemento? Por favor, deja un <b>pulgar arriba</b> en AnkiWeb: ¡es lo que más me ayuda!",
        "ko": "애드온이 마음에 드시나요? AnkiWeb에 <b>좋아요</b>를 남겨주세요 – 가장 큰 응원이 됩니다!",
        "pt": "Está gostando do complemento? Deixe um <b>joinha</b> no AnkiWeb – é o que mais me ajuda!",
        "fr": "Vous aimez ce module ? Laissez un <b>pouce en l'air</b> sur AnkiWeb – c'est ce qui m'aide le plus !",
        "vi": "Bạn thích tiện ích này? Hãy để lại <b>Thích</b> trên AnkiWeb – đó là sự ủng hộ lớn nhất!",
        "zh": "喜欢这个插件吗？请在 AnkiWeb 留下<b>点赞</b>——这对我帮助最大！",
        "hi": "ऐड-ऑन पसंद आया? AnkiWeb पर <b>थम्स अप</b> दें – यही मेरे लिए सबसे बड़ा समर्थन है!",
    },
    "Rate on AnkiWeb": {
        "de": "Auf AnkiWeb bewerten",
        "es": "Valorar en AnkiWeb",
        "ko": "AnkiWeb에서 평가하기",
        "pt": "Avaliar no AnkiWeb",
        "fr": "Évaluer sur AnkiWeb",
        "vi": "Đánh giá trên AnkiWeb",
        "zh": "在 AnkiWeb 评分",
        "hi": "AnkiWeb पर रेटिंग दें",
    },
    "Deadline Bar": {
        "de": "Deadline-Leiste",
        "es": "Barra de fechas límite",
        "ko": "마감일 바",
        "pt": "Barra de prazo",
        "fr": "Barre d'échéance",
        "vi": "Thanh thời hạn",
        "zh": "截止日期栏",
        "hi": "समयसीमा बार",
    },
    "Advanced Statistics": {
        "de": "Erweiterte Statistiken",
        "es": "Estadísticas avanzadas",
        "ko": "고급 통계",
        "pt": "Estatísticas avançadas",
        "fr": "Statistiques avancées",
        "vi": "Thống kê nâng cao",
        "zh": "高级统计",
        "hi": "उन्नत सांख्यिकी",
    },
    "Deck Overview": {
        "de": "Stapel-Übersicht",
        "es": "Resumen del mazo",
        "ko": "덱 개요",
        "pt": "Visão geral do baralho",
        "fr": "Aperçu du paquet",
        "vi": "Tổng quan bộ thẻ",
        "zh": "牌组概览",
        "hi": "डेक अवलोकन",
    },
    "Enable Custom Deck Dashboard": {
        "de": "Eigenes Stapel-Dashboard aktivieren",
        "es": "Activar panel de mazos personalizado",
        "ko": "커스텀 덱 대시보드 활성화",
        "pt": "Ativar painel de baralho personalizado",
        "fr": "Activer le tableau de bord personnalisé",
        "vi": "Bật bảng điều khiển bộ thẻ tùy chỉnh",
        "zh": "启用自定义牌组仪表板",
        "hi": "कस्टम डेक डैशबोर्ड सक्षम करें",
    },
    "Sidebar": {
        "de": "Sidebar",
        "es": "Barra lateral",
        "ko": "사이드바",
        "pt": "Barra lateral",
        "fr": "Barre latérale",
        "vi": "Thanh bên",
        "zh": "侧边栏",
        "hi": "साइडबार",
    },
    "Mind Map": {
        "de": "Mindmap",
        "es": "Mapa mental",
        "ko": "마인드맵",
        "pt": "Mapa mental",
        "fr": "Carte mentale",
        "vi": "Sơ đồ tư duy",
        "zh": "思维导图",
        "hi": "माइंड मैप",
    },
    "Gamification Sidebar": {
        "de": "Gamification-Sidebar",
        "es": "Barra de gamificación",
        "ko": "게임화 사이드바",
        "pt": "Barra de gamificação",
        "fr": "Barre de gamification",
        "vi": "Thanh gamification",
        "zh": "游戏化侧边栏",
        "hi": "गेमिफिकेशन साइडबार",
    },
    "Music Player": {
        "de": "Musik-Player",
        "es": "Reproductor de música",
        "ko": "음악 플레이어",
        "pt": "Reprodutor de música",
        "fr": "Lecteur de musique",
        "vi": "Trình phát nhạc",
        "zh": "音乐播放器",
        "hi": "म्यूजिक प्लेयर",
    },
    "AI Assistant": {
        "de": "KI-Assistent",
        "es": "Asistente de IA",
        "ko": "AI 어시스턴트",
        "pt": "Assistente de IA",
        "fr": "Assistant IA",
        "vi": "Trợ lý AI",
        "zh": "AI 助手",
        "hi": "AI सहायक",
    },
    "Website Viewer": {
        "de": "Website-Anzeige",
        "es": "Visor de sitios web",
        "ko": "웹사이트 뷰어",
        "pt": "Visualizador de sites",
        "fr": "Visionneuse de sites web",
        "vi": "Trình xem trang web",
        "zh": "网页查看器",
        "hi": "वेबसाइट व्यूअर",
    },
    "Cancel": {
        "de": "Abbrechen",
        "es": "Cancelar",
        "ko": "취소",
        "pt": "Cancelar",
        "fr": "Annuler",
        "vi": "Hủy",
        "zh": "取消",
        "hi": "रद्द करें",
    },
    "Save Settings": {
        "de": "Einstellungen speichern",
        "es": "Guardar ajustes",
        "ko": "설정 저장",
        "pt": "Salvar configurações",
        "fr": "Enregistrer les paramètres",
        "vi": "Lưu cài đặt",
        "zh": "保存设置",
        "hi": "सेटिंग्स सहेजें",
    },
    "Default": {
        "de": "Standard",
        "es": "Predeterminado",
        "ko": "기본값",
        "pt": "Padrão",
        "fr": "Par défaut",
        "vi": "Mặc định",
        "zh": "默认",
        "hi": "डिफ़ॉल्ट",
    },

    # ================================================================= #
    # daily_widgets.py
    # ================================================================= #
    "Study Plan": {
        "de": "Lernplan",
        "es": "Plan de estudio",
        "ko": "학습 계획",
        "pt": "Plano de estudos",
        "fr": "Plan d'étude",
        "vi": "Kế hoạch học tập",
        "zh": "学习计划",
        "hi": "अध्ययन योजना",
    },
    "Done": {
        "de": "Fertig",
        "es": "Hecho",
        "ko": "완료",
        "pt": "Concluído",
        "fr": "Terminé",
        "vi": "Xong",
        "zh": "完成",
        "hi": "हो गया",
    },
    "Pause": {
        "de": "Pause",
        "es": "Pausa",
        "ko": "일시정지",
        "pt": "Pausar",
        "fr": "Pause",
        "vi": "Tạm dừng",
        "zh": "暂停",
        "hi": "रुकें",
    },
    "Reset": {
        "de": "Zurücksetzen",
        "es": "Restablecer",
        "ko": "초기화",
        "pt": "Redefinir",
        "fr": "Réinitialiser",
        "vi": "Đặt lại",
        "zh": "重置",
        "hi": "रीसेट",
    },
    "Daily Medical Fact": {
        "de": "Medizin-Fakt des Tages",
        "es": "Dato médico del día",
        "ko": "오늘의 의학 사실",
        "pt": "Fato médico do dia",
        "fr": "Fait médical du jour",
        "vi": "Sự kiện y học hôm nay",
        "zh": "今日医学知识",
        "hi": "आज का चिकित्सा तथ्य",
    },
    "Daily General Fact": {
        "de": "Allgemeiner Fakt des Tages",
        "es": "Dato general del día",
        "ko": "오늘의 일반 사실",
        "pt": "Fato geral do dia",
        "fr": "Fait général du jour",
        "vi": "Sự kiện tổng quát hôm nay",
        "zh": "今日常识",
        "hi": "आज का सामान्य तथ्य",
    },
    "Error": {
        "de": "Fehler",
        "es": "Error",
        "ko": "오류",
        "pt": "Erro",
        "fr": "Erreur",
        "vi": "Lỗi",
        "zh": "错误",
        "hi": "त्रुटि",
    },

    # ================================================================= #
    # gamification.py
    # ================================================================= #
    "Unknown Rank": {
        "de": "Unbekannter Rang",
        "es": "Rango desconocido",
        "ko": "알 수 없는 등급",
        "pt": "Rank desconhecido",
        "fr": "Rang inconnu",
        "vi": "Cấp bậc không xác định",
        "zh": "未知等级",
        "hi": "अज्ञात रैंक",
    },
    "Streak: {} days!\n+{} XP Bonus": {
        "de": "Streak: {} Tage!\n+{} XP Bonus",
        "es": "¡Racha: {} días!\n+{} XP de bonificación",
        "ko": "스트릭: {}일!\n+{} XP 보너스",
        "pt": "Sequência: {} dias!\n+{} XP de bônus",
        "fr": "Série : {} jours !\n+{} XP de bonus",
        "vi": "Chuỗi: {} ngày!\n+{} XP thưởng",
        "zh": "连击：{}天！\n+{} XP 奖励",
        "hi": "स्ट्रीक: {} दिन!\n+{} XP बोनस",
    },
    "No challenge available.": {
        "de": "Keine Challenge verfügbar.",
        "es": "No hay ningún reto disponible.",
        "ko": "사용 가능한 챌린지가 없습니다.",
        "pt": "Nenhum desafio disponível.",
        "fr": "Aucun défi disponible.",
        "vi": "Không có thử thách nào.",
        "zh": "暂无挑战。",
        "hi": "कोई चुनौती उपलब्ध नहीं।",
    },
    "Challenge already completed today!": {
        "de": "Challenge heute bereits abgeschlossen!",
        "es": "¡Ya completaste el reto de hoy!",
        "ko": "오늘 챌린지를 이미 완료했습니다!",
        "pt": "Desafio já concluído hoje!",
        "fr": "Défi déjà complété aujourd'hui !",
        "vi": "Thử thách hôm nay đã hoàn thành!",
        "zh": "今日挑战已完成！",
        "hi": "आज की चुनौती पहले ही पूरी हो चुकी है!",
    },
    "Challenge complete! +{} XP": {
        "de": "Challenge abgeschlossen! +{} XP",
        "es": "¡Reto completado! +{} XP",
        "ko": "챌린지 완료! +{} XP",
        "pt": "Desafio concluído! +{} XP",
        "fr": "Défi terminé ! +{} XP",
        "vi": "Hoàn thành thử thách! +{} XP",
        "zh": "挑战完成！+{} XP",
        "hi": "चुनौती पूरी! +{} XP",
    },
    "Streak": {
        "de": "Streak",
        "es": "Racha",
        "ko": "스트릭",
        "pt": "Sequência",
        "fr": "Série",
        "vi": "Chuỗi",
        "zh": "连击",
        "hi": "स्ट्रीक",
    },
    "Daily Challenge": {
        "de": "Tages-Challenge",
        "es": "Reto diario",
        "ko": "오늘의 챌린지",
        "pt": "Desafio diário",
        "fr": "Défi quotidien",
        "vi": "Thử thách hàng ngày",
        "zh": "每日挑战",
        "hi": "दैनिक चुनौती",
    },

    # ================================================================= #
    # sidebar.py
    # ================================================================= #
    "Next Goal": {
        "de": "Nächstes Ziel",
        "es": "Próximo objetivo",
        "ko": "다음 목표",
        "pt": "Próximo objetivo",
        "fr": "Prochain objectif",
        "vi": "Mục tiêu tiếp theo",
        "zh": "下一目标",
        "hi": "अगला लक्ष्य",
    },
    "Loading...": {
        "de": "Lade…",
        "es": "Cargando…",
        "ko": "로드 중…",
        "pt": "Carregando…",
        "fr": "Chargement…",
        "vi": "Đang tải…",
        "zh": "加载中…",
        "hi": "लोड हो रहा है…",
    },
    "Complete Challenge": {
        "de": "Challenge abschließen",
        "es": "Completar reto",
        "ko": "챌린지 완료",
        "pt": "Completar desafio",
        "fr": "Terminer le défi",
        "vi": "Hoàn thành thử thách",
        "zh": "完成挑战",
        "hi": "चुनौती पूरी करें",
    },
    "All Ranks": {
        "de": "Alle Ränge",
        "es": "Todos los rangos",
        "ko": "모든 등급",
        "pt": "Todos os ranks",
        "fr": "Tous les rangs",
        "vi": "Tất cả cấp bậc",
        "zh": "所有等级",
        "hi": "सभी रैंक",
    },
    "How it works": {
        "de": "So funktioniert's",
        "es": "Cómo funciona",
        "ko": "작동 방식",
        "pt": "Como funciona",
        "fr": "Comment ça marche",
        "vi": "Cách hoạt động",
        "zh": "使用说明",
        "hi": "यह कैसे काम करता है",
    },
    "Level {}": {
        "de": "Level {}",
        "es": "Nivel {}",
        "ko": "레벨 {}",
        "pt": "Nível {}",
        "fr": "Niveau {}",
        "vi": "Cấp {}",
        "zh": "等级 {}",
        "hi": "स्तर {}",
    },
    "Level": {
        "de": "Level", "es": "Nivel", "ko": "레벨", "pt": "Nível",
        "fr": "Niveau", "vi": "Cấp độ", "zh": "等级", "hi": "स्तर",
    },
    "{} Day": {
        "de": "{} Tag",
        "es": "{} día",
        "ko": "{}일",
        "pt": "{} dia",
        "fr": "{} jour",
        "vi": "{} ngày",
        "zh": "{} 天",
        "hi": "{} दिन",
    },
    "{} Days": {
        "de": "{} Tage",
        "es": "{} días",
        "ko": "{}일",
        "pt": "{} dias",
        "fr": "{} jours",
        "vi": "{} ngày",
        "zh": "{} 天",
        "hi": "{} दिन",
    },
    "Only {} XP left": {
        "de": "Nur noch {} XP",
        "es": "Solo faltan {} XP",
        "ko": "XP {} 남음",
        "pt": "Faltam {} XP",
        "fr": "Plus que {} XP",
        "vi": "Còn {} XP",
        "zh": "还差 {} XP",
        "hi": "केवल {} XP शेष",
    },
    "Needed for next level: {}": {
        "de": "Für das nächste Level: {}",
        "es": "Necesario para el siguiente nivel: {}",
        "ko": "다음 레벨까지: {}",
        "pt": "Necessário para o próximo nível: {}",
        "fr": "Requis pour le niveau suivant : {}",
        "vi": "Cần cho cấp tiếp theo: {}",
        "zh": "下一等级所需：{}",
        "hi": "अगले स्तर के लिए आवश्यक: {}",
    },
    "Completed": {
        "de": "Abgeschlossen",
        "es": "Completado",
        "ko": "완료",
        "pt": "Concluído",
        "fr": "Terminé",
        "vi": "Đã hoàn thành",
        "zh": "已完成",
        "hi": "पूर्ण",
    },
    "Maximum Rank Achieved!": {
        "de": "Maximalen Rang erreicht!",
        "es": "¡Rango máximo alcanzado!",
        "ko": "최고 등급 달성!",
        "pt": "Rank máximo alcançado!",
        "fr": "Rang maximum atteint !",
        "vi": "Đã đạt cấp bậc tối đa!",
        "zh": "已达最高等级！",
        "hi": "अधिकतम रैंक प्राप्त!",
    },
    "Congratulations!": {
        "de": "Glückwunsch!",
        "es": "¡Felicidades!",
        "ko": "축하합니다!",
        "pt": "Parabéns!",
        "fr": "Félicitations !",
        "vi": "Chúc mừng!",
        "zh": "恭喜！",
        "hi": "बधाई!",
    },
    "Lvl {}+: {}": {
        "de": "Lvl {}+: {}",
        "es": "Nvl {}+: {}",
        "ko": "Lv {}+: {}",
        "pt": "Nv {}+: {}",
        "fr": "Niv {}+ : {}",
        "vi": "Cấp {}+: {}",
        "zh": "等级 {}+：{}",
        "hi": "स्तर {}+: {}",
    },
    "(Locked)": {
        "de": "(Gesperrt)",
        "es": "(Bloqueado)",
        "ko": "(잠김)",
        "pt": "(Bloqueado)",
        "fr": "(Verrouillé)",
        "vi": "(Bị khóa)",
        "zh": "（已锁定）",
        "hi": "(लॉक)",
    },
    "Error: Gamification Manager not available.": {
        "de": "Fehler: Gamification-Manager nicht verfügbar.",
        "es": "Error: el gestor de gamificación no está disponible.",
        "ko": "오류: 게임화 관리자를 사용할 수 없습니다.",
        "pt": "Erro: gerenciador de gamificação não disponível.",
        "fr": "Erreur : le gestionnaire de gamification n'est pas disponible.",
        "vi": "Lỗi: Trình quản lý gamification không khả dụng.",
        "zh": "错误：游戏化管理器不可用。",
        "hi": "त्रुटि: गेमिफिकेशन मैनेजर उपलब्ध नहीं।",
    },
    "An error occurred.": {
        "de": "Ein Fehler ist aufgetreten.",
        "es": "Se ha producido un error.",
        "ko": "오류가 발생했습니다.",
        "pt": "Ocorreu um erro.",
        "fr": "Une erreur est survenue.",
        "vi": "Đã xảy ra lỗi.",
        "zh": "发生了错误。",
        "hi": "एक त्रुटि हुई।",
    },

    # ================================================================= #
    # study_plan_trigger.py
    # ================================================================= #
    "Error triggering Gamification Sidebar action: {}": {
        "de": "Fehler beim Auslösen der Gamification-Sidebar-Aktion: {}",
        "es": "Error al activar la acción de la barra de gamificación: {}",
        "ko": "게임화 사이드바 작업 실행 오류: {}",
        "pt": "Erro ao acionar ação da barra de gamificação: {}",
        "fr": "Erreur lors du déclenchement de l'action de la barre de gamification : {}",
        "vi": "Lỗi kích hoạt hành động thanh gamification: {}",
        "zh": "触发游戏化侧边栏操作时出错：{}",
        "hi": "गेमिफिकेशन साइडबार क्रिया ट्रिगर करने में त्रुटि: {}",
    },
    "Cannot trigger Gamification Sidebar: Function not initialized by main addon.": {
        "de": "Gamification-Sidebar kann nicht ausgelöst werden: Funktion wurde vom Haupt-Add-on nicht initialisiert.",
        "es": "No se puede activar la barra de gamificación: el add-on principal no inicializó la función.",
        "ko": "게임화 사이드바를 실행할 수 없음: 기능이 메인 애드온에 의해 초기화되지 않았습니다.",
        "pt": "Não é possível acionar a barra de gamificação: função não inicializada pelo complemento principal.",
        "fr": "Impossible de déclencher la barre de gamification : fonction non initialisée par le module principal.",
        "vi": "Không thể kích hoạt thanh gamification: chức năng chưa được khởi tạo bởi tiện ích chính.",
        "zh": "无法触发游戏化侧边栏：功能未由主插件初始化。",
        "hi": "गेमिफिकेशन साइडबार ट्रिगर नहीं हो सकती: मुख्य ऐड-ऑन द्वारा फ़ंक्शन प्रारंभ नहीं किया गया।",
    },

    # ================================================================= #
    # deadline_bar.py
    # ================================================================= #
    "Deadline": {
        "de": "Deadline",
        "es": "Fecha límite",
        "ko": "마감일",
        "pt": "Prazo",
        "fr": "Échéance",
        "vi": "Thời hạn",
        "zh": "截止日期",
        "hi": "समयसीमा",
    },
    "Deadline Error": {
        "de": "Deadline-Fehler",
        "es": "Error de fecha límite",
        "ko": "마감일 오류",
        "pt": "Erro de prazo",
        "fr": "Erreur d'échéance",
        "vi": "Lỗi thời hạn",
        "zh": "截止日期错误",
        "hi": "समयसीमा त्रुटि",
    },
    "Error: Start date is after end date": {
        "de": "Fehler: Startdatum liegt nach dem Enddatum",
        "es": "Error: la fecha de inicio es posterior a la de fin",
        "ko": "오류: 시작 날짜가 종료 날짜 이후입니다",
        "pt": "Erro: a data de início é posterior à data de término",
        "fr": "Erreur : la date de début est après la date de fin",
        "vi": "Lỗi: Ngày bắt đầu sau ngày kết thúc",
        "zh": "错误：开始日期晚于结束日期",
        "hi": "त्रुटि: प्रारंभ तिथि समाप्ति तिथि के बाद है",
    },
    "{} | Starts in {} day(s) | Ends in {} day(s)": {
        "de": "{} | Beginnt in {} Tag(en) | Endet in {} Tag(en)",
        "es": "{} | Comienza en {} día(s) | Termina en {} día(s)",
        "ko": "{} | {} 일 후 시작 | {} 일 후 종료",
        "pt": "{} | Começa em {} dia(s) | Termina em {} dia(s)",
        "fr": "{} | Commence dans {} jour(s) | Finit dans {} jour(s)",
        "vi": "{} | Bắt đầu trong {} ngày | Kết thúc trong {} ngày",
        "zh": "{} | {} 天后开始 | {} 天后结束",
        "hi": "{} | {} दिन में शुरू | {} दिन में समाप्त",
    },
    "{} | Ended {} day(s) ago": {
        "de": "{} | Endete vor {} Tag(en)",
        "es": "{} | Terminó hace {} día(s)",
        "ko": "{} | {} 일 전 종료",
        "pt": "{} | Terminou há {} dia(s)",
        "fr": "{} | Terminé il y a {} jour(s)",
        "vi": "{} | Đã kết thúc {} ngày trước",
        "zh": "{} | {} 天前已结束",
        "hi": "{} | {} दिन पहले समाप्त हुआ",
    },
    "{} | {} day(s) remaining": {
        "de": "{} | Noch {} Tag(e)",
        "es": "{} | {} día(s) restantes",
        "ko": "{} | {} 일 남음",
        "pt": "{} | {} dia(s) restante(s)",
        "fr": "{} | {} jour(s) restant(s)",
        "vi": "{} | Còn {} ngày",
        "zh": "{} | 剩余 {} 天",
        "hi": "{} | {} दिन शेष",
    },
    "Error: Invalid date configuration ({})": {
        "de": "Fehler: Ungültige Datumskonfiguration ({})",
        "es": "Error: configuración de fechas no válida ({})",
        "ko": "오류: 잘못된 날짜 설정 ({})",
        "pt": "Erro: configuração de datas inválida ({})",
        "fr": "Erreur : configuration de date invalide ({})",
        "vi": "Lỗi: Cấu hình ngày không hợp lệ ({})",
        "zh": "错误：无效的日期配置（{}）",
        "hi": "त्रुटि: अमान्य दिनांक कॉन्फ़िगरेशन ({})",
    },
    "Error: {}": {
        "de": "Fehler: {}",
        "es": "Error: {}",
        "ko": "오류: {}",
        "pt": "Erro: {}",
        "fr": "Erreur : {}",
        "vi": "Lỗi: {}",
        "zh": "错误：{}",
        "hi": "त्रुटि: {}",
    },

    # ================================================================= #
    # learning_plan.py
    # ================================================================= #

    # ================================================================= #
    # deck_overview.py
    # ================================================================= #
    "{} Cards": {
        "de": "{} Karten",
        "es": "{} tarjetas",
        "ko": "{} 카드",
        "pt": "{} cartões",
        "fr": "{} cartes",
        "vi": "{} thẻ",
        "zh": "{} 张卡片",
        "hi": "{} कार्ड",
    },
    "Progress": {
        "de": "Fortschritt",
        "es": "Progreso",
        "ko": "진행률",
        "pt": "Progresso",
        "fr": "Progression",
        "vi": "Tiến độ",
        "zh": "进度",
        "hi": "प्रगति",
    },
    "Retention": {
        "de": "Behaltensrate",
        "es": "Retención",
        "ko": "기억률",
        "pt": "Retenção",
        "fr": "Rétention",
        "vi": "Tỷ lệ ghi nhớ",
        "zh": "记忆率",
        "hi": "प्रतिधारण",
    },
    "Hard Cards": {
        "de": "Schwere Karten",
        "es": "Tarjetas difíciles",
        "ko": "어려운 카드",
        "pt": "Cartões difíceis",
        "fr": "Cartes difficiles",
        "vi": "Thẻ khó",
        "zh": "困难卡片",
        "hi": "कठिन कार्ड",
    },
    "Finished Cards": {
        "de": "Fertige Karten",
        "es": "Tarjetas terminadas",
        "ko": "완료된 카드",
        "pt": "Cartões concluídos",
        "fr": "Cartes terminées",
        "vi": "Thẻ đã hoàn thành",
        "zh": "已完成卡片",
        "hi": "पूर्ण कार्ड",
    },
    "Click for details": {
        "de": "Für Details klicken",
        "es": "Haz clic para ver los detalles",
        "ko": "자세히 보려면 클릭",
        "pt": "Clique para detalhes",
        "fr": "Cliquez pour les détails",
        "vi": "Nhấn để xem chi tiết",
        "zh": "点击查看详情",
        "hi": "विवरण के लिए क्लिक करें",
    },
    "Generating Brainstorm Cloud...": {
        "de": "Brainstorm-Wolke wird erstellt…",
        "es": "Generando nube de ideas…",
        "ko": "브레인스토밍 클라우드 생성 중…",
        "pt": "Gerando nuvem de ideias…",
        "fr": "Génération du nuage d'idées…",
        "vi": "Đang tạo đám mây từ khóa…",
        "zh": "正在生成词云…",
        "hi": "ब्रेनस्टॉर्म क्लाउड बन रहा है…",
    },
    "Displays the most frequent bold, underlined, or cloze terms in this deck.": {
        "de": "Zeigt die häufigsten fett, unterstrichen oder als Cloze markierten Begriffe in diesem Stapel.",
        "es": "Muestra los términos en negrita, subrayados o cloze más frecuentes de este mazo.",
        "ko": "이 덱에서 가장 자주 나타나는 굵게, 밑줄 또는 빈칸 채우기 용어를 표시합니다.",
        "pt": "Exibe os termos em negrito, sublinhados ou cloze mais frequentes neste baralho.",
        "fr": "Affiche les termes les plus fréquents en gras, soulignés ou cloze dans ce paquet.",
        "vi": "Hiển thị các từ in đậm, gạch chân hoặc cloze xuất hiện nhiều nhất trong bộ thẻ này.",
        "zh": "显示此牌组中出现频率最高的粗体、下划线或填空词汇。",
        "hi": "इस डेक में सबसे अधिक बार आने वाले बोल्ड, रेखांकित या क्लोज़ शब्द दिखाता है।",
    },
    "Deck Brainstorm Cloud": {
        "de": "Stapel-Brainstorm-Wolke",
        "es": "Nube de ideas del mazo",
        "ko": "덱 브레인스토밍 클라우드",
        "pt": "Nuvem de ideias do baralho",
        "fr": "Nuage d'idées du paquet",
        "vi": "Đám mây từ khóa bộ thẻ",
        "zh": "牌组词云",
        "hi": "डेक ब्रेनस्टॉर्म क्लाउड",
    },
    "Start Study": {
        "de": "Lernen starten",
        "es": "Empezar a estudiar",
        "ko": "학습 시작",
        "pt": "Iniciar estudo",
        "fr": "Commencer l'étude",
        "vi": "Bắt đầu học",
        "zh": "开始学习",
        "hi": "अध्ययन शुरू करें",
    },
    "Hard cards are cards you have forgotten 8 or more times.": {
        "de": "Schwere Karten sind Karten, die du 8 oder mehr Mal vergessen hast.",
        "es": "Las tarjetas difíciles son tarjetas que has olvidado 8 o más veces.",
        "ko": "어려운 카드는 8번 이상 잊어버린 카드입니다.",
        "pt": "Cartões difíceis são aqueles que você esqueceu 8 ou mais vezes.",
        "fr": "Les cartes difficiles sont celles que vous avez oubliées 8 fois ou plus.",
        "vi": "Thẻ khó là những thẻ bạn đã quên 8 lần trở lên.",
        "zh": "困难卡片是您忘记了8次或更多次的卡片。",
        "hi": "कठिन कार्ड वे हैं जिन्हें आप 8 या अधिक बार भूल चुके हैं।",
    },
    "Show Hard Cards": {
        "de": "Schwere Karten anzeigen",
        "es": "Mostrar tarjetas difíciles",
        "ko": "어려운 카드 표시",
        "pt": "Mostrar cartões difíceis",
        "fr": "Afficher les cartes difficiles",
        "vi": "Hiển thị thẻ khó",
        "zh": "显示困难卡片",
        "hi": "कठिन कार्ड दिखाएं",
    },
    "Analyzing...": {
        "de": "Analysiere…",
        "es": "Analizando…",
        "ko": "분석 중…",
        "pt": "Analisando…",
        "fr": "Analyse en cours…",
        "vi": "Đang phân tích…",
        "zh": "分析中…",
        "hi": "विश्लेषण हो रहा है…",
    },
    "No marked words found.": {
        "de": "Keine markierten Wörter gefunden.",
        "es": "No se encontraron palabras marcadas.",
        "ko": "표시된 단어가 없습니다.",
        "pt": "Nenhuma palavra marcada encontrada.",
        "fr": "Aucun mot marqué trouvé.",
        "vi": "Không tìm thấy từ nào được đánh dấu.",
        "zh": "未找到标记词汇。",
        "hi": "कोई चिह्नित शब्द नहीं मिला।",
    },
    "Error: wordcloud2.min.js missing in 'media' folder.": {
        "de": "Fehler: wordcloud2.min.js fehlt im 'media'-Ordner.",
        "es": "Error: falta wordcloud2.min.js en la carpeta 'media'.",
        "ko": "오류: 'media' 폴더에 wordcloud2.min.js가 없습니다.",
        "pt": "Erro: wordcloud2.min.js ausente na pasta 'media'.",
        "fr": "Erreur : wordcloud2.min.js manquant dans le dossier 'media'.",
        "vi": "Lỗi: Thiếu wordcloud2.min.js trong thư mục 'media'.",
        "zh": "错误：'media' 文件夹中缺少 wordcloud2.min.js。",
        "hi": "त्रुटि: 'media' फ़ोल्डर में wordcloud2.min.js गायब है।",
    },

    # background_music.py
    "Focus Music": {
        "de": "Fokus-Musik",
        "es": "Música de concentración",
        "ko": "집중 음악",
        "pt": "Música de foco",
        "fr": "Musique de concentration",
        "vi": "Nhạc tập trung",
        "zh": "专注音乐",
        "hi": "फोकस संगीत",
    },
    "Multimedia libs missing.": {
        "de": "Multimedia-Bibliotheken fehlen.",
        "es": "Faltan las bibliotecas multimedia.",
        "ko": "멀티미디어 라이브러리가 없습니다.",
        "pt": "Bibliotecas multimídia ausentes.",
        "fr": "Bibliothèques multimédia manquantes.",
        "vi": "Thiếu thư viện đa phương tiện.",
        "zh": "缺少多媒体库。",
        "hi": "मल्टीमीडिया लाइब्रेरी गायब हैं।",
    },
    "Alpha Waves": {
        "de": "Alpha-Wellen",
        "es": "Ondas alfa",
        "ko": "알파파",
        "pt": "Ondas alfa",
        "fr": "Ondes alpha",
        "vi": "Sóng Alpha",
        "zh": "阿尔法波",
        "hi": "अल्फा तरंगें",
    },
    "Beta Waves": {
        "de": "Beta-Wellen",
        "es": "Ondas beta",
        "ko": "베타파",
        "pt": "Ondas beta",
        "fr": "Ondes bêta",
        "vi": "Sóng Beta",
        "zh": "贝塔波",
        "hi": "बीटा तरंगें",
    },
    "Library": {
        "de": "Bibliothek",
        "es": "Biblioteca",
        "ko": "도서관",
        "pt": "Biblioteca",
        "fr": "Bibliothèque",
        "vi": "Thư viện",
        "zh": "图书馆",
        "hi": "पुस्तकालय",
    },
    "Jazz": {
        "de": "Jazz",
        "es": "Jazz",
        "ko": "재즈",
        "pt": "Jazz",
        "fr": "Jazz",
        "vi": "Jazz",
        "zh": "爵士乐",
        "hi": "जैज़",
    },
    "Rain": {
        "de": "Regen",
        "es": "Lluvia",
        "ko": "빗소리",
        "pt": "Chuva",
        "fr": "Pluie",
        "vi": "Tiếng mưa",
        "zh": "雨声",
        "hi": "बारिश",
    },
    "Cozy": {
        "de": "Gemütlich",
        "es": "Acogedor",
        "ko": "아늑한",
        "pt": "Aconchegante",
        "fr": "Douillet",
        "vi": "Ấm cúng",
        "zh": "舒适",
        "hi": "आरामदायक",
    },

    # help_dialog.py

    # launcher_widget.py
    "Open Add-on Settings": {
        "de": "Add-on-Einstellungen öffnen",
        "es": "Abrir la configuración del complemento",
        "ko": "애드온 설정 열기",
        "pt": "Abrir configurações do complemento",
        "fr": "Ouvrir les paramètres du module",
        "vi": "Mở cài đặt tiện ích",
        "zh": "打开插件设置",
        "hi": "ऐड-ऑन सेटिंग्स खोलें",
    },
    "Start/Pause Timer": {
        "de": "Timer starten/pausieren",
        "es": "Iniciar/pausar temporizador",
        "ko": "타이머 시작/일시정지",
        "pt": "Iniciar/pausar temporizador",
        "fr": "Démarrer/mettre en pause la minuterie",
        "vi": "Bắt đầu/tạm dừng bộ đếm giờ",
        "zh": "开始/暂停计时器",
        "hi": "टाइमर शुरू/रोकें",
    },
    "Reset Timer": {
        "de": "Timer zurücksetzen",
        "es": "Reiniciar temporizador",
        "ko": "타이머 초기화",
        "pt": "Redefinir temporizador",
        "fr": "Réinitialiser la minuterie",
        "vi": "Đặt lại bộ đếm giờ",
        "zh": "重置计时器",
        "hi": "टाइमर रीसेट करें",
    },
    "Skip current phase": {
        "de": "Aktuelle Phase überspringen",
        "es": "Omitir la fase actual",
        "ko": "현재 단계 건너뛰기",
        "pt": "Pular fase atual",
        "fr": "Passer la phase actuelle",
        "vi": "Bỏ qua giai đoạn hiện tại",
        "zh": "跳过当前阶段",
        "hi": "वर्तमान चरण छोड़ें",
    },
    "Timer Settings": {
        "de": "Timer-Einstellungen",
        "es": "Ajustes del temporizador",
        "ko": "타이머 설정",
        "pt": "Configurações do temporizador",
        "fr": "Paramètres de la minuterie",
        "vi": "Cài đặt bộ đếm giờ",
        "zh": "计时器设置",
        "hi": "टाइमर सेटिंग्स",
    },
    "Play Music": {
        "de": "Musik abspielen",
        "es": "Reproducir música",
        "ko": "음악 재생",
        "pt": "Reproduzir música",
        "fr": "Jouer de la musique",
        "vi": "Phát nhạc",
        "zh": "播放音乐",
        "hi": "संगीत चलाएं",
    },

    # mode.py
    "Restart Required": {
        "de": "Neustart erforderlich",
        "es": "Se requiere reiniciar",
        "ko": "재시작 필요",
        "pt": "Reinicialização necessária",
        "fr": "Redémarrage requis",
        "vi": "Cần khởi động lại",
        "zh": "需要重启",
        "hi": "पुनः प्रारंभ आवश्यक",
    },
    "Don't show this message again": {
        "de": "Diese Meldung nicht erneut anzeigen",
        "es": "No volver a mostrar este mensaje",
        "ko": "이 메시지를 다시 표시하지 않기",
        "pt": "Não mostrar esta mensagem novamente",
        "fr": "Ne plus afficher ce message",
        "vi": "Không hiển thị lại thông báo này",
        "zh": "不再显示此消息",
        "hi": "यह संदेश दोबारा न दिखाएँ",
    },
    "<b>Theme Change Detected</b><br><br>You have switched between Light and Dark mode.<br>To ensure all Smart Study UI elements and styles are applied correctly, please restart Anki.": {
        "de": "<b>Theme-Wechsel erkannt</b><br><br>Du hast zwischen hellem und dunklem Modus gewechselt.<br>Damit alle Smart Study-UI-Elemente und -Stile korrekt übernommen werden, starte Anki bitte neu.",
        "es": "<b>Cambio de tema detectado</b><br><br>Has cambiado entre el modo claro y el oscuro.<br>Para asegurar que todos los elementos y estilos de la interfaz de Smart Study se apliquen correctamente, reinicia Anki.",
        "ko": "<b>테마 변경 감지됨</b><br><br>라이트 모드와 다크 모드 간 전환이 감지되었습니다.<br>Smart Study UI 요소 및 스타일을 올바르게 적용하려면 Anki를 다시 시작하세요.",
        "pt": "<b>Alteração de tema detectada</b><br><br>Você alternou entre o modo claro e escuro.<br>Para garantir que todos os elementos e estilos da interface do Smart Study sejam aplicados corretamente, reinicie o Anki.",
        "fr": "<b>Changement de thème détecté</b><br><br>Vous avez basculé entre le mode clair et sombre.<br>Pour s'assurer que tous les éléments et styles de l'interface Smart Study sont correctement appliqués, veuillez redémarrer Anki.",
        "vi": "<b>Phát hiện thay đổi giao diện</b><br><br>Bạn đã chuyển đổi giữa chế độ sáng và tối.<br>Để đảm bảo tất cả thành phần giao diện Smart Study được áp dụng đúng, hãy khởi động lại Anki.",
        "zh": "<b>检测到主题变更</b><br><br>您在浅色模式和深色模式之间进行了切换。<br>为确保所有 Smart Study 界面元素和样式正确应用，请重启 Anki。",
        "hi": "<b>थीम परिवर्तन का पता चला</b><br><br>आपने लाइट और डार्क मोड के बीच स्विच किया है।<br>सभी Smart Study UI तत्वों और स्टाइल्स को सही से लागू करने के लिए कृपया Anki पुनः प्रारंभ करें।",
    },

    # pomodoro.py
    "Pomodoro": {
        "de": "Pomodoro",
        "es": "Pomodoro",
        "ko": "포모도로",
        "pt": "Pomodoro",
        "fr": "Pomodoro",
        "vi": "Pomodoro",
        "zh": "番茄钟",
        "hi": "पोमोडोरो",
    },
    "Pomodoro Settings": {
        "de": "Pomodoro-Einstellungen",
        "es": "Ajustes del Pomodoro",
        "ko": "포모도로 설정",
        "pt": "Configurações do Pomodoro",
        "fr": "Paramètres Pomodoro",
        "vi": "Cài đặt Pomodoro",
        "zh": "番茄钟设置",
        "hi": "पोमोडोरो सेटिंग्स",
    },
    "Pomodoro settings saved.": {
        "de": "Pomodoro-Einstellungen gespeichert.",
        "es": "Ajustes del Pomodoro guardados.",
        "ko": "포모도로 설정이 저장되었습니다.",
        "pt": "Configurações do Pomodoro salvas.",
        "fr": "Paramètres Pomodoro enregistrés.",
        "vi": "Đã lưu cài đặt Pomodoro.",
        "zh": "番茄钟设置已保存。",
        "hi": "पोमोडोरो सेटिंग्स सहेजी गईं।",
    },
    "Work Duration:": {
        "de": "Arbeitsdauer:",
        "es": "Duración del trabajo:",
        "ko": "작업 시간:",
        "pt": "Duração do trabalho:",
        "fr": "Durée de travail :",
        "vi": "Thời gian làm việc:",
        "zh": "工作时长：",
        "hi": "कार्य अवधि:",
    },
    "Short Break:": {
        "de": "Kurze Pause:",
        "es": "Descanso corto:",
        "ko": "짧은 휴식:",
        "pt": "Pausa curta:",
        "fr": "Pause courte :",
        "vi": "Nghỉ ngắn:",
        "zh": "短休息：",
        "hi": "छोटा ब्रेक:",
    },
    "Long Break:": {
        "de": "Lange Pause:",
        "es": "Descanso largo:",
        "ko": "긴 휴식:",
        "pt": "Pausa longa:",
        "fr": "Pause longue :",
        "vi": "Nghỉ dài:",
        "zh": "长休息：",
        "hi": "लंबा ब्रेक:",
    },
    "Intervals per Cycle:": {
        "de": "Intervalle pro Zyklus:",
        "es": "Intervalos por ciclo:",
        "ko": "사이클당 간격:",
        "pt": "Intervalos por ciclo:",
        "fr": "Intervalles par cycle :",
        "vi": "Khoảng thời gian mỗi chu kỳ:",
        "zh": "每周期间隔数：",
        "hi": "प्रति चक्र अंतराल:",
    },
    "Auto-start next timer": {
        "de": "Nächsten Timer automatisch starten",
        "es": "Iniciar el siguiente temporizador automáticamente",
        "ko": "다음 타이머 자동 시작",
        "pt": "Iniciar próximo temporizador automaticamente",
        "fr": "Démarrer automatiquement la prochaine minuterie",
        "vi": "Tự động bắt đầu bộ đếm giờ tiếp theo",
        "zh": "自动开始下一个计时器",
        "hi": "अगला टाइमर स्वचालित रूप से शुरू करें",
    },
    " min": {
        "de": " Min",
        "es": " min",
        "ko": " 분",
        "pt": " min",
        "fr": " min",
        "vi": " phút",
        "zh": " 分钟",
        "hi": " मि.",
    },
    "Work session finished! ({}/{})": {
        "de": "Arbeitssitzung beendet! ({}/{})",
        "es": "¡Sesión de trabajo terminada! ({}/{})",
        "ko": "작업 세션 완료! ({}/{})",
        "pt": "Sessão de trabalho concluída! ({}/{})",
        "fr": "Session de travail terminée ! ({}/{})",
        "vi": "Phiên làm việc hoàn thành! ({}/{})",
        "zh": "工作会话完成！（{}/{}）",
        "hi": "कार्य सत्र समाप्त! ({}/{})",
    },
    "\nNext: Long Break!": {
        "de": "\nAls Nächstes: Lange Pause!",
        "es": "\nA continuación: ¡descanso largo!",
        "ko": "\n다음: 긴 휴식!",
        "pt": "\nA seguir: Pausa longa!",
        "fr": "\nSuivant : Pause longue !",
        "vi": "\nTiếp theo: Nghỉ dài!",
        "zh": "\n下一步：长休息！",
        "hi": "\nआगे: लंबा ब्रेक!",
    },
    "\nNext: Short Break!": {
        "de": "\nAls Nächstes: Kurze Pause!",
        "es": "\nA continuación: ¡descanso corto!",
        "ko": "\n다음: 짧은 휴식!",
        "pt": "\nA seguir: Pausa curta!",
        "fr": "\nSuivant : Pause courte !",
        "vi": "\nTiếp theo: Nghỉ ngắn!",
        "zh": "\n下一步：短休息！",
        "hi": "\nआगे: छोटा ब्रेक!",
    },
    "Break finished!\nNext: Work": {
        "de": "Pause beendet!\nAls Nächstes: Arbeit",
        "es": "¡Descanso terminado!\nA continuación: trabajo",
        "ko": "휴식 완료!\n다음: 작업",
        "pt": "Pausa concluída!\nA seguir: Trabalho",
        "fr": "Pause terminée !\nSuivant : Travail",
        "vi": "Nghỉ xong!\nTiếp theo: Làm việc",
        "zh": "休息结束！\n下一步：工作",
        "hi": "ब्रेक समाप्त!\nआगे: काम",
    },
    "Pomodoro: Error playing '{}': {}": {
        "de": "Pomodoro: Fehler beim Abspielen von '{}': {}",
        "es": "Pomodoro: error al reproducir '{}': {}",
        "ko": "포모도로: '{}' 재생 오류: {}",
        "pt": "Pomodoro: erro ao reproduzir '{}': {}",
        "fr": "Pomodoro : erreur lors de la lecture de '{}' : {}",
        "vi": "Pomodoro: Lỗi phát '{}': {}",
        "zh": "番茄钟：播放 '{}' 时出错：{}",
        "hi": "Pomodoro: '{}' चलाने में त्रुटि: {}",
    },
    "Pomodoro: Sound file '{}' not found in folder '{}'.": {
        "de": "Pomodoro: Sounddatei '{}' im Ordner '{}' nicht gefunden.",
        "es": "Pomodoro: no se encontró el archivo de sonido '{}' en la carpeta '{}'.",
        "ko": "포모도로: '{}' 폴더에서 사운드 파일 '{}'을(를) 찾을 수 없습니다.",
        "pt": "Pomodoro: arquivo de som '{}' não encontrado na pasta '{}'.",
        "fr": "Pomodoro : fichier son '{}' introuvable dans le dossier '{}'.",
        "vi": "Pomodoro: Không tìm thấy tệp âm thanh '{}' trong thư mục '{}'.",
        "zh": "番茄钟：在文件夹 '{}' 中找不到声音文件 '{}'。",
        "hi": "Pomodoro: फ़ोल्डर '{}' में ध्वनि फ़ाइल '{}' नहीं मिली।",
    },

    # pomodoro.py – Statistics tab
    "Statistics": {
        "de": "Statistiken",
        "es": "Estadísticas",
        "ko": "통계",
        "pt": "Estatísticas",
        "fr": "Statistiques",
        "vi": "Thống kê",
        "zh": "统计",
        "hi": "सांख्यिकी",
    },
    "Total Pomodoros": {
        "de": "Gesamt Pomodoros",
        "es": "Pomodoros totales",
        "ko": "총 포모도로",
        "pt": "Total de Pomodoros",
        "fr": "Total Pomodoros",
        "vi": "Tổng số Pomodoro",
        "zh": "总番茄钟数",
        "hi": "कुल पोमोडोरो",
    },
    "Focus Time": {
        "de": "Fokuszeit",
        "es": "Tiempo de enfoque",
        "ko": "집중 시간",
        "pt": "Tempo de foco",
        "fr": "Temps de concentration",
        "vi": "Thời gian tập trung",
        "zh": "专注时间",
        "hi": "फोकस समय",
    },
    "Current Streak": {
        "de": "Aktuelle Serie",
        "es": "Racha actual",
        "ko": "현재 연속",
        "pt": "Sequência atual",
        "fr": "Série actuelle",
        "vi": "Chuỗi hiện tại",
        "zh": "当前连续",
        "hi": "वर्तमान क्रम",
    },
    "Best Streak": {
        "de": "Beste Serie",
        "es": "Mejor racha",
        "ko": "최고 연속",
        "pt": "Melhor sequência",
        "fr": "Meilleure série",
        "vi": "Chuỗi tốt nhất",
        "zh": "最佳连续",
        "hi": "सर्वश्रेष्ठ क्रम",
    },
    "Last 7 Days": {
        "de": "Letzte 7 Tage",
        "es": "Últimos 7 días",
        "ko": "최근 7일",
        "pt": "Últimos 7 dias",
        "fr": "7 derniers jours",
        "vi": "7 ngày qua",
        "zh": "过去7天",
        "hi": "पिछले 7 दिन",
    },
    "Today": {
        "de": "Heute",
        "es": "Hoy",
        "ko": "오늘",
        "pt": "Hoje",
        "fr": "Aujourd'hui",
        "vi": "Hôm nay",
        "zh": "今天",
        "hi": "आज",
    },
    "Reset Statistics": {
        "de": "Statistiken zurücksetzen",
        "es": "Restablecer estadísticas",
        "ko": "통계 초기화",
        "pt": "Redefinir estatísticas",
        "fr": "Réinitialiser les statistiques",
        "vi": "Đặt lại thống kê",
        "zh": "重置统计",
        "hi": "सांख्यिकी रीसेट करें",
    },
    "Are you sure you want to reset all Pomodoro statistics?": {
        "de": "Möchtest du wirklich alle Pomodoro-Statistiken zurücksetzen?",
        "es": "¿Estás seguro de que quieres restablecer todas las estadísticas de Pomodoro?",
        "ko": "모든 포모도로 통계를 초기화하시겠습니까?",
        "pt": "Tem certeza de que deseja redefinir todas as estatísticas do Pomodoro?",
        "fr": "Êtes-vous sûr de vouloir réinitialiser toutes les statistiques Pomodoro ?",
        "vi": "Bạn có chắc muốn đặt lại tất cả thống kê Pomodoro?",
        "zh": "确定要重置所有番茄钟统计数据吗？",
        "hi": "क्या आप सभी पोमोडोरो सांख्यिकी रीसेट करना चाहते हैं?",
    },
    "Statistics reset.": {
        "de": "Statistiken zurückgesetzt.",
        "es": "Estadísticas restablecidas.",
        "ko": "통계가 초기화되었습니다.",
        "pt": "Estatísticas redefinidas.",
        "fr": "Statistiques réinitialisées.",
        "vi": "Đã đặt lại thống kê.",
        "zh": "统计已重置。",
        "hi": "सांख्यिकी रीसेट हुई।",
    },
    # Short weekday labels used in the bar chart
    "Mon": {
        "de": "Mo",
        "es": "Lun",
        "ko": "월",
        "pt": "Seg",
        "fr": "Lun",
        "vi": "T2",
        "zh": "周一",
        "hi": "सो",
    },
    "Tue": {
        "de": "Di",
        "es": "Mar",
        "ko": "화",
        "pt": "Ter",
        "fr": "Mar",
        "vi": "T3",
        "zh": "周二",
        "hi": "मं",
    },
    "Wed": {
        "de": "Mi",
        "es": "Mié",
        "ko": "수",
        "pt": "Qua",
        "fr": "Mer",
        "vi": "T4",
        "zh": "周三",
        "hi": "बु",
    },
    "Thu": {
        "de": "Do",
        "es": "Jue",
        "ko": "목",
        "pt": "Qui",
        "fr": "Jeu",
        "vi": "T5",
        "zh": "周四",
        "hi": "गु",
    },
    "Fri": {
        "de": "Fr",
        "es": "Vie",
        "ko": "금",
        "pt": "Sex",
        "fr": "Ven",
        "vi": "T6",
        "zh": "周五",
        "hi": "शु",
    },
    "Sat": {
        "de": "Sa",
        "es": "Sáb",
        "ko": "토",
        "pt": "Sáb",
        "fr": "Sam",
        "vi": "T7",
        "zh": "周六",
        "hi": "श",
    },
    "Sun": {
        "de": "So",
        "es": "Dom",
        "ko": "일",
        "pt": "Dom",
        "fr": "Dim",
        "vi": "CN",
        "zh": "周日",
        "hi": "र",
    },

    # ------------------------------------------------------------------
    # statistics_widget.py
    # ------------------------------------------------------------------
    "Last {} days": {
        "de": "Letzte {} Tage",
        "es": "Últimos {} días",
        "ko": "최근 {} 일",
        "pt": "Últimos {} dias",
        "fr": "{} derniers jours",
        "vi": "{} ngày qua",
        "zh": "过去 {} 天",
        "hi": "पिछले {} दिन",
    },

    # ------------------------------------------------------------------
    # settings_dialog.py – Themes card + theme_editor_dialog.py
    # ------------------------------------------------------------------
    "Edit Theme": {
        "de": "Theme bearbeiten",
        "es": "Editar tema",
        "ko": "테마 편집",
        "pt": "Editar tema",
        "fr": "Modifier le thème",
        "vi": "Chỉnh sửa giao diện",
        "zh": "编辑主题",
        "hi": "थीम संपादित करें",
    },
    # ── theme_editor_dialog.py ─────────────────────────────────────────
    "Theme Editor": {
        "de": "Theme-Editor",
        "es": "Editor de temas",
        "ko": "테마 편집기",
        "pt": "Editor de temas",
        "fr": "Éditeur de thèmes",
        "vi": "Trình chỉnh sửa giao diện",
        "zh": "主题编辑器",
        "hi": "थीम संपादक",
    },
    "Quick Presets": {
        "de": "Vorlagen",
        "es": "Plantillas",
        "ko": "빠른 프리셋",
        "pt": "Predefinições rápidas",
        "fr": "Préréglages rapides",
        "vi": "Cài đặt sẵn nhanh",
        "zh": "快速预设",
        "hi": "त्वरित प्रीसेट",
    },
    "Custom Colors": {
        "de": "Farben anpassen",
        "es": "Colores personalizados",
        "ko": "커스텀 색상",
        "pt": "Cores personalizadas",
        "fr": "Couleurs personnalisées",
        "vi": "Màu sắc tùy chỉnh",
        "zh": "自定义颜色",
        "hi": "कस्टम रंग",
    },
    "Primary color": {
        "de": "Primärfarbe",
        "es": "Color primario",
        "ko": "기본 색상",
        "pt": "Cor primária",
        "fr": "Couleur principale",
        "vi": "Màu chính",
        "zh": "主色",
        "hi": "प्राथमिक रंग",
    },
    "Hover color": {
        "de": "Hover-Farbe",
        "es": "Color al pasar el ratón",
        "ko": "호버 색상",
        "pt": "Cor ao passar o mouse",
        "fr": "Couleur au survol",
        "vi": "Màu khi di chuột",
        "zh": "悬停颜色",
        "hi": "होवर रंग",
    },
    "Pressed color": {
        "de": "Gedrückt-Farbe",
        "es": "Color al presionar",
        "ko": "눌림 색상",
        "pt": "Cor ao pressionar",
        "fr": "Couleur enfoncé",
        "vi": "Màu khi nhấn",
        "zh": "按下颜色",
        "hi": "दबाया रंग",
    },
    "Bright accent": {
        "de": "Heller Akzent",
        "es": "Acento claro",
        "ko": "밝은 강조",
        "pt": "Destaque claro",
        "fr": "Accent lumineux",
        "vi": "Màu nhấn sáng",
        "zh": "亮色强调",
        "hi": "चमकीला उच्चारण",
    },
    "Click to choose a color": {
        "de": "Klicken, um eine Farbe zu wählen",
        "es": "Clic para elegir un color",
        "ko": "색상을 선택하려면 클릭",
        "pt": "Clique para escolher uma cor",
        "fr": "Cliquez pour choisir une couleur",
        "vi": "Nhấn để chọn màu",
        "zh": "点击选择颜色",
        "hi": "रंग चुनने के लिए क्लिक करें",
    },
    "Colors apply to both Light and Dark mode.": {
        "de": "Farben gelten für Light- und Dark-Mode gleichermaßen.",
        "es": "Los colores se aplican tanto al modo claro como al oscuro.",
        "ko": "색상은 라이트 모드와 다크 모드 모두에 적용됩니다.",
        "pt": "As cores se aplicam tanto ao modo claro quanto ao escuro.",
        "fr": "Les couleurs s'appliquent aux modes clair et sombre.",
        "vi": "Màu sắc áp dụng cho cả chế độ sáng và tối.",
        "zh": "颜色同时适用于浅色和深色模式。",
        "hi": "रंग लाइट और डार्क दोनों मोड पर लागू होते हैं।",
    },
    "Apply": {
        "de": "Übernehmen",
        "es": "Aplicar",
        "ko": "적용",
        "pt": "Aplicar",
        "fr": "Appliquer",
        "vi": "Áp dụng",
        "zh": "应用",
        "hi": "लागू करें",
    },

    # ------------------------------------------------------------------
    # notebook_sidebar.py
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # website_sidebar.py
    # ------------------------------------------------------------------
    "Limit of {} custom sites reached.": {
        "de": "Grenze von {} benutzerdefinierten Seiten erreicht.",
        "es": "Se alcanzó el límite de {} sitios personalizados.",
        "ko": "{} 개의 커스텀 사이트 한도에 도달했습니다.",
        "pt": "Limite de {} sites personalizados atingido.",
        "fr": "Limite de {} sites personnalisés atteinte.",
        "vi": "Đã đạt giới hạn {} trang tùy chỉnh.",
        "zh": "已达到 {} 个自定义网站的限制。",
        "hi": "{} कस्टम साइट की सीमा पहुंच गई।",
    },
    "Add Website": {
        "de": "Website hinzufügen",
        "es": "Añadir sitio web",
        "ko": "웹사이트 추가",
        "pt": "Adicionar site",
        "fr": "Ajouter un site web",
        "vi": "Thêm trang web",
        "zh": "添加网站",
        "hi": "वेबसाइट जोड़ें",
    },
    "Name for the new button:": {
        "de": "Name für den neuen Button:",
        "es": "Nombre del nuevo botón:",
        "ko": "새 버튼 이름:",
        "pt": "Nome para o novo botão:",
        "fr": "Nom du nouveau bouton :",
        "vi": "Tên cho nút mới:",
        "zh": "新按钮的名称：",
        "hi": "नए बटन के लिए नाम:",
    },
    "URL for '{}':": {
        "de": "URL für '{}':",
        "es": "URL para '{}':",
        "ko": "'{}'의 URL:",
        "pt": "URL para '{}':",
        "fr": "URL pour '{}' :",
        "vi": "URL cho '{}':",
        "zh": "'{}'的 URL：",
        "hi": "'{}' के लिए URL:",
    },
    "URL automatically prefixed with https://": {
        "de": "URL automatisch mit https:// ergänzt",
        "es": "URL completada automáticamente con https://",
        "ko": "URL에 https://가 자동으로 추가됩니다",
        "pt": "URL prefixada automaticamente com https://",
        "fr": "URL préfixée automatiquement avec https://",
        "vi": "URL tự động thêm tiền tố https://",
        "zh": "URL 自动添加 https:// 前缀",
        "hi": "URL स्वचालित रूप से https:// से शुरू होती है",
    },
    "URL '{}' seems invalid.": {
        "de": "URL '{}' scheint ungültig zu sein.",
        "es": "La URL '{}' parece no ser válida.",
        "ko": "URL '{}'이 유효하지 않은 것 같습니다.",
        "pt": "A URL '{}' parece inválida.",
        "fr": "L'URL '{}' semble invalide.",
        "vi": "URL '{}' có vẻ không hợp lệ.",
        "zh": "URL '{}' 似乎无效。",
        "hi": "URL '{}' अमान्य लगती है।",
    },
    "Site '{}' added.": {
        "de": "Seite '{}' hinzugefügt.",
        "es": "Sitio '{}' añadido.",
        "ko": "사이트 '{}'이 추가되었습니다.",
        "pt": "Site '{}' adicionado.",
        "fr": "Site '{}' ajouté.",
        "vi": "Đã thêm trang '{}'.",
        "zh": "网站 '{}' 已添加。",
        "hi": "साइट '{}' जोड़ी गई।",
    },
    "Site '{}' removed.": {
        "de": "Seite '{}' entfernt.",
        "es": "Sitio '{}' eliminado.",
        "ko": "사이트 '{}'이 삭제되었습니다.",
        "pt": "Site '{}' removido.",
        "fr": "Site '{}' supprimé.",
        "vi": "Đã xóa trang '{}'.",
        "zh": "网站 '{}' 已删除。",
        "hi": "साइट '{}' हटाई गई।",
    },
    "Could not delete site: Invalid index.": {
        "de": "Seite konnte nicht gelöscht werden: Ungültiger Index.",
        "es": "No se pudo eliminar el sitio: índice no válido.",
        "ko": "사이트를 삭제할 수 없습니다: 잘못된 인덱스.",
        "pt": "Não foi possível excluir o site: índice inválido.",
        "fr": "Impossible de supprimer le site : index invalide.",
        "vi": "Không thể xóa trang: chỉ mục không hợp lệ.",
        "zh": "无法删除网站：索引无效。",
        "hi": "साइट हटाई नहीं जा सकी: अमान्य इंडेक्स।",
    },
    """
        <body style='font-family: sans-serif; padding: 20px; color: #333; background-color: #f9f9f9;'>
            <h2 style='color: #d32f2f;'>Invalid URL</h2>
            <p>The URL you tried to open seems to be invalid or is not a standard web URL (http/https).</p>
            <p>Attempted URL: <code>{url_str}</code></p>
        </body>""": {
        "de": """
        <body style='font-family: sans-serif; padding: 20px; color: #333; background-color: #f9f9f9;'>
            <h2 style='color: #d32f2f;'>Ungültige URL</h2>
            <p>Die URL, die Du öffnen wolltest, scheint ungültig oder keine Standard-Web-URL (http/https) zu sein.</p>
            <p>Versuchte URL: <code>{url_str}</code></p>
        </body>""",
        "es": """
        <body style='font-family: sans-serif; padding: 20px; color: #333; background-color: #f9f9f9;'>
            <h2 style='color: #d32f2f;'>URL no válida</h2>
            <p>La URL que intentaste abrir parece no ser válida o no es una URL estándar de la web (http/https).</p>
            <p>URL intentada: <code>{url_str}</code></p>
        </body>""",
        "ko": """
        <body style='font-family: sans-serif; padding: 20px; color: #333; background-color: #f9f9f9;'>
            <h2 style='color: #d32f2f;'>유효하지 않은 URL</h2>
            <p>열려고 한 URL이 유효하지 않거나 표준 웹 URL(http/https)이 아닌 것 같습니다.</p>
            <p>시도한 URL: <code>{url_str}</code></p>
        </body>""",
        "pt": """
        <body style='font-family: sans-serif; padding: 20px; color: #333; background-color: #f9f9f9;'>
            <h2 style='color: #d32f2f;'>URL Inválida</h2>
            <p>A URL que você tentou abrir parece inválida ou não é uma URL web padrão (http/https).</p>
            <p>URL tentada: <code>{url_str}</code></p>
        </body>""",
        "fr": """
        <body style='font-family: sans-serif; padding: 20px; color: #333; background-color: #f9f9f9;'>
            <h2 style='color: #d32f2f;'>URL invalide</h2>
            <p>L'URL que vous avez essayé d'ouvrir semble invalide ou n'est pas une URL web standard (http/https).</p>
            <p>URL tentée : <code>{url_str}</code></p>
        </body>""",
        "vi": """
        <body style='font-family: sans-serif; padding: 20px; color: #333; background-color: #f9f9f9;'>
            <h2 style='color: #d32f2f;'>URL không hợp lệ</h2>
            <p>URL bạn cố mở có vẻ không hợp lệ hoặc không phải URL web tiêu chuẩn (http/https).</p>
            <p>URL đã thử: <code>{url_str}</code></p>
        </body>""",
        "zh": """
        <body style='font-family: sans-serif; padding: 20px; color: #333; background-color: #f9f9f9;'>
            <h2 style='color: #d32f2f;'>无效 URL</h2>
            <p>您尝试打开的 URL 似乎无效或不是标准 Web URL（http/https）。</p>
            <p>尝试的 URL：<code>{url_str}</code></p>
        </body>""",
        "hi": """
        <body style='font-family: sans-serif; padding: 20px; color: #333; background-color: #f9f9f9;'>
            <h2 style='color: #d32f2f;'>अमान्य URL</h2>
            <p>आपने जो URL खोलने की कोशिश की वह अमान्य लगती है या मानक वेब URL (http/https) नहीं है।</p>
            <p>प्रयास की गई URL: <code>{url_str}</code></p>
        </body>""",
    },
    "Add new website": {
        "de": "Neue Website hinzufügen",
        "es": "Añadir nuevo sitio web",
        "ko": "새 웹사이트 추가",
        "pt": "Adicionar novo site",
        "fr": "Ajouter un nouveau site web",
        "vi": "Thêm trang web mới",
        "zh": "添加新网站",
        "hi": "नई वेबसाइट जोड़ें",
    },
    "Maximum {} custom sites reached": {
        "de": "Maximum von {} benutzerdefinierten Seiten erreicht",
        "es": "Se alcanzó el máximo de {} sitios personalizados",
        "ko": "최대 {} 개의 커스텀 사이트에 도달했습니다",
        "pt": "Máximo de {} sites personalizados atingido",
        "fr": "Maximum de {} sites personnalisés atteint",
        "vi": "Đã đạt tối đa {} trang tùy chỉnh",
        "zh": "已达到 {} 个自定义网站上限",
        "hi": "{} कस्टम साइट की अधिकतम सीमा पहुंच गई",
    },
    "Remove '{}'": {
        "de": "'{}' entfernen",
        "es": "Eliminar '{}'",
        "ko": "'{}' 제거",
        "pt": "Remover '{}'",
        "fr": "Supprimer '{}'",
        "vi": "Xóa '{}'",
        "zh": "删除 '{}'",
        "hi": "'{}' हटाएं",
    },
    "Web Sidebar": {
        "de": "Web-Seitenleiste",
        "es": "Barra lateral web",
        "ko": "웹 사이드바",
        "pt": "Barra lateral web",
        "fr": "Barre latérale web",
        "vi": "Thanh bên web",
        "zh": "网页侧边栏",
        "hi": "वेब साइडबार",
    },
    "Home": {
        "de": "Start",
        "es": "Inicio",
        "ko": "홈",
        "pt": "Início",
        "fr": "Accueil",
        "vi": "Trang chủ",
        "zh": "主页",
        "hi": "होम",
    },
    "Home (Smart Study Browser)": {
        "de": "Start (Smart Study-Browser)",
        "es": "Inicio (navegador Smart Study)",
        "ko": "홈 (Smart Study 브라우저)",
        "pt": "Início (Navegador Smart Study)",
        "fr": "Accueil (Navigateur Smart Study)",
        "vi": "Trang chủ (Trình duyệt Smart Study)",
        "zh": "主页（Smart Study 浏览器）",
        "hi": "होम (Smart Study ब्राउज़र)",
    },
    "Go Back": {
        "de": "Zurück",
        "es": "Atrás",
        "ko": "뒤로",
        "pt": "Voltar",
        "fr": "Retour",
        "vi": "Quay lại",
        "zh": "后退",
        "hi": "पीछे जाएं",
    },
    "Go Forward": {
        "de": "Vor",
        "es": "Adelante",
        "ko": "앞으로",
        "pt": "Avançar",
        "fr": "Avancer",
        "vi": "Tiến lên",
        "zh": "前进",
        "hi": "आगे जाएं",
    },
    "Reload Page": {
        "de": "Seite neu laden",
        "es": "Recargar página",
        "ko": "페이지 새로고침",
        "pt": "Recarregar página",
        "fr": "Recharger la page",
        "vi": "Tải lại trang",
        "zh": "重新加载页面",
        "hi": "पृष्ठ पुनः लोड करें",
    },
    "Website Sidebar: Qt components not available.": {
        "de": "Website-Seitenleiste: Qt-Komponenten nicht verfügbar.",
        "es": "Barra lateral de sitios web: los componentes de Qt no están disponibles.",
        "ko": "웹사이트 사이드바: Qt 컴포넌트를 사용할 수 없습니다.",
        "pt": "Barra lateral de sites: componentes Qt não disponíveis.",
        "fr": "Barre latérale web : composants Qt non disponibles.",
        "vi": "Thanh bên trang web: Các thành phần Qt không khả dụng.",
        "zh": "网页侧边栏：Qt 组件不可用。",
        "hi": "वेबसाइट साइडबार: Qt घटक उपलब्ध नहीं हैं।",
    },
    "{}:\nCould not create or find the website sidebar.": {
        "de": "{}:\nWebsite-Seitenleiste konnte nicht erstellt oder gefunden werden.",
        "es": "{}:\nNo se pudo crear o encontrar la barra lateral de sitios web.",
        "ko": "{}:\n웹사이트 사이드바를 만들거나 찾을 수 없습니다.",
        "pt": "{}:\nNão foi possível criar ou encontrar a barra lateral de sites.",
        "fr": "{}:\nImpossible de créer ou de trouver la barre latérale web.",
        "vi": "{}:\nKhông thể tạo hoặc tìm thanh bên trang web.",
        "zh": "{}:\n无法创建或找到网页侧边栏。",
        "hi": "{}:\nवेबसाइट साइडबार बनाया या मिला नहीं।",
    },
    "Sidebar Browser not initialized.": {
        "de": "Seitenleisten-Browser nicht initialisiert.",
        "es": "El navegador de la barra lateral no está inicializado.",
        "ko": "사이드바 브라우저가 초기화되지 않았습니다.",
        "pt": "Navegador da barra lateral não inicializado.",
        "fr": "Navigateur de la barre latérale non initialisé.",
        "vi": "Trình duyệt thanh bên chưa được khởi tạo.",
        "zh": "侧边栏浏览器未初始化。",
        "hi": "साइडबार ब्राउज़र प्रारंभ नहीं हुआ।",
    },
    "Search '{}' in Sidebar": {
        "de": "'{}' in der Seitenleiste suchen",
        "es": "Buscar '{}' en la barra lateral",
        "ko": "사이드바에서 '{}' 검색",
        "pt": "Pesquisar '{}' na barra lateral",
        "fr": "Rechercher '{}' dans la barre latérale",
        "vi": "Tìm '{}' trong thanh bên",
        "zh": "在侧边栏搜索 '{}'",
        "hi": "साइडबार में '{}' खोजें",
    },

    # ------------------------------------------------------------------
    # ai_assistant.py
    # ------------------------------------------------------------------
    "OK": {
        "de": "OK",
        "es": "Aceptar",
        "ko": "확인",
        "pt": "OK",
        "fr": "OK",
        "vi": "OK",
        "zh": "确认",
        "hi": "ठीक है",
    },
    "Help": {
        "de": "Hilfe",
        "es": "Ayuda",
        "ko": "도움말",
        "pt": "Ajuda",
        "fr": "Aide",
        "vi": "Trợ giúp",
        "zh": "帮助",
        "hi": "सहायता",
    },
    "Copy": {
        "de": "Kopieren",
        "es": "Copiar",
        "ko": "복사",
        "pt": "Copiar",
        "fr": "Copier",
        "vi": "Sao chép",
        "zh": "复制",
        "hi": "कॉपी करें",
    },

    # ================================================================= #
    # Daily Challenges  (gamification.py – DAILY_CHALLENGES[i]["text"])
    # ================================================================= #

    # ================================================================= #
    # Daily Medical Facts  (daily_widgets.py – MEDICAL_FACTS[i]["text"])
    # ================================================================= #
    "Did you know? Your brain consumes a significant amount of energy, about 20% of your body's total supply, despite only accounting for roughly 2% of your total body weight.": {
        "de": "Dein Gehirn verbraucht ~20 % der Körperenergie, obwohl es nur ~2 % des Körpergewichts ausmacht.",
        "es": "Tu cerebro consume el ~20 % de la energía corporal, aunque representa solo el ~2 % del peso.",
        "ko": "뇌는 체중의 약 2%에 불과하지만 신체 에너지의 약 20%를 소비합니다.",
        "pt": "O cérebro consome ~20% da energia do corpo, apesar de representar apenas ~2% do peso corporal.",
        "fr": "Le cerveau consomme ~20 % de l'énergie corporelle, bien qu'il ne représente que ~2 % du poids corporel.",
        "vi": "Não tiêu thụ ~20% năng lượng cơ thể dù chỉ chiếm ~2% trọng lượng cơ thể.",
        "zh": "大脑仅占体重的约2%，却消耗约20%的身体能量。",
        "hi": "मस्तिष्क शरीर के वजन का केवल ~2% है, लेकिन शरीर की ~20% ऊर्जा उपभोग करता है।",
    },
    "It's astounding: If you lined up all ~25 trillion erythrocytes (red blood cells) in your body end-to-end, they would form a chain long enough to circle the entire Earth four times at the equator!": {
        "de": "Die ~25 Billionen Erythrozyten deines Körpers würden aneinandergereiht die Erde viermal am Äquator umspannen!",
        "es": "Los ~25 billones de eritrocitos de tu cuerpo, en fila, rodearían la Tierra cuatro veces por el ecuador.",
        "ko": "체내 약 25조 개의 적혈구를 일렬로 세우면 지구를 적도에서 4바퀴 돌 수 있습니다!",
        "pt": "Os ~25 trilhões de eritrócitos do seu corpo, enfileirados, dariam 4 voltas ao redor da Terra no equador!",
        "fr": "Les ~25 billions d'érythrocytes de votre corps, mis bout à bout, feraient quatre fois le tour de la Terre à l'équateur!",
        "vi": "Khoảng 25 nghìn tỷ hồng cầu trong cơ thể, nếu xếp thẳng hàng, sẽ quấn quanh Trái Đất 4 vòng ở đường xích đạo!",
        "zh": "体内约25万亿个红细胞首尾相连，可绕赤道4圈！",
        "hi": "शरीर में ~25 ट्रिलियन लाल रक्त कोशिकाओं को एक पंक्ति में रखा जाए तो वे भूमध्य रेखा पर पृथ्वी के 4 चक्कर लगा सकती हैं!",
    },
    "Technically, you perceive sound with your brain, not directly with your ears. Your ears simply act as sophisticated collectors, converting sound waves into signals the brain interprets.": {
        "de": "Du nimmst Schall mit dem Gehirn wahr, nicht den Ohren. Die Ohren wandeln Schallwellen nur in Signale um.",
        "es": "Percibes el sonido con el cerebro, no los oídos. Estos solo convierten ondas en señales que el cerebro interpreta.",
        "ko": "소리는 귀가 아니라 뇌로 인식합니다. 귀는 음파를 신호로 변환하는 역할만 합니다.",
        "pt": "Você percebe o som com o cérebro, não com os ouvidos. Os ouvidos apenas convertem ondas sonoras em sinais.",
        "fr": "Vous percevez le son avec le cerveau, pas directement avec les oreilles. Les oreilles convertissent les ondes sonores en signaux.",
        "vi": "Bạn nghe bằng não, không phải bằng tai. Tai chỉ chuyển đổi sóng âm thành tín hiệu cho não.",
        "zh": "您用大脑感知声音，而非直接用耳朵。耳朵只是将声波转换为大脑解读的信号。",
        "hi": "आप ध्वनि कानों से नहीं, मस्तिष्क से सुनते हैं। कान बस ध्वनि तरंगों को संकेतों में बदलते हैं।",
    },
    "Unique within the body, the cornea lacks its own blood supply. Instead, this transparent eye layer gets the oxygen it needs directly from the surrounding air.": {
        "de": "Die Hornhaut hat keine eigenen Blutgefäße und bezieht Sauerstoff direkt aus der Luft.",
        "es": "La córnea carece de vasos sanguíneos y obtiene oxígeno directamente del aire.",
        "ko": "각막은 혈관이 없는 신체 유일의 조직으로, 공기에서 직접 산소를 공급받습니다.",
        "pt": "A córnea é única no corpo por não ter suprimento de sangue próprio, obtendo oxigênio diretamente do ar.",
        "fr": "La cornée est unique dans le corps: elle n'a pas de vaisseaux sanguins et obtient son oxygène directement de l'air.",
        "vi": "Giác mạc là mô duy nhất trong cơ thể không có mạch máu, lấy oxy trực tiếp từ không khí.",
        "zh": "角膜是体内唯一没有血液供应的组织，直接从空气中获取氧气。",
        "hi": "कॉर्निया शरीर का एकमात्र ऊतक है जिसमें रक्त आपूर्ति नहीं होती, यह सीधे हवा से ऑक्सीजन लेता है।",
    },
    "Your skeleton isn't static! Bones are constantly undergoing a process of breakdown and rebuilding, leading to a complete skeletal renewal approximately every 10 years.": {
        "de": "Knochen werden ständig ab- und aufgebaut – dein gesamtes Skelett erneuert sich etwa alle 10 Jahre.",
        "es": "Los huesos se renuevan constantemente; el esqueleto completo se regenera cada ~10 años.",
        "ko": "뼈는 지속적으로 분해·재형성되며, 전체 골격이 약 10년마다 완전히 새로워집니다.",
        "pt": "Os ossos estão em constante renovação; todo o esqueleto se renova aproximadamente a cada 10 anos.",
        "fr": "Les os se renouvellent constamment; l'intégralité du squelette se régénère environ tous les 10 ans.",
        "vi": "Xương liên tục được phá vỡ và tái tạo, toàn bộ bộ xương được đổi mới khoảng mỗi 10 năm.",
        "zh": "骨骼不是静止的！骨骼持续分解和重建，整个骨架约每10年完全更新一次。",
        "hi": "हड्डियां लगातार टूटती और बनती रहती हैं – पूरा कंकाल लगभग हर 10 साल में नवीनीकृत होता है।",
    },
    "The power of the mind: The placebo effect can be so potent that treatments sometimes still work even when patients are fully aware they're receiving a placebo.": {
        "de": "Der Placebo-Effekt kann so stark sein, dass Behandlungen wirken, selbst wenn Patienten wissen, dass sie ein Placebo erhalten.",
        "es": "El efecto placebo puede ser tan potente que funciona incluso cuando el paciente sabe que toma un placebo.",
        "ko": "플라시보 효과는 환자가 위약임을 알고 있어도 치료가 효과를 나타낼 만큼 강력할 수 있습니다.",
        "pt": "O efeito placebo pode ser tão potente que os tratamentos às vezes funcionam mesmo quando os pacientes sabem que estão recebendo um placebo.",
        "fr": "L'effet placebo peut être si puissant que les traitements fonctionnent parfois même quand les patients savent qu'ils reçoivent un placebo.",
        "vi": "Hiệu ứng giả dược có thể mạnh đến mức điều trị vẫn hiệu quả dù bệnh nhân biết họ đang dùng giả dược.",
        "zh": "安慰剂效应如此强大，即使患者知道自己在接受安慰剂，治疗有时仍然有效。",
        "hi": "प्लेसबो प्रभाव इतना शक्तिशाली हो सकता है कि मरीज़ को पता होने पर भी उपचार काम करता है।",
    },
    "Contrary to popular belief, human blood is never actually blue. It only appears bluish through the skin because of how different wavelengths of light penetrate and reflect off tissues.": {
        "de": "Menschliches Blut ist nie blau. Es wirkt durch die Haut bläulich, weil Licht unterschiedlich tief ins Gewebe eindringt.",
        "es": "La sangre humana nunca es azul. Parece azulada a través de la piel por la forma en que la luz penetra el tejido.",
        "ko": "인간의 혈액은 파란색이 아닙니다. 피부를 통해 파랗게 보이는 것은 빛의 파장이 조직에 다르게 투과되기 때문입니다.",
        "pt": "Ao contrário da crença popular, o sangue humano nunca é azul. Parece azulado através da pele por causa de como a luz penetra nos tecidos.",
        "fr": "Contrairement aux idées reçues, le sang humain n'est jamais bleu. Il paraît bleuté à travers la peau en raison de la façon dont la lumière pénètre les tissus.",
        "vi": "Máu người không bao giờ thực sự có màu xanh. Vẻ xanh qua da là do cách các bước sóng ánh sáng khác nhau xuyên qua mô.",
        "zh": "与普遍认知相反，人类血液从不呈蓝色。通过皮肤看起来蓝色是因为不同波长的光穿透组织的方式不同。",
        "hi": "आम धारणा के विपरीत, मानव रक्त कभी नीला नहीं होता। त्वचा के माध्यम से नीला दिखना प्रकाश की तरंगदैर्ध्य के कारण होता है।",
    },
    "Those wrinkly fingers after a bath aren't just from water absorption! It's an active nervous system response, possibly evolved to improve grip on wet surfaces.": {
        "de": "Schrumpelige Finger im Bad sind keine Wasseraufnahme, sondern eine Nervenreaktion – wohl zur besseren Griffigkeit.",
        "es": "Los dedos arrugados en el baño no se deben al agua, sino al sistema nervioso: mejoran el agarre en superficies mojadas.",
        "ko": "목욕 후 주름진 손가락은 물 흡수 때문이 아닙니다! 젖은 표면에서 그립을 향상시키기 위해 진화한 신경계 반응입니다.",
        "pt": "Os dedos enrugados após o banho não são apenas absorção de água! É uma resposta do sistema nervoso, possivelmente evoluída para melhorar a aderência em superfícies molhadas.",
        "fr": "Les doigts ridés après un bain ne sont pas dus à l'absorption d'eau! C'est une réponse active du système nerveux, peut-être évoluée pour améliorer la prise sur les surfaces mouillées.",
        "vi": "Ngón tay nhăn sau khi tắm không chỉ do hút nước! Đó là phản ứng của hệ thần kinh, có thể tiến hóa để cải thiện độ bám trên bề mặt ướt.",
        "zh": "洗澡后手指起皱不只是因为吸水！这是神经系统的主动反应，可能是进化来改善湿滑表面的抓握力。",
        "hi": "नहाने के बाद झुर्रीदार उंगलियां सिर्फ पानी सोखने से नहीं होतीं! यह तंत्रिका तंत्र की सक्रिय प्रतिक्रिया है।",
    },
    "Your gut contains its own complex 'brain,' the enteric nervous system. This extensive network boasts over 100 million neurons, managing digestion largely independently.": {
        "de": "Dein Darm besitzt ein eigenes Nervensystem mit über 100 Mio. Neuronen, das die Verdauung weitgehend selbstständig steuert.",
        "es": "Tu intestino tiene su propio sistema nervioso con más de 100 millones de neuronas que dirige la digestión de forma autónoma.",
        "ko": "장은 1억 개 이상의 뉴런을 가진 장신경계로 소화를 독립적으로 조절합니다.",
        "pt": "O intestino contém seu próprio 'cérebro', o sistema nervoso entérico, com mais de 100 milhões de neurônios.",
        "fr": "L'intestin possède son propre 'cerveau', le système nerveux entérique, avec plus de 100 millions de neurones.",
        "vi": "Ruột có 'bộ não' riêng là hệ thần kinh ruột, với hơn 100 triệu tế bào thần kinh điều hành tiêu hóa.",
        "zh": "肠道拥有自己的'大脑'——肠神经系统，拥有超过1亿个神经元，基本独立管理消化。",
        "hi": "आंत में अपना जटिल 'मस्तिष्क' है - आंतरिक तंत्रिका तंत्र, जिसमें 10 करोड़ से अधिक न्यूरॉन्स हैं।",
    },
    "The sheer complexity of the human brain is staggering: It contains more connections (synapses) between neurons than there are estimated stars in the entire Milky Way galaxy.": {
        "de": "Das menschliche Gehirn hat mehr Synapsen zwischen Neuronen als die Milchstraße Sterne besitzt.",
        "es": "El cerebro humano contiene más sinapsis entre neuronas que estrellas hay en la Vía Láctea.",
        "ko": "인간 뇌의 시냅스 수는 은하수의 별 수보다 많습니다.",
        "pt": "O cérebro humano contém mais sinapses entre neurônios do que estrelas estimadas em toda a Via Láctea.",
        "fr": "Le cerveau humain contient plus de connexions (synapses) entre neurones qu'il n'y a d'étoiles estimées dans la Voie lactée.",
        "vi": "Não người có nhiều kết nối (synapse) giữa các tế bào thần kinh hơn số sao ước tính trong dải Ngân hà.",
        "zh": "人脑神经元之间的突触数量超过了银河系中估计的星星数量。",
        "hi": "मानव मस्तिष्क में न्यूरॉन्स के बीच जितने सिनैप्स हैं, उससे अधिक आकाशगंगा में तारे नहीं हैं।",
    },
    "During moments of intense fear, your body initiates the 'fight or flight' response, strategically redirecting blood flow away from non-essential areas and towards your major muscles.": {
        "de": "Bei starker Angst leitet der Körper im 'Kampf-oder-Flucht'-Modus Blut von unwichtigen Bereichen zu den Hauptmuskeln um.",
        "es": "Ante el miedo intenso, la respuesta de lucha o huida redirige la sangre de órganos no esenciales hacia los músculos principales.",
        "ko": "극도의 공포 시 '투쟁-도피' 반응으로 혈액이 비필수 부위에서 주요 근육으로 이동합니다.",
        "pt": "Em momentos de medo intenso, o corpo inicia a resposta de 'luta ou fuga', redirecionando o fluxo sanguíneo para os músculos principais.",
        "fr": "En cas de peur intense, le corps déclenche la réponse 'combat ou fuite', redirigeant le flux sanguin vers les muscles principaux.",
        "vi": "Khi sợ hãi tột độ, cơ thể kích hoạt phản ứng 'chiến đấu hay bỏ chạy', chuyển máu từ các cơ quan không thiết yếu đến cơ bắp chính.",
        "zh": "在极度恐惧时，身体会启动'战斗或逃跑'反应，将血流从非必要区域转向主要肌肉。",
        "hi": "तीव्र भय के क्षणों में शरीर 'लड़ो या भागो' प्रतिक्रिया शुरू करता है, रक्त प्रवाह मुख्य मांसपेशियों की ओर मोड़ता है।",
    },
    "A good laugh is like natural medicine! Laughter can actually increase your pain tolerance by triggering the release of endorphins, the body's natural feel-good chemicals, in the brain.": {
        "de": "Lachen erhöht die Schmerztoleranz, indem es die Ausschüttung von Endorphinen – den körpereigenen Glückshormonen – anregt.",
        "es": "Reír aumenta la tolerancia al dolor al desencadenar la liberación de endorfinas, los analgésicos naturales del cuerpo.",
        "ko": "웃음은 엔돌핀 분비를 유발해 통증 허용 한도를 높이는 자연 의학입니다!",
        "pt": "Uma boa risada é como remédio natural! O riso pode aumentar a tolerância à dor ao desencadear a liberação de endorfinas.",
        "fr": "Un bon rire est comme un médicament naturel! Le rire peut augmenter votre tolérance à la douleur en déclenchant la libération d'endorphines.",
        "vi": "Cười là thuốc tự nhiên! Tiếng cười kích thích giải phóng endorphin, giúp tăng khả năng chịu đựng đau.",
        "zh": "大笑如同天然良药！笑声能触发大脑释放内啡肽，提高痛觉耐受力。",
        "hi": "अच्छी हंसी प्राकृतिक दवा की तरह है! हंसी एंडोर्फिन मुक्त करके दर्द सहनशीलता बढ़ाती है।",
    },
    "Despite its widespread use in medicine for decades, the precise mechanisms of how general anesthesia works to induce unconsciousness remain surprisingly not fully understood by science.": {
        "de": "Obwohl seit Jahrzehnten eingesetzt, sind die genauen Wirkmechanismen der Vollnarkose wissenschaftlich noch nicht vollständig verstanden.",
        "es": "Pese a su uso médico durante décadas, los mecanismos exactos de la anestesia general aún no se comprenden del todo.",
        "ko": "수십 년간 사용되었음에도 전신마취가 의식 상실을 유도하는 정확한 메커니즘은 아직 완전히 밝혀지지 않았습니다.",
        "pt": "Apesar do uso médico por décadas, os mecanismos precisos de como a anestesia geral induz inconsciência ainda não são completamente compreendidos.",
        "fr": "Malgré des décennies d'utilisation médicale, les mécanismes précis par lesquels l'anesthésie générale induit l'inconscience ne sont toujours pas entièrement compris.",
        "vi": "Dù được dùng trong y học hàng chục năm, cơ chế chính xác của gây mê toàn thân vẫn chưa được khoa học hiểu đầy đủ.",
        "zh": "尽管在医学中使用了数十年，全身麻醉诱导失去意识的确切机制至今仍未完全被科学理解。",
        "hi": "दशकों से चिकित्सा में उपयोग के बावजूद, सामान्य संज्ञाहरण अचेतनता कैसे उत्पन्न करता है, यह पूरी तरह समझा नहीं गया।",
    },
    "Those tiny bumps on your skin? Goosebumps are a fascinating evolutionary leftover, a reflex inherited from our hairier ancestors used to raise fur for insulation or intimidation.": {
        "de": "Gänsehaut ist ein evolutionäres Überbleibsel: Bei behaarten Vorfahren richtete dieser Reflex das Fell zur Isolation oder Einschüchterung auf.",
        "es": "La piel de gallina es un vestigio evolutivo: en ancestros más peludos, erizaba el pelo para aislarse o intimidar.",
        "ko": "소름은 털이 많은 조상에게서 물려받은 진화적 유산으로, 보온이나 위협용으로 털을 세우는 반사입니다.",
        "pt": "A pele de galinha é um resquício evolutivo fascinante, um reflexo herdado de antepassados mais peludos para erguer a pelagem.",
        "fr": "La chair de poule est un vestige évolutif fascinant, un réflexe hérité de nos ancêtres plus velus pour dresser la fourrure.",
        "vi": "Da gà là di tích tiến hóa thú vị, phản xạ thừa kế từ tổ tiên có nhiều lông để dựng lông giữ ấm hoặc dọa nạt.",
        "zh": "起鸡皮疙瘩是迷人的进化遗留，是从毛发更多的祖先遗传下来的反射，用于竖起毛发保暖或恐吓。",
        "hi": "रोंगटे खड़े होना एक विकासवादी अवशेष है, जो हमारे बालदार पूर्वजों से विरासत में मिला है।",
    },
    "You're vastly outnumbered inside! Your gut microbiome hosts more individual bacterial cells than there are human cells comprising your entire body, playing vital roles in overall health.": {
        "de": "Dein Darmmikrobiom enthält mehr Bakterienzellen als der Körper menschliche Zellen hat – und ist entscheidend für die Gesundheit.",
        "es": "Tu microbioma intestinal contiene más células bacterianas que células humanas tiene tu cuerpo, con un papel vital para la salud.",
        "ko": "장내 미생물군에는 인체 전체의 인간 세포보다 많은 박테리아가 살고 있습니다!",
        "pt": "Seu microbioma intestinal abriga mais células bacterianas do que células humanas em todo o seu corpo!",
        "fr": "Votre microbiome intestinal abrite plus de cellules bactériennes qu'il n'y a de cellules humaines dans votre corps!",
        "vi": "Hệ vi sinh vật ruột của bạn chứa nhiều tế bào vi khuẩn hơn tổng số tế bào người trong toàn cơ thể!",
        "zh": "您的肠道微生物组中的细菌细胞数量超过了整个身体的人类细胞数量！",
        "hi": "आपके आंत के माइक्रोबायोम में पूरे शरीर की मानव कोशिकाओं से अधिक जीवाणु कोशिकाएं हैं!",
    },
    "A rare condition known as Superior Canal Dehiscence Syndrome allows some individuals to actually hear internal body sounds, such as their own eyeballs moving within their sockets.": {
        "de": "Das seltene Syndrom der superioren Bogengangsdehiszenz lässt Betroffene innere Körpergeräusche hören – z. B. die eigenen Augäpfel.",
        "es": "El síndrome de dehiscencia del canal superior permite oír sonidos internos, como el movimiento de los propios globos oculares.",
        "ko": "상반고리관 결손 증후군이라는 희귀 질환이 있는 사람들은 안구 움직임 소리 같은 내부 신체 소리를 들을 수 있습니다.",
        "pt": "A Síndrome de Dehiscência do Canal Superior permite que algumas pessoas ouçam sons corporais internos, como os próprios olhos se movendo.",
        "fr": "Le Syndrome de Déhiscence du Canal Supérieur permet à certaines personnes d'entendre des sons corporels internes, comme leurs yeux bougeant.",
        "vi": "Hội chứng Vỡ Ống Bán khuyên Trên cho phép một số người nghe thấy âm thanh bên trong cơ thể, như tiếng nhãn cầu di chuyển.",
        "zh": "上半规管裂隙综合征这种罕见疾病使一些人能听到内部身体声音，如自己眼球移动的声音。",
        "hi": "सुपीरियर कैनाल डीहिसेंस सिंड्रोम नामक दुर्लभ स्थिति में लोग अंदरूनी शरीर की आवाजें सुन सकते हैं।",
    },
    "Why do we yawn? One leading theory suggests yawning might function as a natural thermostat, helping to cool down an overheating brain by increasing blood flow and air intake.": {
        "de": "Warum gähnen wir? Eine Theorie besagt, Gähnen kühlt ein überhitztes Gehirn, indem es die Durchblutung und Luftaufnahme steigert.",
        "es": "¿Por qué bostezamos? Una teoría sugiere que el bostezo enfría el cerebro recalentado al aumentar el flujo sanguíneo y la entrada de aire.",
        "ko": "왜 하품을 할까요? 한 이론에 따르면 하품은 혈류와 공기 흡입을 늘려 과열된 뇌를 식히는 자연 체온 조절기입니다.",
        "pt": "Por que bocejamos? Uma teoria sugere que o bocejo funciona como um termostato natural, resfriando o cérebro superaquecido.",
        "fr": "Pourquoi bâillons-nous? Une théorie principale suggère que le bâillement fonctionne comme un thermostat naturel pour refroidir un cerveau en surchauffe.",
        "vi": "Tại sao chúng ta ngáp? Một lý thuyết cho rằng ngáp hoạt động như bộ điều nhiệt tự nhiên, làm mát não quá nóng.",
        "zh": "为什么我们打哈欠？一种主要理论认为，打哈欠可能充当天然恒温器，通过增加血流和进气量来冷却过热的大脑。",
        "hi": "हम जम्हाई क्यों लेते हैं? एक प्रमुख सिद्धांत बताता है कि जम्हाई मस्तिष्क को ठंडा करने के लिए प्राकृतिक थर्मोस्टेट है।",
    },
    "There's a physiological basis for connection: Studies show that when people hold hands or gaze into each other's eyes for a period, their heartbeats can actually synchronize.": {
        "de": "Studien zeigen: Wenn Menschen sich in die Augen schauen oder die Hände halten, können sich ihre Herzschläge synchronisieren.",
        "es": "Estudios muestran que cuando las personas se toman de la mano o se miran a los ojos, sus corazones pueden sincronizarse.",
        "ko": "연구에 따르면 사람들이 손을 잡거나 서로 눈을 바라볼 때 심박수가 실제로 동기화될 수 있습니다.",
        "pt": "Estudos mostram que quando as pessoas seguram as mãos ou se olham nos olhos, seus batimentos cardíacos podem realmente sincronizar.",
        "fr": "Des études montrent que lorsque les gens se tiennent la main ou se regardent dans les yeux, leurs battements de cœur peuvent se synchroniser.",
        "vi": "Nghiên cứu cho thấy khi người ta nắm tay hoặc nhìn vào mắt nhau, nhịp tim của họ có thể đồng bộ hóa.",
        "zh": "研究表明，当人们牵手或凝视彼此眼睛时，他们的心跳实际上可以同步。",
        "hi": "अध्ययन दिखाते हैं कि जब लोग हाथ पकड़ते हैं या एक-दूसरे की आंखों में देखते हैं, तो उनकी दिल की धड़कनें समन्वयित हो सकती हैं।",
    },
    "Over an average lifetime, you'll shed approximately 40 pounds (around 18kg) of dead skin cells. Much of the common household dust is actually composed of this sloughed-off skin.": {
        "de": "Im Leben verlierst du rund 18 kg abgestorbene Hautzellen. Ein Großteil des Hausstaubs besteht aus dieser abgelösten Haut.",
        "es": "A lo largo de tu vida perderás ~18 kg de células muertas. Gran parte del polvo doméstico está formado por esta piel.",
        "ko": "평균 수명 동안 약 18kg의 죽은 피부세포를 흘립니다. 가정의 먼지 상당 부분이 이 피부로 구성됩니다.",
        "pt": "Durante uma vida média, você perderá aproximadamente 18 kg de células mortas de pele. Grande parte da poeira doméstica é composta por essa pele.",
        "fr": "Au cours d'une vie moyenne, vous perdrez environ 18 kg de cellules mortes de peau. Une grande partie de la poussière domestique est composée de cette peau.",
        "vi": "Trong suốt đời người, bạn sẽ bong ~18kg tế bào da chết. Phần lớn bụi nhà thực ra là da bong ra.",
        "zh": "在平均一生中，您将脱落约18公斤的死皮细胞。普通家庭灰尘很大程度上由这些脱落的皮肤组成。",
        "hi": "जीवनकाल में लगभग 18 किलो मृत त्वचा कोशिकाएं झड़ती हैं। घर की धूल का बड़ा हिस्सा इसी से बना होता है।",
    },
    "The brain's internal body map is powerful: Phantom limb sensations or even pain can occur in individuals born without that specific limb, demonstrating the map's innate nature.": {
        "de": "Das Gehirn hat eine innere Körperkarte: Phantomschmerzen können sogar bei Menschen auftreten, die ein Glied nie besessen haben.",
        "es": "El mapa corporal interno del cerebro es innato: el dolor de miembro fantasma puede darse incluso en quienes nacieron sin él.",
        "ko": "뇌의 내부 신체 지도는 강력합니다: 특정 사지 없이 태어난 사람에게도 환상통이 발생할 수 있습니다.",
        "pt": "O mapa corporal interno do cérebro é poderoso: sensações de membro fantasma podem ocorrer em pessoas nascidas sem esse membro.",
        "fr": "La carte corporelle interne du cerveau est puissante: des sensations de membre fantôme peuvent survenir chez des personnes nées sans ce membre.",
        "vi": "Bản đồ cơ thể bên trong não rất mạnh: cảm giác chi ma thậm chí xuất hiện ở người sinh ra đã không có chi đó.",
        "zh": "大脑的内部身体地图非常强大：幻肢感甚至疼痛可能出现在天生缺少该肢体的人身上。",
        "hi": "मस्तिष्क का आंतरिक शरीर मानचित्र शक्तिशाली है: जन्म से अंग के बिना लोगों को भी फैंटम दर्द हो सकता है।",
    },
    "The liver possesses an incredible regenerative capacity. It's capable of regrowing back to its full, original size even if only 25% of the healthy tissue remains after damage or surgery.": {
        "de": "Die Leber kann sich selbst regenerieren: Sie wächst auf ihre volle Größe zurück, selbst wenn nur 25 % des Gewebes verbleiben.",
        "es": "El hígado puede regenerarse hasta su tamaño original aunque solo quede el 25 % del tejido sano.",
        "ko": "간은 건강한 조직의 25%만 남아있어도 원래 크기로 재생될 수 있는 놀라운 재생 능력을 가지고 있습니다.",
        "pt": "O fígado possui incrível capacidade regenerativa, sendo capaz de crescer de volta ao seu tamanho original mesmo com apenas 25% do tecido saudável.",
        "fr": "Le foie possède une incroyable capacité régénératrice. Il est capable de repousser jusqu'à sa taille originale même si seulement 25% du tissu sain reste.",
        "vi": "Gan có khả năng tái tạo đáng kinh ngạc: có thể phục hồi kích thước ban đầu dù chỉ còn 25% mô lành.",
        "zh": "肝脏具有令人难以置信的再生能力：即使只剩下25%的健康组织，也能重新长回原来的完整大小。",
        "hi": "लिवर में अविश्वसनीय पुनर्जनन क्षमता है: केवल 25% स्वस्थ ऊतक बचे होने पर भी यह पूरे आकार में वापस आ सकता है।",
    },
    "Believe it or not, humans actually emit a faint glow through natural bioluminescence! However, this light is approximately 1,000 times weaker than what the unaided human eye is capable of detecting.": {
        "de": "Menschen strahlen tatsächlich ein schwaches Biolumineszenzlicht aus – es ist jedoch ~1 000-mal schwächer, als das Auge wahrnehmen kann.",
        "es": "Los humanos emiten bioluminiscencia, pero es ~1 000 veces más débil de lo que el ojo puede detectar.",
        "ko": "인간은 자연 생물발광을 통해 약하게 빛을 냅니다! 하지만 이 빛은 육안으로 감지할 수 있는 것보다 약 1,000배 약합니다.",
        "pt": "Acredite ou não, humanos emitem um brilho fraco por bioluminescência natural! Porém, é ~1.000 vezes mais fraco que o olho nu pode detectar.",
        "fr": "Croyez-le ou non, les humains émettent une faible lueur par bioluminescence naturelle! Cependant, cette lumière est ~1 000 fois plus faible que ce que l'œil peut détecter.",
        "vi": "Tin hay không, con người thực sự phát sáng yếu qua bioluminescence tự nhiên! Tuy nhiên, ánh sáng này yếu hơn ~1.000 lần so với mắt thường có thể nhận ra.",
        "zh": "信不信由你，人类通过天然生物发光实际上会发出微弱的光！但这种光比肉眼能检测到的约弱1,000倍。",
        "hi": "मानो या न मानो, मनुष्य प्राकृतिक जैव-प्रकाश के माध्यम से वास्तव में एक धीमी चमक उत्सर्जित करते हैं! लेकिन यह आंखों से ~1,000 गुना कमजोर है।",
    },
    "You experience a slight height change daily! You're typically taller just after waking up because the cartilage discs in your spine gradually compress under gravity throughout the day.": {
        "de": "Du bist morgens etwas größer: Tagsüber komprimiert die Schwerkraft die Knorpelscheiben der Wirbelsäule.",
        "es": "Eres algo más alto al levantarte: durante el día la gravedad comprime los discos cartilaginosos de la columna.",
        "ko": "매일 약간의 키 변화를 경험합니다! 척추의 연골 디스크가 중력으로 압축되기 전인 기상 직후에 더 큽니다.",
        "pt": "Você experimenta uma pequena mudança de altura diária! Você é mais alto logo ao acordar porque os discos de cartilagem comprimem ao longo do dia.",
        "fr": "Vous subissez un léger changement de taille quotidien! Vous êtes généralement plus grand juste après le réveil car les disques cartilagineux se compriment sous la gravité.",
        "vi": "Bạn thay đổi chiều cao nhỏ mỗi ngày! Bạn cao hơn ngay khi thức dậy vì đĩa sụn cột sống dần bị nén bởi trọng lực.",
        "zh": "您每天都会经历轻微的身高变化！刚起床时通常更高，因为脊柱软骨盘在重力下整天逐渐压缩。",
        "hi": "आप प्रतिदिन थोड़ी ऊंचाई में बदलाव अनुभव करते हैं! जागने के तुरंत बाद आप लंबे होते हैं क्योंकि कार्टिलेज डिस्क गुरुत्वाकर्षण से दबती हैं।",
    },
    "Fibrodysplasia Ossificans Progressiva, sometimes called 'Stone Man Syndrome,' is an extremely rare genetic condition where injured muscle and connective tissue gradually ossify, turning into solid bone over time.": {
        "de": "Die Fibrodysplasia ossificans progressiva («Steinmann-Syndrom») ist eine seltene Krankheit, bei der verletztes Muskel- und Bindegewebe zu Knochen verknöchert.",
        "es": "La fibrodisplasia osificante progresiva («síndrome del hombre de piedra») es una enfermedad rara donde músculo y tejido conectivo se osifican.",
        "ko": "'석인 증후군'이라고도 불리는 진행성 골화 섬유이형성증은 손상된 근육과 결합 조직이 서서히 뼈로 변하는 극히 희귀한 유전 질환입니다.",
        "pt": "A Fibrodisplasia Ossificante Progressiva, às vezes chamada de 'Síndrome do Homem de Pedra', é uma condição genética extremamente rara onde músculo e tecido conjuntivo gradualmente ossificam.",
        "fr": "La Fibrodysplasie Ossifiante Progressive, parfois appelée 'Syndrome de l'Homme de Pierre', est une condition génétique extrêmement rare où les muscles et tissus conjonctifs s'ossifient progressivement.",
        "vi": "Fibrodysplasia Ossificans Progressiva, đôi khi gọi là 'Hội chứng Người Đá', là bệnh di truyền cực hiếm khiến cơ và mô liên kết bị ossify dần thành xương cứng.",
        "zh": "进行性骨化性纤维发育不全，有时称为'石人综合征'，是一种极为罕见的遗传病，受损的肌肉和结缔组织逐渐骨化。",
        "hi": "'पत्थर मानव सिंड्रोम' के नाम से जानी जाने वाली फाइब्रोडिसप्लेसिया ओसिफिकेंस प्रोग्रेसिवा एक अत्यंत दुर्लभ आनुवांशिक स्थिति है।",
    },

    # ================================================================= #
    # Daily Law Facts  (daily_widgets.py – LAW_FACTS[i]["text"])
    # ================================================================= #
    "The word 'lawyer' comes from the Middle English 'lawe,' meaning 'that which is laid down,' highlighting how laws were seen as fixed foundations of society.": {
        "de": "'Lawyer' kommt vom mittelenglischen 'lawe' (das Festgelegte) – Gesetze galten als feste Grundlage der Gesellschaft.",
        "es": "«Lawyer» viene del inglés medio «lawe» («lo establecido»), reflejo de que las leyes se veían como cimientos fijos de la sociedad.",
        "ko": "'lawyer'는 중세 영어 'lawe'('정해진 것')에서 유래했으며, 법이 사회의 고정된 토대로 여겨졌음을 보여줍니다.",
        "pt": "A palavra 'lawyer' vem do inglês médio 'lawe', que significa 'o que foi estabelecido', destacando como as leis eram vistas como fundamentos fixos da sociedade.",
        "fr": "Le mot 'lawyer' vient du moyen anglais 'lawe', signifiant 'ce qui est établi', soulignant comment les lois étaient vues comme des fondements fixes de la société.",
        "vi": "Từ 'lawyer' xuất phát từ tiếng Anh Trung cổ 'lawe' nghĩa là 'điều được đặt ra', cho thấy luật pháp từng được xem là nền tảng cố định của xã hội.",
        "zh": "'lawyer'一词来自中古英语'lawe'，意为'被规定之物'，突显了法律被视为社会固定基础的观念。",
        "hi": "'lawyer' शब्द मध्य अंग्रेजी 'lawe' से आता है, जिसका अर्थ है 'जो निर्धारित किया गया है', यह दर्शाता है कि कानूनों को समाज की स्थिर नींव माना जाता था।",
    },
    "The first-year law curriculum is notoriously intense; it's designed less to teach content and more to train the mind to 'think like a lawyer.'": {
        "de": "Das erste Jurastudiumsjahr ist bekannt intensiv – es soll weniger Inhalte lehren als vielmehr juristisches Denken trainieren.",
        "es": "El primer año de Derecho es intenso por diseño: entrena a pensar como abogado más que a memorizar contenido.",
        "ko": "법학 1년 차 커리큘럼은 내용 교육보다 '변호사처럼 생각하는' 방법을 훈련하도록 설계된 것으로 악명 높습니다.",
        "pt": "O currículo do primeiro ano de direito é notoriamente intenso; é projetado menos para ensinar conteúdo e mais para treinar a mente a 'pensar como um advogado'.",
        "fr": "Le programme de première année de droit est notoirement intense; il est conçu moins pour enseigner du contenu que pour entraîner l'esprit à 'penser comme un avocat'.",
        "vi": "Chương trình năm nhất luật nổi tiếng là khốc liệt; được thiết kế ít để dạy nội dung hơn là rèn luyện tư duy 'suy nghĩ như một luật sư'.",
        "zh": "法律第一年课程以强度著称；它的设计不是为了教授内容，而是为了训练'像律师一样思考'。",
        "hi": "कानून की पहली साल की पाठ्यक्रम कुख्यात रूप से कठिन है; यह सामग्री सिखाने से कम और 'वकील की तरह सोचना' प्रशिक्षित करने के लिए डिज़ाइन की गई है।",
    },
    "Some students experience 'law school syndrome' — jokingly believing they have every legal condition they study, similar to medical student syndrome.": {
        "de": "Manche Jurastudierenden glauben scherzhaft, jedes Rechtsproblem zu haben, das sie gerade studieren – ähnlich dem Medizinstudentensyndrom.",
        "es": "Algunos estudiantes de Derecho creen humorísticamente padecer cada problema jurídico que estudian, como el síndrome del estudiante de medicina.",
        "ko": "일부 학생들은 의대생 증후군과 유사하게 자신이 공부하는 모든 법적 상황에 처해있다고 농담처럼 믿는 '법학대학원 증후군'을 경험합니다.",
        "pt": "Alguns estudantes experimentam a 'síndrome da faculdade de direito' — acreditando jocosamente ter cada condição legal que estudam.",
        "fr": "Certains étudiants vivent le 'syndrome de l'école de droit' — croyant en plaisantant avoir chaque condition légale qu'ils étudient.",
        "vi": "Một số sinh viên gặp 'hội chứng trường luật' — vui đùa tin rằng mình mắc mọi tình trạng pháp lý họ học.",
        "zh": "一些学生经历'法学院综合症'——开玩笑地认为自己遇到了所学的每一种法律情况，类似于医学生综合症。",
        "hi": "कुछ छात्र 'लॉ स्कूल सिंड्रोम' अनुभव करते हैं — मजाकिया तौर पर यह विश्वास करते हुए कि उनके पास अध्ययन की गई हर कानूनी स्थिति है।",
    },
    "Legal language, often mocked for being confusing, is intentionally precise, as small word choices can completely change a statute's interpretation.": {
        "de": "Juristischer Sprachgebrauch wirkt verwirrend, ist aber bewusst präzise: Kleine Wortunterschiede können die Auslegung eines Gesetzes komplett verändern.",
        "es": "El lenguaje jurídico, burlado por confuso, es deliberadamente preciso: pequeñas diferencias léxicas cambian totalmente la interpretación de una ley.",
        "ko": "법률 언어는 종종 혼란스럽다고 비판받지만, 작은 단어 선택이 법령 해석을 완전히 바꿀 수 있어 의도적으로 정밀합니다.",
        "pt": "A linguagem jurídica, frequentemente ridicularizada por ser confusa, é intencionalmente precisa, pois pequenas escolhas de palavras podem mudar completamente a interpretação de uma lei.",
        "fr": "Le langage juridique, souvent moqué pour sa complexité, est intentionnellement précis, car de petits choix de mots peuvent complètement changer l'interprétation d'une loi.",
        "vi": "Ngôn ngữ pháp lý, thường bị chế giễu vì gây bối rối, thực ra được cố ý chính xác, vì lựa chọn từ nhỏ có thể thay đổi hoàn toàn cách giải thích luật.",
        "zh": "法律语言常因令人困惑而被嘲笑，实际上是刻意精确的，因为小小的措辞选择可以完全改变法律的解释。",
        "hi": "कानूनी भाषा, अक्सर भ्रामक होने के लिए उपहास की जाती है, जानबूझकर सटीक है क्योंकि छोटे शब्द चुनाव किसी क़ानून की व्याख्या पूरी तरह बदल सकते हैं।",
    },
    "The scales of justice, a symbol recognized globally, date back to ancient Egypt, representing the weighing of truth and fairness before the gods.": {
        "de": "Die Waage der Gerechtigkeit stammt aus dem alten Ägypten und symbolisiert das Abwägen von Wahrheit und Fairness vor den Göttern.",
        "es": "La balanza de la justicia se remonta al antiguo Egipto, donde simbolizaba el peso de la verdad ante los dioses.",
        "ko": "전 세계적으로 인정받는 정의의 저울은 고대 이집트에서 유래하여 신들 앞에서 진실과 공정함을 재는 것을 상징합니다.",
        "pt": "As balanças da justiça, símbolo reconhecido globalmente, remontam ao Egito antigo, representando a pesagem da verdade e equidade perante os deuses.",
        "fr": "Les balances de la justice, symbole reconnu mondialement, remontent à l'Égypte antique, représentant la pesée de la vérité et de l'équité devant les dieux.",
        "vi": "Cán cân công lý, biểu tượng được công nhận toàn cầu, có từ Ai Cập cổ đại, tượng trưng cho việc cân đo sự thật và công bằng trước các vị thần.",
        "zh": "正义的天平，全球公认的象征，可追溯到古埃及，代表在诸神面前权衡真理与公平。",
        "hi": "न्याय की तराजू, वैश्विक रूप से मान्यता प्राप्त प्रतीक, प्राचीन मिस्र से आती है, देवताओं के समक्ष सत्य और निष्पक्षता को तौलने का प्रतीक।",
    },
    "The adversarial system, where two sides argue before a neutral judge, is based on the belief that truth emerges from conflict, not harmony.": {
        "de": "Das adversarische System, in dem zwei Seiten vor einem neutralen Richter streiten, beruht auf der Idee, dass Wahrheit aus Konflikt entsteht.",
        "es": "El sistema adversarial, donde dos partes litigan ante un juez neutral, se basa en que la verdad emerge del conflicto.",
        "ko": "중립적인 판사 앞에서 두 측이 논쟁하는 대심제는 진실이 조화가 아닌 갈등에서 나온다는 믿음에 기반합니다.",
        "pt": "O sistema adversarial, onde dois lados argumentam perante um juiz neutro, baseia-se na crença de que a verdade emerge do conflito, não da harmonia.",
        "fr": "Le système contradictoire, où deux parties argumentent devant un juge neutre, est basé sur la croyance que la vérité émerge du conflit, pas de l'harmonie.",
        "vi": "Hệ thống tranh tụng, nơi hai bên tranh luận trước thẩm phán trung lập, dựa trên niềm tin rằng sự thật xuất hiện từ xung đột, không phải hài hòa.",
        "zh": "对抗制，两方在中立法官前争辩，基于真相从冲突而非和谐中产生的信念。",
        "hi": "प्रतिकूल प्रणाली, जहां दो पक्ष एक तटस्थ न्यायाधीश के सामने बहस करते हैं, इस विश्वास पर आधारित है कि सत्य संघर्ष से उभरता है।",
    },
    "In legal philosophy, a core debate exists between natural law (law based on morality) and legal positivism (law based on human-made rules).": {
        "de": "In der Rechtsphilosophie streiten Naturrecht (Recht aus Moral) und Rechtspositivismus (Recht aus menschengesetzten Regeln) miteinander.",
        "es": "En filosofía jurídica debate el derecho natural (basado en la moral) frente al positivismo jurídico (basado en normas humanas).",
        "ko": "법철학에서 자연법(도덕에 기반한 법)과 법실증주의(인간이 만든 규칙에 기반한 법) 사이의 핵심 논쟁이 있습니다.",
        "pt": "Na filosofia jurídica, existe um debate central entre o direito natural (lei baseada na moralidade) e o positivismo jurídico (lei baseada em regras humanas).",
        "fr": "En philosophie juridique, un débat central existe entre le droit naturel (loi basée sur la morale) et le positivisme juridique (loi basée sur des règles humaines).",
        "vi": "Trong triết học pháp lý, tồn tại cuộc tranh luận cốt lõi giữa luật tự nhiên (luật dựa trên đạo đức) và chủ nghĩa thực chứng pháp lý (luật dựa trên quy tắc do con người tạo ra).",
        "zh": "在法律哲学中，自然法（基于道德的法律）和法律实证主义（基于人为规则的法律）之间存在核心争论。",
        "hi": "कानूनी दर्शन में, प्राकृतिक कानून (नैतिकता पर आधारित) और कानूनी प्रत्यक्षवाद (मानव निर्मित नियमों पर आधारित) के बीच मुख्य बहस है।",
    },
    "The phrase 'ignorance of the law is no excuse' exists in most legal systems, even though no one can possibly know all the laws that apply to them.": {
        "de": "'Unwissenheit schützt vor Strafe nicht' gilt in den meisten Rechtssystemen, obwohl niemand alle für ihn geltenden Gesetze kennen kann.",
        "es": "«La ignorancia de la ley no exime de su cumplimiento» rige en casi todos los sistemas, aunque nadie pueda conocerlos todos.",
        "ko": "'법을 몰랐다고 변명이 되지 않는다'는 원칙은 대부분의 법체계에 존재하지만, 아무도 자신에게 적용되는 모든 법을 알 수 없습니다.",
        "pt": "A frase 'ignorância da lei não é desculpa' existe na maioria dos sistemas jurídicos, embora ninguém possa conhecer todas as leis que se aplicam a eles.",
        "fr": "La phrase 'l'ignorance de la loi n'est pas une excuse' existe dans la plupart des systèmes juridiques, même si personne ne peut connaître toutes les lois qui leur sont applicables.",
        "vi": "Câu 'không biết luật không phải lý do chính đáng' tồn tại trong hầu hết hệ thống pháp lý, dù không ai có thể biết tất cả luật áp dụng với họ.",
        "zh": "'不知法不是借口'这一原则存在于大多数法律体系中，尽管没有人能了解适用于自己的所有法律。",
        "hi": "'कानून से अनजानी कोई बहाना नहीं' का सिद्धांत अधिकांश कानूनी प्रणालियों में मौजूद है, हालांकि कोई भी सभी लागू कानूनों को नहीं जान सकता।",
    },
    "Many of the world's influential legal systems, from civil law to common law, ultimately trace their roots back to Roman law.": {
        "de": "Viele einflussreiche Rechtssysteme der Welt – vom Civil Law bis zum Common Law – gehen letztlich auf das römische Recht zurück.",
        "es": "Muchos sistemas jurídicos influyentes, del derecho civil al common law, tienen sus raíces en el derecho romano.",
        "ko": "민법에서 보통법에 이르기까지 세계의 많은 영향력 있는 법체계는 궁극적으로 로마법에 뿌리를 두고 있습니다.",
        "pt": "Muitos dos sistemas jurídicos influentes do mundo, do direito civil ao common law, traçam suas raízes ao direito romano.",
        "fr": "Beaucoup des systèmes juridiques influents du monde, du droit civil à la common law, trouvent finalement leurs racines dans le droit romain.",
        "vi": "Nhiều hệ thống pháp lý có ảnh hưởng trên thế giới, từ luật dân sự đến common law, đều có nguồn gốc từ luật La Mã.",
        "zh": "世界上许多有影响力的法律体系，从民法到普通法，最终都可追溯到罗马法。",
        "hi": "दुनिया की कई प्रभावशाली कानूनी प्रणालियां, सिविल लॉ से कॉमन लॉ तक, अंततः रोमन कानून से उत्पन्न होती हैं।",
    },
    "The Latin phrases still used in modern law—like habeas corpus or mens rea—survive from medieval times, when Latin was the universal language of educated discourse.": {
        "de": "Lateinische Begriffe wie 'habeas corpus' oder 'mens rea' stammen aus dem Mittelalter, als Latein die Sprache der Gelehrten war.",
        "es": "Términos latinos como «habeas corpus» o «mens rea» perviven del Medievo, cuando el latín era la lengua universal del saber.",
        "ko": "현대 법에서 여전히 사용되는 라틴어 표현들, 예를 들어 habeas corpus나 mens rea는 라틴어가 교육의 보편적 언어였던 중세 시대부터 살아남았습니다.",
        "pt": "As frases latinas ainda usadas no direito moderno — como habeas corpus ou mens rea — sobrevivem da Idade Média, quando o latim era a linguagem universal do discurso culto.",
        "fr": "Les phrases latines encore utilisées dans le droit moderne — comme habeas corpus ou mens rea — survivent des temps médiévaux, quand le latin était la langue universelle du discours savant.",
        "vi": "Các cụm từ Latin vẫn dùng trong luật hiện đại — như habeas corpus hay mens rea — sống sót từ thời Trung Cổ khi Latin là ngôn ngữ phổ quát của học thuật.",
        "zh": "现代法律中仍使用的拉丁短语——如人身保护令或犯罪意图——从中世纪存活至今，当时拉丁语是受教育话语的通用语言。",
        "hi": "आधुनिक कानून में अभी भी उपयोग किए जाने वाले लैटिन वाक्यांश — जैसे habeas corpus या mens rea — मध्ययुगीन काल से बचे हैं।",
    },
    "The first recorded 'law school' dates back to ancient Rome around 450 BCE, when the Twelve Tables were taught as the foundation of Roman law.": {
        "de": "Die erste bekannte 'Rechtsschule' gab es im alten Rom um 450 v. Chr., wo die Zwölf Tafeln als Grundlage des römischen Rechts gelehrt wurden.",
        "es": "La primera «escuela de derecho» documentada data del 450 a. C. en Roma, donde las Doce Tablas eran el fundamento del derecho.",
        "ko": "최초의 기록된 '법학교'는 기원전 450년경 고대 로마로 거슬러 올라가며, 열두 표가 로마법의 기초로 가르쳐졌습니다.",
        "pt": "A primeira 'escola de direito' registrada data da Roma antiga por volta de 450 AEC, quando as Doze Tábuas eram ensinadas como fundamento do direito romano.",
        "fr": "La première 'école de droit' enregistrée remonte à la Rome antique vers 450 avant J.-C., quand les Douze Tables étaient enseignées comme fondement du droit romain.",
        "vi": "Trường luật đầu tiên được ghi lại có từ La Mã cổ đại khoảng năm 450 TCN, khi Mười Hai Bảng được dạy như nền tảng của luật La Mã.",
        "zh": "第一所有记录的'法学院'可追溯到公元前450年的古罗马，当时十二铜表法作为罗马法的基础被教授。",
        "hi": "पहला दर्ज 'लॉ स्कूल' लगभग 450 ईसा पूर्व प्राचीन रोम में था, जहां बारह तालिकाओं को रोमन कानून की नींव के रूप में पढ़ाया जाता था।",
    },
    "Most legal disputes never reach a courtroom; the vast majority are settled privately through negotiation or mediation.": {
        "de": "Die meisten Rechtsstreitigkeiten gelangen nie vor Gericht – die große Mehrheit wird durch Verhandlung oder Mediation privat beigelegt.",
        "es": "La mayoría de los conflictos jurídicos no llegan a juicio; se resuelven en privado por negociación o mediación.",
        "ko": "대부분의 법적 분쟁은 법정에 가지 않으며, 압도적 다수가 협상이나 중재를 통해 사적으로 해결됩니다.",
        "pt": "A maioria das disputas jurídicas nunca chega a um tribunal; a grande maioria é resolvida privadamente através de negociação ou mediação.",
        "fr": "La plupart des litiges juridiques n'arrivent jamais devant un tribunal; la grande majorité est réglée en privé par négociation ou médiation.",
        "vi": "Phần lớn tranh chấp pháp lý không bao giờ đến tòa; đại đa số được giải quyết riêng tư qua thương lượng hoặc hòa giải.",
        "zh": "大多数法律纠纷从不上法庭；绝大多数通过谈判或调解私下解决。",
        "hi": "अधिकांश कानूनी विवाद अदालत तक नहीं पहुंचते; अधिकांश को बातचीत या मध्यस्थता के माध्यम से निजी तौर पर सुलझाया जाता है।",
    },
    "There's a famous saying in legal circles: 'Hard cases make bad law,' meaning emotionally charged cases often lead to poor general rules.": {
        "de": "In Juristenkreisen gilt: 'Hard cases make bad law' – emotionsgeladene Fälle führen oft zu schlechten allgemeinen Regeln.",
        "es": "Hay un dicho jurídico: «Hard cases make bad law»: los casos emocionalmente difíciles suelen generar malas normas generales.",
        "ko": "법조계의 유명한 격언: '어려운 사건은 나쁜 법을 만든다'는 감정적으로 격한 사건이 종종 나쁜 일반 규칙으로 이어진다는 의미입니다.",
        "pt": "Há um famoso ditado nos círculos jurídicos: 'Casos difíceis fazem leis ruins', significando que casos emocionalmente carregados frequentemente levam a regras gerais ruins.",
        "fr": "Il y a un célèbre dicton dans les milieux juridiques: 'Les cas difficiles font de mauvaises lois', signifiant que les cas émotionnellement chargés mènent souvent à de mauvaises règles générales.",
        "vi": "Có câu nói nổi tiếng trong giới luật: 'Vụ án khó tạo ra luật tệ', nghĩa là các vụ án đầy cảm xúc thường dẫn đến quy tắc chung kém.",
        "zh": "法律界有句名言：'难案产生坏法'，意味着情绪化的案例往往导致糟糕的一般规则。",
        "hi": "कानूनी क्षेत्र में एक प्रसिद्ध कहावत: 'कठिन मामले बुरे कानून बनाते हैं', अर्थात भावनात्मक रूप से आवेशित मामले अक्सर खराब नियमों की ओर ले जाते हैं।",
    },
    "In France, it is illegal to name a pig 'Napoleon' out of respect for the famous emperor.": {
        "de": "In Frankreich ist es aus Respekt vor dem Kaiser verboten, ein Schwein 'Napoleon' zu nennen.",
        "es": "En Francia está prohibido llamar «Napoleón» a un cerdo, por respeto al famoso emperador.",
        "ko": "프랑스에서는 유명한 황제에 대한 경의로 돼지에게 '나폴레옹'이라는 이름을 붙이는 것이 불법입니다.",
        "pt": "Na França, é ilegal nomear um porco de 'Napoleão' por respeito ao famoso imperador.",
        "fr": "En France, il est illégal de nommer un cochon 'Napoléon' par respect pour le célèbre empereur.",
        "vi": "Ở Pháp, việc đặt tên cho lợn là 'Napoleon' là bất hợp pháp vì tôn trọng hoàng đế nổi tiếng.",
        "zh": "在法国，出于对著名皇帝的尊重，将猪命名为'拿破仑'是违法的。",
        "hi": "फ्रांस में, प्रसिद्ध सम्राट के सम्मान में सुअर का नाम 'नेपोलियन' रखना अवैध है।",
    },
    "In Samoa, it's illegal to forget your wife's birthday—a law meant to protect marital harmony.": {
        "de": "In Samoa ist es illegal, den Geburtstag seiner Frau zu vergessen – ein Gesetz zum Schutz der ehelichen Harmonie.",
        "es": "En Samoa es ilegal olvidar el cumpleaños de tu esposa, ley pensada para proteger la armonía conyugal.",
        "ko": "사모아에서는 아내의 생일을 잊는 것이 불법입니다 — 부부 화합을 보호하기 위한 법입니다.",
        "pt": "Em Samoa, é ilegal esquecer o aniversário da sua esposa — uma lei destinada a proteger a harmonia conjugal.",
        "fr": "À Samoa, il est illégal d'oublier l'anniversaire de votre femme — une loi destinée à protéger l'harmonie conjugale.",
        "vi": "Ở Samoa, việc quên ngày sinh nhật của vợ là bất hợp pháp — một luật nhằm bảo vệ hòa khí hôn nhân.",
        "zh": "在萨摩亚，忘记妻子生日是违法的——这是一条旨在保护婚姻和谐的法律。",
        "hi": "समोआ में, पत्नी का जन्मदिन भूलना अवैध है — वैवाहिक सद्भाव की रक्षा के लिए बनाया गया कानून।",
    },
    "The United States has more lawyers than any other country—roughly 1.3 million—which means about one lawyer for every 240 people.": {
        "de": "Die USA haben mehr Anwälte als jedes andere Land – rund 1,3 Millionen, also etwa einen pro 240 Einwohner.",
        "es": "EE. UU. tiene más abogados que cualquier otro país: ~1,3 millones, uno por cada 240 habitantes.",
        "ko": "미국은 다른 어떤 나라보다 많은 변호사를 보유하고 있습니다 — 약 130만 명 — 즉 240명당 한 명의 변호사입니다.",
        "pt": "Os Estados Unidos têm mais advogados do que qualquer outro país — aproximadamente 1,3 milhão — o que significa cerca de um advogado para cada 240 pessoas.",
        "fr": "Les États-Unis ont plus d'avocats que tout autre pays — environ 1,3 million — ce qui signifie environ un avocat pour 240 personnes.",
        "vi": "Hoa Kỳ có nhiều luật sư hơn bất kỳ quốc gia nào khác — khoảng 1,3 triệu — tức là khoảng một luật sư cho mỗi 240 người.",
        "zh": "美国拥有比其他任何国家更多的律师——约130万——这意味着大约每240人就有一名律师。",
        "hi": "संयुक्त राज्य अमेरिका में किसी भी अन्य देश की तुलना में अधिक वकील हैं — लगभग 1.3 मिलियन — यानी प्रत्येक 240 लोगों पर एक वकील।",
    },
    "In ancient Greece, lawyers didn't exist; citizens had to represent themselves in court, though they could hire speechwriters to craft their arguments.": {
        "de": "Im alten Griechenland gab es keine Anwälte – Bürger mussten sich selbst vertreten, konnten aber Redenschreiber engagieren.",
        "es": "En la antigua Grecia no había abogados; los ciudadanos se representaban solos, aunque podían contratar redactores de discursos.",
        "ko": "고대 그리스에는 변호사가 없었습니다; 시민들은 법정에서 스스로를 변호해야 했지만 연설 작가를 고용할 수 있었습니다.",
        "pt": "Na Grécia antiga, advogados não existiam; os cidadãos tinham que se representar no tribunal, embora pudessem contratar redatores de discursos.",
        "fr": "Dans la Grèce antique, les avocats n'existaient pas; les citoyens devaient se représenter eux-mêmes au tribunal, bien qu'ils puissent engager des rédacteurs de discours.",
        "vi": "Ở Hy Lạp cổ đại, không có luật sư; công dân phải tự đại diện cho mình tại tòa, dù có thể thuê người viết bài phát biểu.",
        "zh": "在古希腊，律师不存在；公民必须在法庭上为自己辩护，尽管他们可以雇用演讲撰写人。",
        "hi": "प्राचीन ग्रीस में वकील नहीं थे; नागरिकों को अदालत में स्वयं का प्रतिनिधित्व करना पड़ता था, हालांकि वे भाषण लेखक नियुक्त कर सकते थे।",
    },
    "International law technically lacks a global 'police force'; compliance depends largely on mutual agreement and political pressure.": {
        "de": "Das Völkerrecht hat keine globale 'Polizei' – die Einhaltung beruht auf gegenseitigen Vereinbarungen und politischem Druck.",
        "es": "El derecho internacional carece de una «policía» global; su cumplimiento depende de acuerdos mutuos y presión política.",
        "ko": "국제법은 기술적으로 전 세계적인 '경찰력'이 없으며, 준수는 주로 상호 합의와 정치적 압력에 달려 있습니다.",
        "pt": "O direito internacional tecnicamente carece de uma 'força policial' global; o cumprimento depende em grande parte de acordo mútuo e pressão política.",
        "fr": "Le droit international manque techniquement d'une 'force de police' mondiale; la conformité dépend largement des accords mutuels et de la pression politique.",
        "vi": "Luật quốc tế về mặt kỹ thuật thiếu 'lực lượng cảnh sát' toàn cầu; việc tuân thủ phụ thuộc phần lớn vào thỏa thuận chung và áp lực chính trị.",
        "zh": "国际法在技术上缺乏全球'警察力量'；合规性主要取决于相互协议和政治压力。",
        "hi": "अंतरराष्ट्रीय कानून में तकनीकी रूप से वैश्विक 'पुलिस बल' का अभाव है; अनुपालन मुख्यतः आपसी समझौते और राजनीतिक दबाव पर निर्भर है।",
    },
    "Lawyers are sometimes called 'professional pessimists,' as their job is to imagine every possible way something could go wrong to protect their clients.": {
        "de": "Anwälte gelten als 'professionelle Pessimisten': Ihr Job ist es, jeden möglichen Fehlerfall zu antizipieren, um Mandanten zu schützen.",
        "es": "Los abogados se llaman «pesimistas profesionales»: su trabajo es imaginar todo lo que puede salir mal para proteger a sus clientes.",
        "ko": "변호사들은 때때로 '전문 비관주의자'라고 불립니다 — 고객을 보호하기 위해 잘못될 수 있는 모든 경우를 상상하는 것이 그들의 일이기 때문입니다.",
        "pt": "Os advogados são às vezes chamados de 'pessimistas profissionais', pois seu trabalho é imaginar todas as maneiras possíveis pelas quais algo pode dar errado.",
        "fr": "Les avocats sont parfois appelés 'pessimistes professionnels', car leur travail consiste à imaginer toutes les façons possibles dont quelque chose pourrait mal tourner.",
        "vi": "Luật sư đôi khi được gọi là 'bi quan chuyên nghiệp', vì công việc của họ là tưởng tượng mọi cách có thể xảy ra sai sót để bảo vệ khách hàng.",
        "zh": "律师有时被称为'职业悲观主义者'，因为他们的工作是想象所有可能出错的方式来保护客户。",
        "hi": "वकीलों को कभी-कभी 'पेशेवर निराशावादी' कहा जाता है, क्योंकि उनका काम है हर संभावित गलती की कल्पना करके अपने मुवक्किलों की रक्षा करना।",
    },
    "The correct answer to almost any complex legal question is: 'It depends.'": {
        "de": "Die richtige Antwort auf fast jede komplexe Rechtsfrage lautet: 'Es kommt darauf an.'",
        "es": "La respuesta correcta a casi cualquier pregunta jurídica compleja es: «Depende».",
        "ko": "거의 모든 복잡한 법적 질문에 대한 정답은 '경우에 따라 다릅니다'입니다.",
        "pt": "A resposta correta para quase qualquer questão jurídica complexa é: 'Depende.'",
        "fr": "La bonne réponse à presque toute question juridique complexe est: 'Ça dépend.'",
        "vi": "Câu trả lời đúng cho hầu hết câu hỏi pháp lý phức tạp là: 'Tùy trường hợp.'",
        "zh": "几乎任何复杂法律问题的正确答案是：'视情况而定。'",
        "hi": "लगभग किसी भी जटिल कानूनी प्रश्न का सही उत्तर है: 'यह निर्भर करता है।'",
    },
    "Many famous revolutions, from the American to the French, began not with weapons but with legal arguments about rights and legitimacy.": {
        "de": "Viele berühmte Revolutionen – von der amerikanischen bis zur französischen – begannen nicht mit Waffen, sondern mit Rechtsargumenten.",
        "es": "Muchas revoluciones famosas, desde la americana hasta la francesa, comenzaron con argumentos jurídicos sobre derechos y legitimidad.",
        "ko": "미국 혁명부터 프랑스 혁명까지, 많은 유명한 혁명들은 무기가 아닌 권리와 정당성에 관한 법적 논쟁으로 시작되었습니다.",
        "pt": "Muitas revoluções famosas, da americana à francesa, começaram não com armas, mas com argumentos legais sobre direitos e legitimidade.",
        "fr": "Beaucoup de révolutions célèbres, de l'américaine à la française, ont commencé non pas avec des armes mais avec des arguments juridiques sur les droits et la légitimité.",
        "vi": "Nhiều cuộc cách mạng nổi tiếng, từ Mỹ đến Pháp, bắt đầu không phải bằng vũ khí mà bằng các lập luận pháp lý về quyền lợi và tính hợp pháp.",
        "zh": "许多著名的革命，从美国到法国，开始不是用武器，而是用关于权利和合法性的法律论点。",
        "hi": "कई प्रसिद्ध क्रांतियां, अमेरिकी से फ्रांसीसी तक, हथियारों से नहीं बल्कि अधिकारों और वैधता के बारे में कानूनी तर्कों से शुरू हुईं।",
    },
    "The phrase 'law and order' is misleading—in reality, law often creates conflict before it restores order, since every rule can be challenged or reinterpreted.": {
        "de": "'Recht und Ordnung' ist irreführend: Recht schafft oft Konflikte, bevor es Ordnung herstellt, da jede Regel angefochten werden kann.",
        "es": "«Ley y orden» es engañoso: el derecho suele crear conflictos antes de restaurar el orden, pues toda norma puede impugnarse.",
        "ko": "'법과 질서'라는 표현은 오해를 불러일으킵니다 — 실제로 법은 모든 규칙이 도전받거나 재해석될 수 있기 때문에 종종 질서 회복 전에 갈등을 만듭니다.",
        "pt": "A frase 'lei e ordem' é enganosa — na realidade, a lei frequentemente cria conflito antes de restaurar a ordem, pois toda regra pode ser desafiada ou reinterpretada.",
        "fr": "L'expression 'loi et ordre' est trompeuse — en réalité, la loi crée souvent des conflits avant de restaurer l'ordre, car chaque règle peut être contestée ou réinterprétée.",
        "vi": "Cụm từ 'pháp luật và trật tự' gây hiểu nhầm — thực tế, luật pháp thường tạo ra xung đột trước khi khôi phục trật tự vì mọi quy tắc đều có thể bị thách thức.",
        "zh": "'法律与秩序'这个说法具有误导性——实际上，法律往往在恢复秩序之前制造冲突，因为每条规则都可以被质疑或重新解释。",
        "hi": "'कानून और व्यवस्था' वाक्यांश भ्रामक है — वास्तव में, कानून अक्सर व्यवस्था बहाल करने से पहले संघर्ष पैदा करता है।",
    },
    "Law students often spend more time reading cases than attending lectures—a single case can run dozens of pages, filled with historical reasoning.": {
        "de": "Jurastudierende verbringen mehr Zeit mit Fallstudien als mit Vorlesungen – ein einziger Fall kann dutzende Seiten umfassen.",
        "es": "Los estudiantes de Derecho leen casos más que asisten a clases; un solo caso puede tener decenas de páginas de razonamiento histórico.",
        "ko": "법학생들은 종종 강의 참석보다 사례 읽기에 더 많은 시간을 씁니다 — 하나의 사례가 역사적 추론으로 가득한 수십 페이지에 달할 수 있습니다.",
        "pt": "Os estudantes de direito frequentemente gastam mais tempo lendo casos do que assistindo aulas — um único caso pode ter dezenas de páginas repletas de raciocínio histórico.",
        "fr": "Les étudiants en droit passent souvent plus de temps à lire des affaires qu'à suivre des cours — une seule affaire peut s'étendre sur des dizaines de pages, remplie de raisonnements historiques.",
        "vi": "Sinh viên luật thường dành nhiều thời gian đọc án lệ hơn dự giảng — một vụ án có thể dài hàng chục trang đầy lý luận lịch sử.",
        "zh": "法学生通常花更多时间阅读案例而非上课——单个案例可能长达数十页，充满历史推理。",
        "hi": "कानून के छात्र अक्सर व्याख्यानों में उपस्थित होने की तुलना में मामले पढ़ने में अधिक समय बिताते हैं — एक मामला ऐतिहासिक तर्क से भरे दर्जनों पृष्ठों का हो सकता है।",
    },
    "In South Korea, law students may study for up to 20 hours a day before bar exams, preparing for years before even sitting the test.": {
        "de": "In Südkorea lernen Jurastudierende vor dem Staatsexamen bis zu 20 Stunden täglich und bereiten sich jahrelang vor.",
        "es": "En Corea del Sur, los estudiantes de Derecho estudian hasta 20 h diarias antes del examen de colegiación, preparándose durante años.",
        "ko": "한국에서 법학생들은 변호사 시험 전 하루 최대 20시간을 공부하며, 시험을 보기 전 수년간 준비합니다.",
        "pt": "Na Coreia do Sul, estudantes de direito podem estudar até 20 horas por dia antes dos exames da ordem, preparando-se por anos antes de fazer o teste.",
        "fr": "En Corée du Sud, les étudiants en droit peuvent étudier jusqu'à 20 heures par jour avant les examens du barreau, se préparant pendant des années.",
        "vi": "Ở Hàn Quốc, sinh viên luật có thể học tới 20 giờ mỗi ngày trước kỳ thi luật sư, chuẩn bị trong nhiều năm trước khi thi.",
        "zh": "在韩国，法学生在律师考试前可能每天学习多达20小时，在参加考试前准备数年。",
        "hi": "दक्षिण कोरिया में, कानून के छात्र बार परीक्षाओं से पहले प्रतिदिन 20 घंटे तक पढ़ सकते हैं, परीक्षा देने से पहले वर्षों तक तैयारी करते हुए।",
    },
    "The shortest U.S. Supreme Court decision ever written contained only one word: 'Affirmed.' It meant the lower court's decision stood.": {
        "de": "Die kürzeste Entscheidung des US-Supreme-Court enthielt nur ein Wort: 'Affirmed' – die Vorinstanz hatte recht.",
        "es": "La decisión más corta del Tribunal Supremo de EE. UU. contenía solo una palabra: «Afirmado». La sentencia inferior era correcta.",
        "ko": "미국 대법원 역사상 가장 짧은 판결은 단 하나의 단어만 담았습니다: '확인'. 하급법원의 판결이 유지된다는 의미였습니다.",
        "pt": "A mais curta decisão do Supremo Tribunal dos EUA já escrita continha apenas uma palavra: 'Afirmado.' Significava que a decisão do tribunal inferior era mantida.",
        "fr": "La plus courte décision de la Cour suprême des États-Unis jamais écrite ne contenait qu'un seul mot: 'Confirmé.' Cela signifiait que la décision du tribunal inférieur était maintenue.",
        "vi": "Bản án ngắn nhất của Tòa án Tối cao Mỹ chỉ gồm một từ: 'Khẳng định.' Nghĩa là quyết định của tòa cấp dưới được giữ nguyên.",
        "zh": "美国最高法院历史上最短的判决只包含一个词：'确认。' 这意味着下级法院的判决成立。",
        "hi": "अमेरिकी सर्वोच्च न्यायालय का अब तक का सबसे छोटा निर्णय केवल एक शब्द का था: 'पुष्टि।' इसका अर्थ था कि निचली अदालत का निर्णय बरकरार है।",
    },
    "In China, law students must study Marxist legal theory as part of their curriculum, as it is a foundation for the country's legal philosophy.": {
        "de": "In China müssen Jurastudierende marxistische Rechtstheorie studieren, da sie Grundlage der staatlichen Rechtsphilosophie ist.",
        "es": "En China, los estudiantes de Derecho deben estudiar teoría jurídica marxista, base de la filosofía legal del país.",
        "ko": "중국에서 법학생들은 국가 법철학의 기초로서 마르크스 법학 이론을 교육과정의 일부로 공부해야 합니다.",
        "pt": "Na China, os estudantes de direito devem estudar a teoria jurídica marxista como parte do currículo, pois é uma base da filosofia jurídica do país.",
        "fr": "En Chine, les étudiants en droit doivent étudier la théorie juridique marxiste dans le cadre de leur programme, car c'est un fondement de la philosophie juridique du pays.",
        "vi": "Ở Trung Quốc, sinh viên luật phải học lý thuyết pháp lý Marxist như một phần của chương trình học, vì đây là nền tảng triết học pháp lý của đất nước.",
        "zh": "在中国，法学生必须将马克思主义法学理论作为课程的一部分来学习，因为它是国家法律哲学的基础。",
        "hi": "चीन में, कानून के छात्रों को पाठ्यक्रम के हिस्से के रूप में मार्क्सवादी कानूनी सिद्धांत का अध्ययन करना होता है।",
    },

    # ================================================================= #
    # Daily General Facts  (daily_widgets.py – GENERAL_FACTS[i]["text"])
    # ================================================================= #
    "If you could remove all the empty space inside atoms, the entire human race would fit into a sugar cube.": {
        "de": "Würde man den Leerraum in Atomen entfernen, würde die gesamte Menschheit in einen Würfelzucker passen.",
        "es": "Si se eliminara el espacio vacío de los átomos, toda la humanidad cabría en un terrón de azúcar.",
        "ko": "원자 내부의 모든 빈 공간을 제거할 수 있다면, 인류 전체가 각설탕 하나에 들어갑니다.",
        "pt": "Se você pudesse remover todo o espaço vazio dentro dos átomos, toda a raça humana caberia em um cubo de açúcar.",
        "fr": "Si vous pouviez supprimer tout l'espace vide à l'intérieur des atomes, toute la race humaine tiendrait dans un cube de sucre.",
        "vi": "Nếu bạn có thể loại bỏ tất cả không gian trống bên trong nguyên tử, toàn bộ nhân loại sẽ vừa vào một viên đường.",
        "zh": "如果你能移除原子内部的所有空间，整个人类将能装进一块方糖。",
        "hi": "यदि आप परमाणुओं के अंदर की सारी खाली जगह हटा सकें, तो पूरी मानव जाति एक चीनी के क्यूब में समा जाएगी।",
    },
    "Sloths can hold their breath longer than dolphins — up to 40 minutes — by slowing their heart rate.": {
        "de": "Faultiere können länger als Delfine die Luft anhalten – bis zu 40 Minuten – indem sie ihren Herzschlag verlangsamen.",
        "es": "Los perezosos aguantan la respiración hasta 40 minutos, más que los delfines, ralentizando su ritmo cardíaco.",
        "ko": "나무늘보는 심박수를 낮춰 돌고래보다 오래 — 최대 40분까지 — 숨을 참을 수 있습니다.",
        "pt": "As preguiças podem prender a respiração por mais tempo que os golfinhos — até 40 minutos — desacelerando sua frequência cardíaca.",
        "fr": "Les paresseux peuvent retenir leur souffle plus longtemps que les dauphins — jusqu'à 40 minutes — en ralentissant leur rythme cardiaque.",
        "vi": "Lười biếng có thể nín thở lâu hơn cá heo — tới 40 phút — bằng cách làm chậm nhịp tim.",
        "zh": "树懒可以比海豚更长时间地憋气——最长40分钟——通过降低心率。",
        "hi": "आलस अपनी हृदय गति धीमी करके डॉल्फिन से भी लंबे समय तक — 40 मिनट तक — सांस रोक सकते हैं।",
    },
    "The average cloud weighs around one million pounds, but floats because the air below it is even heavier.": {
        "de": "Eine durchschnittliche Wolke wiegt rund 500 Tonnen, schwebt aber, weil die Luft darunter noch schwerer ist.",
        "es": "Una nube media pesa ~500 toneladas, pero flota porque el aire debajo es aún más denso.",
        "ko": "평균적인 구름은 약 500톤에 달하지만, 아래 공기가 더 무겁기 때문에 떠 있습니다.",
        "pt": "A nuvem média pesa cerca de 500 toneladas, mas flutua porque o ar abaixo dela é ainda mais pesado.",
        "fr": "Un nuage moyen pèse environ 500 tonnes, mais flotte parce que l'air en dessous est encore plus lourd.",
        "vi": "Một đám mây trung bình nặng khoảng 500 tấn, nhưng nổi vì không khí bên dưới còn nặng hơn.",
        "zh": "平均云重约500吨，但漂浮是因为其下方的空气更重。",
        "hi": "औसत बादल का वजन लगभग 500 टन होता है, लेकिन यह तैरता है क्योंकि इसके नीचे की हवा और भी भारी होती है।",
    },
    "There are more trees on Earth than stars in the Milky Way — roughly three trillion versus 100–400 billion.": {
        "de": "Auf der Erde gibt es mehr Bäume als Sterne in der Milchstraße – rund 3 Billionen gegenüber 100–400 Milliarden.",
        "es": "En la Tierra hay más árboles que estrellas en la Vía Láctea: ~3 billones frente a 100–400 mil millones.",
        "ko": "지구의 나무 수는 은하수의 별 수보다 많습니다 — 약 3조 대 1,000~4,000억입니다.",
        "pt": "Há mais árvores na Terra do que estrelas na Via Láctea — aproximadamente três trilhões versus 100–400 bilhões.",
        "fr": "Il y a plus d'arbres sur Terre que d'étoiles dans la Voie lactée — environ trois billions contre 100–400 milliards.",
        "vi": "Số cây trên Trái Đất nhiều hơn số sao trong dải Ngân hà — khoảng 3 nghìn tỷ so với 100–400 tỷ.",
        "zh": "地球上的树木数量超过银河系中的星星数量——大约3万亿棵对比1000–4000亿颗。",
        "hi": "पृथ्वी पर आकाशगंगा के तारों से अधिक पेड़ हैं — लगभग 3 ट्रिलियन बनाम 100–400 बिलियन।",
    },
    "A single strand of spider silk, if scaled up to the thickness of a pencil, could stop a passenger plane in flight.": {
        "de": "Eine einzelne Spinnenseide, auf Bleistiftdicke vergrößert, könnte ein Passagierflugzeug im Flug stoppen.",
        "es": "Un hilo de seda de araña, escalado al grosor de un lápiz, podría detener un avión comercial en vuelo.",
        "ko": "거미줄 한 가닥을 연필 두께로 확대하면 비행 중인 여객기를 멈출 수 있습니다.",
        "pt": "Um único fio de seda de aranha, se escalado para a espessura de um lápis, poderia parar um avião de passageiros em voo.",
        "fr": "Un seul brin de soie d'araignée, si agrandi à l'épaisseur d'un crayon, pourrait arrêter un avion de passagers en vol.",
        "vi": "Một sợi tơ nhện, nếu phóng đại đến độ dày của cây bút chì, có thể dừng máy bay chở khách đang bay.",
        "zh": "一根蜘蛛丝，如果放大到铅笔的粗细，可以停止一架飞行中的客机。",
        "hi": "एक मकड़ी के जाले का एक धागा, यदि पेंसिल की मोटाई तक बड़ा किया जाए, उड़ान में एक यात्री विमान को रोक सकता है।",
    },
    "In Antarctica, there's a waterfall that runs red as blood — it's actually caused by oxidized iron in saltwater.": {
        "de": "In der Antarktis gibt es einen blutrot fließenden Wasserfall – verursacht durch oxidiertes Eisen im Salzwasser.",
        "es": "En la Antártida hay una cascada roja como sangre, causada por hierro oxidado en agua salada.",
        "ko": "남극에는 혈액처럼 붉게 흐르는 폭포가 있습니다 — 실제로 소금물의 산화철 때문입니다.",
        "pt": "Na Antártica, há uma cachoeira que flui vermelha como sangue — é causada pelo ferro oxidado na água salgada.",
        "fr": "En Antarctique, il y a une cascade qui coule rouge comme du sang — causée par du fer oxydé dans de l'eau salée.",
        "vi": "Ở Nam Cực, có một thác nước chảy đỏ như máu — thực ra do sắt bị oxy hóa trong nước muối.",
        "zh": "在南极洲，有一个像血一样红色流淌的瀑布——实际上是由盐水中氧化铁造成的。",
        "hi": "अंटार्कटिका में एक झरना है जो खून की तरह लाल बहता है — यह वास्तव में खारे पानी में ऑक्सीकृत लोहे के कारण होता है।",
    },
    "Time passes slightly faster at your head than at your feet — thanks to Einstein's theory of relativity and gravity's effect on time.": {
        "de": "An deinem Kopf vergeht die Zeit etwas schneller als an deinen Füßen – Einsteins Relativitätstheorie macht's möglich.",
        "es": "El tiempo transcurre ligeramente más rápido en tu cabeza que en tus pies, según la relatividad de Einstein.",
        "ko": "아인슈타인의 상대성 이론과 중력의 시간 효과 덕분에 머리 쪽의 시간이 발 쪽보다 약간 더 빠르게 흐릅니다.",
        "pt": "O tempo passa ligeiramente mais rápido na sua cabeça do que nos seus pés — graças à teoria da relatividade de Einstein e ao efeito da gravidade sobre o tempo.",
        "fr": "Le temps passe légèrement plus vite à votre tête qu'à vos pieds — grâce à la théorie de la relativité d'Einstein et à l'effet de la gravité sur le temps.",
        "vi": "Thời gian trôi nhanh hơn một chút ở đầu bạn so với ở chân — nhờ thuyết tương đối của Einstein và ảnh hưởng của trọng lực lên thời gian.",
        "zh": "由于爱因斯坦的相对论和重力对时间的影响，您头部的时间流逝比脚部稍快。",
        "hi": "आइंस्टीन के सापेक्षता सिद्धांत और समय पर गुरुत्वाकर्षण के प्रभाव के कारण आपके सिर पर समय पैरों की तुलना में थोड़ा तेज गुजरता है।",
    },
    "Bananas are berries, but strawberries aren't — botanically speaking.": {
        "de": "Botanisch gesehen sind Bananen Beeren, Erdbeeren aber nicht.",
        "es": "Botánicamente, los plátanos son bayas, pero las fresas no.",
        "ko": "식물학적으로 바나나는 장과(베리)지만 딸기는 그렇지 않습니다.",
        "pt": "Bananas são frutas do tipo baga, mas morangos não são — botanicamente falando.",
        "fr": "Les bananes sont des baies, mais les fraises ne le sont pas — botaniquement parlant.",
        "vi": "Về mặt thực vật học, chuối là quả mọng nhưng dâu tây thì không.",
        "zh": "从植物学角度来看，香蕉是浆果，但草莓不是。",
        "hi": "वनस्पति विज्ञान की दृष्टि से केले जामुन हैं, लेकिन स्ट्रॉबेरी नहीं हैं।",
    },
    "Wombat poop is cube-shaped, so it doesn't roll away and can be used to mark territory.": {
        "de": "Wombat-Kot ist würfelförmig, damit er nicht wegrollt und zur Reviermarkierung genutzt werden kann.",
        "es": "Las heces de wombat son cúbicas para que no rueden y sirvan para marcar territorio.",
        "ko": "웜뱃의 배설물은 정육면체 모양이라 굴러가지 않고 영역을 표시하는 데 사용됩니다.",
        "pt": "O cocô do wombat tem formato de cubo, para que não role e possa ser usado para marcar território.",
        "fr": "Les crottes de wombat sont en forme de cube, pour qu'elles ne roulent pas et puissent être utilisées pour marquer le territoire.",
        "vi": "Phân wombat có hình khối vuông, để không lăn đi và có thể dùng để đánh dấu lãnh thổ.",
        "zh": "袋熊的粪便呈立方体形状，这样它不会滚走，可以用来标记领地。",
        "hi": "वोम्बैट का मल घन आकार का होता है, इसलिए यह लुढ़कता नहीं और क्षेत्र चिह्नित करने में उपयोग किया जा सकता है।",
    },
    "Octopuses have three hearts and blue blood; two hearts pump to the gills, one to the rest of the body.": {
        "de": "Tintenfische haben drei Herzen und blaues Blut: Zwei pumpen zu den Kiemen, eines zum restlichen Körper.",
        "es": "Los pulpos tienen tres corazones y sangre azul: dos bombean hacia las branquias y uno hacia el resto del cuerpo.",
        "ko": "문어는 세 개의 심장과 파란 피를 가지고 있습니다; 두 개는 아가미에, 하나는 나머지 몸에 혈액을 펌프합니다.",
        "pt": "Os polvos têm três corações e sangue azul; dois corações bombeiam para as brânquias, um para o resto do corpo.",
        "fr": "Les pieuvres ont trois cœurs et du sang bleu; deux cœurs pompent vers les branchies, un vers le reste du corps.",
        "vi": "Bạch tuộc có ba tim và máu xanh; hai tim bơm cho mang, một tim bơm cho phần còn lại của cơ thể.",
        "zh": "章鱼有三个心脏和蓝色血液；两个心脏向鳃泵血，一个向身体其余部分泵血。",
        "hi": "ऑक्टोपस के तीन दिल और नीला खून होता है; दो दिल गलफड़ों को, एक बाकी शरीर को पंप करता है।",
    },
    "Cleopatra lived closer in time to the invention of the iPhone than to the construction of the Great Pyramid.": {
        "de": "Kleopatra lebte zeitlich näher an der Erfindung des iPhones als an der Erbauung der Großen Pyramide.",
        "es": "Cleopatra vivió más cerca de la invención del iPhone que de la construcción de la Gran Pirámide.",
        "ko": "클레오파트라는 시간적으로 대피라미드 건설보다 아이폰 발명에 더 가깝게 살았습니다.",
        "pt": "Cleópatra viveu temporalmente mais próxima da invenção do iPhone do que da construção da Grande Pirâmide.",
        "fr": "Cléopâtre a vécu plus proche dans le temps de l'invention de l'iPhone que de la construction de la Grande Pyramide.",
        "vi": "Nữ hoàng Cleopatra sống gần thời điểm phát minh iPhone hơn là thời điểm xây Đại Kim Tự Tháp.",
        "zh": "克利奥帕特拉在时间上更接近iPhone的发明，而非大金字塔的建造。",
        "hi": "क्लियोपेट्रा समय की दृष्टि से महान पिरामिड के निर्माण की बजाय iPhone के आविष्कार के करीब जीती थीं।",
    },
    "There are more possible ways to shuffle a deck of cards than there are atoms on Earth.": {
        "de": "Es gibt mehr Möglichkeiten, ein Kartenspiel zu mischen, als Atome auf der Erde existieren.",
        "es": "Hay más formas posibles de barajar una baraja que átomos en la Tierra.",
        "ko": "카드 한 벌을 섞는 방법의 수는 지구의 원자 수보다 많습니다.",
        "pt": "Há mais maneiras possíveis de embaralhar um baralho de cartas do que há átomos na Terra.",
        "fr": "Il y a plus de façons possibles de mélanger un jeu de cartes qu'il n'y a d'atomes sur Terre.",
        "vi": "Số cách có thể xáo bộ bài nhiều hơn số nguyên tử trên Trái Đất.",
        "zh": "洗牌的可能方式比地球上的原子数量还多。",
        "hi": "ताश के पत्तों को फेरने के संभावित तरीके पृथ्वी के परमाणुओं से भी अधिक हैं।",
    },
    "Sharks existed before trees did — by about 50 million years.": {
        "de": "Haie existierten schon vor Bäumen – rund 50 Millionen Jahre früher.",
        "es": "Los tiburones existieron antes que los árboles, con unos 50 millones de años de antelación.",
        "ko": "상어는 나무보다 약 5천만 년 먼저 존재했습니다.",
        "pt": "Os tubarões existiram antes das árvores — cerca de 50 milhões de anos antes.",
        "fr": "Les requins ont existé avant les arbres — d'environ 50 millions d'années.",
        "vi": "Cá mập tồn tại trước cây cối khoảng 50 triệu năm.",
        "zh": "鲨鱼比树木早出现约5000万年。",
        "hi": "शार्क पेड़ों से पहले अस्तित्व में थी — लगभग 5 करोड़ साल पहले।",
    },
    "In theory, if you could fold a piece of paper 42 times, it would reach the Moon.": {
        "de": "Theoretisch würde ein 42-mal gefaltetes Blatt Papier bis zum Mond reichen.",
        "es": "En teoría, un papel doblado 42 veces alcanzaría la Luna.",
        "ko": "이론적으로 종이를 42번 접을 수 있다면 달까지 닿을 것입니다.",
        "pt": "Em teoria, se você pudesse dobrar um pedaço de papel 42 vezes, ele alcançaria a Lua.",
        "fr": "En théorie, si vous pouviez plier une feuille de papier 42 fois, elle atteindrait la Lune.",
        "vi": "Về mặt lý thuyết, nếu bạn có thể gấp một tờ giấy 42 lần, nó sẽ chạm tới Mặt Trăng.",
        "zh": "理论上，如果你能将一张纸折叠42次，它将能到达月球。",
        "hi": "सिद्धांत रूप में, यदि आप एक कागज़ के टुकड़े को 42 बार मोड़ सकें, तो यह चंद्रमा तक पहुंच जाएगा।",
    },
    "The Eiffel Tower grows taller in summer; heat expands the metal by about 15 centimeters.": {
        "de": "Der Eiffelturm wird im Sommer durch Wärmeausdehnung des Metalls um etwa 15 cm größer.",
        "es": "La Torre Eiffel crece ~15 cm en verano por la dilatación térmica del metal.",
        "ko": "에펠탑은 여름에 더 높아집니다; 열이 금속을 약 15센티미터 팽창시킵니다.",
        "pt": "A Torre Eiffel fica mais alta no verão; o calor expande o metal em cerca de 15 centímetros.",
        "fr": "La Tour Eiffel grandit en été; la chaleur dilate le métal d'environ 15 centimètres.",
        "vi": "Tháp Eiffel cao hơn vào mùa hè; nhiệt làm giãn kim loại khoảng 15 cm.",
        "zh": "埃菲尔铁塔在夏天会变得更高；热量使金属膨胀约15厘米。",
        "hi": "एफिल टॉवर गर्मियों में लंबा होता है; गर्मी धातु को लगभग 15 सेंटीमीटर तक फैला देती है।",
    },
    "Honey never spoils — archaeologists have found 3,000-year-old honey that's still edible.": {
        "de": "Honig wird nie schlecht – Archäologen fanden 3 000 Jahre alten Honig, der noch essbar war.",
        "es": "La miel nunca caduca; arqueólogos han encontrado miel de 3 000 años aún comestible.",
        "ko": "꿀은 절대 상하지 않습니다 — 고고학자들이 여전히 먹을 수 있는 3,000년 된 꿀을 발견했습니다.",
        "pt": "O mel nunca estraga — arqueólogos encontraram mel com 3.000 anos que ainda é comestível.",
        "fr": "Le miel ne se gâte jamais — des archéologues ont trouvé du miel vieux de 3 000 ans encore comestible.",
        "vi": "Mật ong không bao giờ hỏng — các nhà khảo cổ đã tìm thấy mật ong 3.000 năm tuổi vẫn còn ăn được.",
        "zh": "蜂蜜永不变质——考古学家发现了3,000年前仍可食用的蜂蜜。",
        "hi": "शहद कभी खराब नहीं होता — पुरातत्वविदों ने 3,000 साल पुराना शहद पाया जो अभी भी खाने योग्य था।",
    },
    "A day on Venus is longer than a year on Venus — it rotates so slowly that it spins once per orbit.": {
        "de": "Ein Tag auf der Venus ist länger als ein Jahr auf der Venus – sie dreht sich so langsam wie eine Umlaufbahn.",
        "es": "Un día en Venus es más largo que un año en Venus: gira tan despacio que completa una vuelta por órbita.",
        "ko": "금성의 하루는 금성의 일 년보다 길습니다 — 너무 느리게 자전하여 궤도마다 한 번 자전합니다.",
        "pt": "Um dia em Vênus é mais longo que um ano em Vênus — ela gira tão lentamente que gira uma vez por órbita.",
        "fr": "Un jour sur Vénus est plus long qu'une année sur Vénus — elle tourne si lentement qu'elle fait une rotation par orbite.",
        "vi": "Một ngày trên Sao Kim dài hơn một năm trên Sao Kim — nó quay quá chậm đến mức quay đúng một vòng mỗi quỹ đạo.",
        "zh": "金星上的一天比金星上的一年还长——它旋转如此缓慢，每绕轨道一圈才自转一次。",
        "hi": "शुक्र पर एक दिन शुक्र पर एक साल से लंबा है — यह इतनी धीरे घूमता है कि प्रति कक्षा एक बार घूमता है।",
    },
    "The fingerprints of koalas are so similar to humans' that they've confused crime scene investigators.": {
        "de": "Koala-Fingerabdrücke ähneln menschlichen so sehr, dass sie Kriminaltechniker schon verwirrt haben.",
        "es": "Las huellas dactilares de los koalas son tan similares a las humanas que han confundido a investigadores forenses.",
        "ko": "코알라의 지문은 인간의 것과 너무 유사하여 범죄 수사관들을 혼란스럽게 한 적이 있습니다.",
        "pt": "As impressões digitais dos coalas são tão semelhantes às dos humanos que já confundiram investigadores de cenas de crime.",
        "fr": "Les empreintes digitales des koalas sont si similaires à celles des humains qu'elles ont confondu des enquêteurs de scènes de crime.",
        "vi": "Dấu vân tay của gấu túi rất giống với con người đến mức đã gây nhầm lẫn cho các điều tra viên hiện trường.",
        "zh": "考拉的指纹与人类的如此相似，以至于曾让犯罪现场调查人员感到困惑。",
        "hi": "कोआला के उंगलियों के निशान इंसानों के निशानों से इतने मिलते-जुलते हैं कि इन्होंने अपराध स्थल जांचकर्ताओं को भ्रमित कर दिया है।",
    },
    "You can't hum while holding your nose closed — try it, it's impossible.": {
        "de": "Du kannst nicht summen, wenn du dir die Nase zuhältst – probiere es, es ist unmöglich.",
        "es": "No puedes tararear tapándote la nariz; inténtalo, es imposible.",
        "ko": "코를 막고 콧노래를 부를 수 없습니다 — 해보세요, 불가능합니다.",
        "pt": "Você não pode cantarolar enquanto segura o nariz — tente, é impossível.",
        "fr": "Vous ne pouvez pas fredonner en vous tenant le nez fermé — essayez, c'est impossible.",
        "vi": "Bạn không thể ngân nga khi bịt mũi — thử đi, không thể được.",
        "zh": "你无法在捏住鼻子的同时哼歌——试试看，这是不可能的。",
        "hi": "आप नाक बंद रखते हुए गुनगुना नहीं सकते — कोशिश करें, यह असंभव है।",
    },
    "Some turtles can breathe through their rear ends during hibernation — it's called cloacal respiration.": {
        "de": "Manche Schildkröten atmen im Winterschlaf durch ihren Hintern – das nennt sich Kloakalatmung.",
        "es": "Algunas tortugas respiran por la cloaca durante la hibernación, en lo que se llama respiración cloacal.",
        "ko": "일부 거북이는 동면 중 항문으로 호흡할 수 있습니다 — 이를 총배설강 호흡이라고 합니다.",
        "pt": "Algumas tartarugas podem respirar pela parte traseira durante a hibernação — chama-se respiração cloacal.",
        "fr": "Certaines tortues peuvent respirer par leur arrière-train pendant l'hibernation — c'est la respiration cloacale.",
        "vi": "Một số rùa có thể thở qua phần sau trong kỳ ngủ đông — gọi là hô hấp cloacal.",
        "zh": "一些乌龟在冬眠期间可以通过尾部呼吸——这被称为泄殖腔呼吸。",
        "hi": "कुछ कछुए शीतनिद्रा के दौरान अपने पीछे से सांस ले सकते हैं — इसे क्लोकल श्वसन कहते हैं।",
    },
    "There's enough DNA in your body to stretch from the Sun to Pluto and back — 17 times.": {
        "de": "Die DNA deines Körpers würde von der Sonne bis Pluto und zurück reichen – 17-mal.",
        "es": "El ADN de tu cuerpo se extendería del Sol a Plutón y de vuelta 17 veces.",
        "ko": "당신의 체내 DNA를 펼치면 태양에서 명왕성까지 17번 왕복할 수 있습니다.",
        "pt": "Há DNA suficiente no seu corpo para esticar do Sol a Plutão e de volta — 17 vezes.",
        "fr": "Il y a assez d'ADN dans votre corps pour s'étirer du Soleil à Pluton et retour — 17 fois.",
        "vi": "DNA trong cơ thể bạn đủ để trải dài từ Mặt Trời đến Sao Diêm Vương và trở lại — 17 lần.",
        "zh": "您体内的DNA足以从太阳延伸到冥王星再回来——17次。",
        "hi": "आपके शरीर में पर्याप्त DNA है जो सूर्य से प्लूटो और वापस — 17 बार — तक फैल सके।",
    },
    "A teaspoon of neutron star material would weigh about six billion tons.": {
        "de": "Ein Teelöffel Neutronenstermmaterial würde etwa sechs Milliarden Tonnen wiegen.",
        "es": "Una cucharadita de materia de estrella de neutrones pesaría unos seis mil millones de toneladas.",
        "ko": "중성자 별 물질 한 찻숟가락은 약 60억 톤의 무게가 나갑니다.",
        "pt": "Uma colher de chá de material de estrela de nêutrons pesaria cerca de seis bilhões de toneladas.",
        "fr": "Une cuillère à café de matière d'étoile à neutrons pèserait environ six milliards de tonnes.",
        "vi": "Một thìa cà phê vật chất sao neutron sẽ nặng khoảng sáu tỷ tấn.",
        "zh": "一茶匙中子星物质的重量约为60亿吨。",
        "hi": "न्यूट्रॉन तारे की सामग्री का एक चम्मच लगभग 6 अरब टन वजन का होगा।",
    },
    "The shortest war in history was between Britain and Zanzibar in 1896 — it lasted 38 minutes.": {
        "de": "Der kürzeste Krieg der Geschichte war der zwischen Großbritannien und Sansibar 1896 – er dauerte 38 Minuten.",
        "es": "La guerra más corta de la historia fue entre Gran Bretaña y Zanzíbar en 1896: duró 38 minutos.",
        "ko": "역사상 가장 짧은 전쟁은 1896년 영국과 잔지바르 사이였습니다 — 38분간 지속되었습니다.",
        "pt": "A guerra mais curta da história foi entre a Grã-Bretanha e Zanzibar em 1896 — durou 38 minutos.",
        "fr": "La guerre la plus courte de l'histoire était entre la Grande-Bretagne et Zanzibar en 1896 — elle a duré 38 minutes.",
        "vi": "Cuộc chiến ngắn nhất trong lịch sử là giữa Anh và Zanzibar năm 1896 — kéo dài 38 phút.",
        "zh": "历史上最短的战争是1896年英国与桑给巴尔之间的战争——持续了38分钟。",
        "hi": "इतिहास की सबसे छोटी लड़ाई 1896 में ब्रिटेन और ज़ांज़ीबार के बीच थी — यह 38 मिनट चली।",
    },
    "Cows have best friends and get stressed when they're separated.": {
        "de": "Kühe haben beste Freunde und werden gestresst, wenn sie voneinander getrennt werden.",
        "es": "Las vacas tienen mejores amigos y se estresan cuando las separan.",
        "ko": "소에게는 절친한 친구가 있으며 분리되면 스트레스를 받습니다.",
        "pt": "As vacas têm melhores amigos e ficam estressadas quando são separadas.",
        "fr": "Les vaches ont des meilleurs amis et sont stressées quand elles sont séparées.",
        "vi": "Bò có bạn thân và bị căng thẳng khi bị tách ra.",
        "zh": "奶牛有最好的朋友，当它们被分开时会感到压力。",
        "hi": "गायों के प्रिय मित्र होते हैं और जब उन्हें अलग किया जाता है तो वे तनावग्रस्त हो जाती हैं।",
    },
    "Space smells like seared steak — astronauts report the odor comes from dying stars and cosmic dust.": {
        "de": "Das Weltall riecht nach angebratenem Steak – laut Astronauten stammt der Geruch von sterbenden Sternen und kosmischem Staub.",
        "es": "El espacio huele a carne a la parrilla; los astronautas dicen que el olor proviene de estrellas moribundas y polvo cósmico.",
        "ko": "우주는 구운 스테이크 냄새가 납니다 — 우주비행사들은 그 냄새가 죽어가는 별과 우주 먼지에서 온다고 보고합니다.",
        "pt": "O espaço cheira a bife selado — os astronautas relatam que o odor vem de estrelas moribundas e poeira cósmica.",
        "fr": "L'espace sent le steak grillé — les astronautes rapportent que l'odeur provient d'étoiles mourantes et de poussière cosmique.",
        "vi": "Không gian có mùi như bít tết nướng — các phi hành gia cho biết mùi đến từ các ngôi sao đang tắt và bụi vũ trụ.",
        "zh": "太空闻起来像烤牛排——宇航员报告说气味来自垂死的星球和宇宙尘埃。",
        "hi": "अंतरिक्ष में भुने हुए स्टेक की तरह गंध आती है — अंतरिक्ष यात्री रिपोर्ट करते हैं कि गंध मरते हुए तारों और ब्रह्मांडीय धूल से आती है।",
    },

    # ================================================================= #
    # Daily Country/Language Facts  (daily_widgets.py – COUNTRY_FACTS[i]["text"])
    # ================================================================= #
    "Did you know? Papua New Guinea is the most linguistically diverse country on Earth. With over 800 indigenous languages, it houses roughly 12% of the world's languages despite its small population.": {
        "de": "Papua-Neuguinea ist das sprachlich vielfältigste Land der Welt: Über 800 Sprachen – rund 12 % aller Weltsprachen – trotz kleiner Bevölkerung.",
        "es": "Papúa Nueva Guinea es el país más diverso lingüísticamente: más de 800 idiomas, el ~12 % de los del mundo, pese a su pequeña población.",
        "ko": "파푸아뉴기니는 세계에서 언어적으로 가장 다양한 나라입니다. 800개 이상의 토착 언어가 있어 세계 언어의 약 12%를 차지합니다.",
        "pt": "Papua Nova Guiné é o país linguisticamente mais diverso do mundo. Com mais de 800 línguas indígenas, abriga ~12% das línguas do mundo apesar de sua pequena população.",
        "fr": "La Papouasie-Nouvelle-Guinée est le pays linguistiquement le plus diversifié au monde. Avec plus de 800 langues indigènes, elle abrite ~12% des langues mondiales malgré sa petite population.",
        "vi": "Papua New Guinea là quốc gia đa dạng ngôn ngữ nhất trên Trái Đất. Với hơn 800 ngôn ngữ bản địa, chiếm ~12% ngôn ngữ thế giới dù dân số ít.",
        "zh": "巴布亚新几内亚是世界上语言最多元化的国家。尽管人口不多，却拥有800多种土著语言，约占世界语言的12%。",
        "hi": "पापुआ न्यू गिनी पृथ्वी पर भाषाई रूप से सबसे विविध देश है। 800 से अधिक स्वदेशी भाषाओं के साथ, यह छोटी आबादी के बावजूद विश्व की ~12% भाषाएं रखता है।",
    },
    "A musical masterpiece: South Africa's national anthem is globally unique. Its lyrics seamlessly switch between five of the country's twelve official languages: Xhosa, Zulu, Sesotho, Afrikaans, and English.": {
        "de": "Südafrikas Nationalhymne ist einzigartig: Ihre Texte wechseln nahtlos zwischen fünf der zwölf Amtssprachen – Xhosa, Zulu, Sesotho, Afrikaans und Englisch.",
        "es": "El himno nacional sudafricano es único: su letra alterna cinco de las doce lenguas oficiales del país: xhosa, zulú, sesoto, afrikáans e inglés.",
        "ko": "남아프리카 국가는 세계적으로 독특합니다. 가사가 코사어, 줄루어, 소토어, 아프리칸스어, 영어 등 12개 공식 언어 중 5개를 원활하게 전환합니다.",
        "pt": "O hino nacional da África do Sul é globalmente único. Suas letras alternam perfeitamente entre cinco das doze línguas oficiais do país: Xhosa, Zulu, Sesotho, Africâner e Inglês.",
        "fr": "L'hymne national sud-africain est unique au monde. Ses paroles alternent parfaitement entre cinq des douze langues officielles du pays: Xhosa, Zulu, Sesotho, Afrikaans et Anglais.",
        "vi": "Quốc ca Nam Phi độc nhất trên thế giới. Lời bài hát chuyển đổi liền mạch giữa năm trong số mười hai ngôn ngữ chính thức: Xhosa, Zulu, Sesotho, Afrikaans và Anh.",
        "zh": "南非国歌在全球独一无二。歌词在该国十二种官方语言中的五种之间无缝切换：科萨语、祖鲁语、索托语、南非荷兰语和英语。",
        "hi": "दक्षिण अफ्रीका का राष्ट्रगान विश्व में अद्वितीय है। इसके बोल देश की बारह आधिकारिक भाषाओं में से पांच के बीच सहजता से बदलते हैं।",
    },
    "A touch of antiquity: Because Latin is the official language of the Catholic Church, Vatican City is the only country in the world offering ATMs with a Latin language interface.": {
        "de": "Da Latein die Amtssprache der Katholischen Kirche ist, ist der Vatikan das einzige Land der Welt mit Geldautomaten auf Lateinisch.",
        "es": "Como el latín es la lengua oficial de la Iglesia católica, el Vaticano es el único país del mundo con cajeros automáticos en latín.",
        "ko": "라틴어가 가톨릭 교회의 공식 언어이기 때문에, 바티칸 시국은 라틴어 인터페이스가 있는 ATM을 제공하는 유일한 나라입니다.",
        "pt": "Porque o latim é a língua oficial da Igreja Católica, a Cidade do Vaticano é o único país do mundo que oferece ATMs com interface em latim.",
        "fr": "Parce que le latin est la langue officielle de l'Église catholique, la Cité du Vatican est le seul pays au monde à proposer des distributeurs automatiques avec une interface en latin.",
        "vi": "Vì tiếng Latin là ngôn ngữ chính thức của Giáo hội Công giáo, Vatican là quốc gia duy nhất trên thế giới có máy ATM với giao diện tiếng Latin.",
        "zh": "因为拉丁语是天主教的官方语言，梵蒂冈城是世界上唯一提供拉丁语界面ATM的国家。",
        "hi": "क्योंकि लैटिन कैथोलिक चर्च की आधिकारिक भाषा है, वेटिकन सिटी दुनिया का एकमात्र देश है जो लैटिन भाषा इंटरफ़ेस वाले ATM प्रदान करता है।",
    },
    "A matter of perception: Historically, Japan used only one word ('ao') for both blue and green. Due to this linguistic quirk, Japanese traffic lights often illuminate in a distinct blue instead of green.": {
        "de": "Japan nutzte historisch nur ein Wort ('ao') für Blau und Grün. Deshalb leuchten japanische Ampeln oft eher blau als grün.",
        "es": "Históricamente, Japón usaba una sola palabra («ao») para azul y verde. Por eso los semáforos japoneses suelen ser azulados.",
        "ko": "역사적으로 일본은 파란색과 초록색 둘 다 '아오'라는 단어 하나만 사용했습니다. 이 언어적 특이성 때문에 일본 신호등은 종종 초록이 아닌 파란색으로 켜집니다.",
        "pt": "Historicamente, o Japão usava apenas uma palavra ('ao') tanto para azul quanto para verde. Por causa dessa peculiaridade linguística, os semáforos japoneses frequentemente iluminam em azul.",
        "fr": "Historiquement, le Japon n'utilisait qu'un seul mot ('ao') pour le bleu et le vert. En raison de cette particularité linguistique, les feux de circulation japonais s'illuminent souvent en bleu.",
        "vi": "Lịch sử, Nhật Bản chỉ dùng một từ ('ao') cho cả màu xanh lam lẫn xanh lá. Do đặc điểm ngôn ngữ này, đèn giao thông Nhật thường sáng màu xanh lam.",
        "zh": "历史上，日本用同一个词('ao')表示蓝色和绿色。由于这种语言特点，日本交通灯经常照亮为蓝色而非绿色。",
        "hi": "ऐतिहासिक रूप से, जापान में नीले और हरे दोनों के लिए एक ही शब्द ('ao') था। इस भाषाई विशेषता के कारण, जापानी ट्रैफिक लाइटें अक्सर हरे की बजाय नीले रंग में जलती हैं।",
    },
    "A record holder for inclusion: Bolivia holds the world record for the most official languages. Alongside Spanish, the country's constitution recognizes a staggering 36 indigenous languages as completely equal.": {
        "de": "Bolivien hält den Rekord der meisten Amtssprachen: Neben Spanisch erkennt die Verfassung 36 indigene Sprachen als gleichwertig an.",
        "es": "Bolivia tiene el récord de idiomas oficiales: junto al español, su constitución reconoce 36 lenguas indígenas como plenamente iguales.",
        "ko": "볼리비아는 공식 언어 수 세계 기록 보유자입니다. 스페인어와 함께 헌법은 36개의 토착 언어를 완전히 동등하게 인정합니다.",
        "pt": "A Bolívia detém o recorde mundial de mais línguas oficiais. Além do espanhol, a constituição do país reconhece incríveis 36 línguas indígenas como completamente iguais.",
        "fr": "La Bolivie détient le record mondial du plus grand nombre de langues officielles. En plus de l'espagnol, la constitution du pays reconnaît 36 langues indigènes comme complètement égales.",
        "vi": "Bolivia giữ kỷ lục thế giới về số ngôn ngữ chính thức nhiều nhất. Ngoài tiếng Tây Ban Nha, hiến pháp công nhận 36 ngôn ngữ bản địa hoàn toàn bình đẳng.",
        "zh": "玻利维亚保持着官方语言最多的世界记录。除西班牙语外，该国宪法承认36种土著语言具有完全平等的地位。",
        "hi": "बोलीविया के पास सबसे अधिक आधिकारिक भाषाओं का विश्व रिकॉर्ड है। स्पेनिश के साथ, देश का संविधान 36 स्वदेशी भाषाओं को पूरी तरह समान मानता है।",
    },
    "A linguistic quirk: The Irish language (Gaeilge) has no direct words for 'yes' or 'no'. Instead, you answer by repeating the question's verb in either a positive or negative form.": {
        "de": "Das Irische (Gaeilge) hat keine direkte Entsprechung für 'Ja' oder 'Nein'. Stattdessen wiederholt man das Verb der Frage in positiver oder negativer Form.",
        "es": "El irlandés (gaélico) no tiene palabras para «sí» o «no»; se responde repitiendo el verbo de la pregunta en forma afirmativa o negativa.",
        "ko": "아일랜드어(게일어)에는 '예' 또는 '아니오'에 해당하는 직접적인 단어가 없습니다. 대신 질문의 동사를 긍정 또는 부정 형태로 반복하여 대답합니다.",
        "pt": "O irlandês (Gaeilge) não tem palavras diretas para 'sim' ou 'não'. Em vez disso, você responde repetindo o verbo da pergunta de forma positiva ou negativa.",
        "fr": "La langue irlandaise (Gaeilge) n'a pas de mots directs pour 'oui' ou 'non'. Au lieu de cela, vous répondez en répétant le verbe de la question sous forme positive ou négative.",
        "vi": "Tiếng Ireland (Gaeilge) không có từ trực tiếp cho 'có' hoặc 'không'. Thay vào đó, bạn trả lời bằng cách lặp lại động từ của câu hỏi theo dạng khẳng định hoặc phủ định.",
        "zh": "爱尔兰语（盖尔语）没有直接的'是'或'否'词语。相反，你通过以肯定或否定形式重复问题的动词来回答。",
        "hi": "आयरिश भाषा (गाएलगे) में 'हां' या 'नहीं' के लिए कोई सीधे शब्द नहीं हैं। इसके बजाय, आप प्रश्न के क्रिया को सकारात्मक या नकारात्मक रूप में दोहराकर उत्तर देते हैं।",
    },
    "An artificial alphabet: The Korean script, Hangul, didn't evolve naturally; it was invented in 1443. The letter shapes ingeniously mimic the anatomical positions of your tongue and lips when speaking.": {
        "de": "Das koreanische Alphabet Hangul wurde 1443 erfunden – die Buchstabenformen ahmen die Mund- und Zungenstellungen beim Sprechen nach.",
        "es": "El hangul coreano fue inventado en 1443; las formas de sus letras imitan las posiciones de lengua y labios al hablar.",
        "ko": "한글은 자연적으로 발전한 것이 아니라 1443년에 창제되었습니다. 글자 모양은 발음 시 혀와 입술의 해부학적 위치를 교묘하게 모방합니다.",
        "pt": "O alfabeto coreano, Hangul, não evoluiu naturalmente; foi inventado em 1443. As formas das letras imitam as posições anatômicas da língua e lábios ao falar.",
        "fr": "L'alphabet coréen, le Hangul, n'a pas évolué naturellement; il a été inventé en 1443. Les formes des lettres imitent astucieusement les positions anatomiques de la langue et des lèvres lors de la parole.",
        "vi": "Chữ viết Hàn Quốc, Hangul, không phát triển tự nhiên; nó được phát minh năm 1443. Hình dạng các chữ cái khéo léo bắt chước vị trí giải phẫu của lưỡi và môi khi nói.",
        "zh": "韩文字母表韩文不是自然演化的；它于1443年被发明。字母形状巧妙地模仿了说话时舌头和嘴唇的解剖位置。",
        "hi": "कोरियाई लिपि, हांगुल, प्राकृतिक रूप से विकसित नहीं हुई; इसे 1443 में आविष्कार किया गया था। अक्षर के आकार बोलते समय जीभ और होठों की शारीरिक स्थितियों की नकल करते हैं।",
    },
    "Whistling instead of speaking: On the Canary Island of La Gomera, locals communicate across vast valleys using 'Silbo Gomero'—a fully whistled version of Spanish that translates vowels and consonants into tones.": {
        "de": "Auf der Kanareninsel La Gomera kommunizieren Einheimische über weite Täler mit 'Silbo Gomero' – einer vollständig gepfiffenen Version des Spanischen.",
        "es": "En La Gomera se comunican con el «Silbo Gomero», una versión completamente silbada del español que traduce vocales y consonantes en tonos.",
        "ko": "카나리아 제도 라 고메라에서 현지인들은 모음과 자음을 음조로 변환하는 완전히 휘파람으로 된 스페인어 버전인 '실보 고메로'를 사용해 넓은 계곡을 가로질러 소통합니다.",
        "pt": "Na Ilha Canária de La Gomera, os locais se comunicam por vastos vales usando 'Silbo Gomero' — uma versão inteiramente assobiada do espanhol que traduz vogais e consoantes em tons.",
        "fr": "Sur l'île canarienne de La Gomera, les habitants communiquent à travers de vastes vallées en utilisant le 'Silbo Gomero' — une version entièrement sifflée de l'espagnol.",
        "vi": "Trên đảo Canary La Gomera, người dân giao tiếp qua các thung lũng rộng lớn bằng 'Silbo Gomero' — phiên bản tiếng Tây Ban Nha hoàn toàn bằng tiếng huýt sáo.",
        "zh": "在加那利岛拉戈梅拉岛，当地人使用'Silbo Gomero'横跨广阔山谷交流——一种完全用口哨发音的西班牙语版本。",
        "hi": "कैनरी द्वीप ला गोमेरा पर, स्थानीय लोग 'सिल्बो गोमेरो' का उपयोग करके विशाल घाटियों में संवाद करते हैं — स्पेनिश का पूरी तरह से सीटी वाला संस्करण।",
    },
    "Absolute orientation: The Australian Aboriginal language Guugu Yimithirr lacks words for 'left' or 'right'. Speakers use only cardinal directions, giving them an incredibly precise internal compass from birth.": {
        "de": "Die australische Aborigine-Sprache Guugu Yimithirr kennt kein 'links' oder 'rechts' – Sprecher nutzen nur Himmelsrichtungen und besitzen einen präzisen inneren Kompass.",
        "es": "El guugu yimithirr australiano no tiene «izquierda» ni «derecha»; sus hablantes usan puntos cardinales y tienen un compás interno extraordinario.",
        "ko": "호주 원주민 언어 구구 이미티르에는 '왼쪽'이나 '오른쪽'에 해당하는 단어가 없습니다. 화자들은 방위만 사용하여 태어날 때부터 정밀한 내부 나침반을 갖습니다.",
        "pt": "A língua aborígene australiana Guugu Yimithirr não tem palavras para 'esquerda' ou 'direita'. Os falantes usam apenas direções cardinais, dando-lhes uma bússola interna incrivelmente precisa.",
        "fr": "La langue aborigène australienne Guugu Yimithirr n'a pas de mots pour 'gauche' ou 'droite'. Les locuteurs n'utilisent que les directions cardinales, leur donnant une boussole interne incroyablement précise.",
        "vi": "Ngôn ngữ thổ dân Úc Guugu Yimithirr không có từ cho 'trái' hay 'phải'. Người nói chỉ dùng phương hướng cơ bản, cho họ la bàn nội tâm cực kỳ chính xác từ khi sinh.",
        "zh": "澳大利亚土著语言Guugu Yimithirr缺乏'左'或'右'的词汇。说话者只使用基本方向，使他们从出生起就拥有极其精确的内部罗盘。",
        "hi": "ऑस्ट्रेलियाई आदिवासी भाषा गुगु यिमिथिर में 'बाएं' या 'दाएं' के लिए शब्द नहीं हैं। वक्ता केवल दिशाओं का उपयोग करते हैं, जिससे उन्हें जन्म से अविश्वसनीय रूप से सटीक आंतरिक कम्पास मिलता है।",
    },
    "Strict naming rules: In Iceland, you can't just pick any name for a child. A government Naming Committee strictly reviews new names to ensure they follow traditional Icelandic grammatical rules.": {
        "de": "In Island prüft ein staatlicher Namensausschuss jeden Kindesnamen streng darauf, ob er den isländischen Grammatikregeln entspricht.",
        "es": "En Islandia, un Comité de Nombres gubernamental revisa rigurosamente los nombres de bebés para que cumplan las reglas gramaticales islandesas.",
        "ko": "아이슬란드에서는 아이 이름을 마음대로 정할 수 없습니다. 정부 이름 위원회가 새 이름이 전통적인 아이슬란드어 문법 규칙을 따르는지 엄격히 검토합니다.",
        "pt": "Na Islândia, você não pode simplesmente escolher qualquer nome para uma criança. Um Comitê de Nomes governamental revisa rigorosamente novos nomes para garantir que sigam as regras gramaticais islandesas.",
        "fr": "En Islande, vous ne pouvez pas simplement choisir n'importe quel nom pour un enfant. Un Comité des Noms gouvernemental examine strictement les nouveaux noms pour s'assurer qu'ils suivent les règles grammaticales islandaises.",
        "vi": "Ở Iceland, bạn không thể tùy ý đặt tên cho trẻ. Một Ủy ban Đặt tên của chính phủ xem xét nghiêm ngặt các tên mới để đảm bảo chúng theo quy tắc ngữ pháp Iceland truyền thống.",
        "zh": "在冰岛，你不能随意给孩子取名。政府命名委员会严格审查新名字，确保它们遵循传统冰岛语语法规则。",
        "hi": "आइसलैंड में, आप बच्चे के लिए कोई भी नाम नहीं चुन सकते। एक सरकारी नामकरण समिति नए नामों की सख्ती से समीक्षा करती है।",
    },
    "It's astounding: Mandarin Chinese doesn't use a standard alphabet, but rather thousands of individual characters. To fluently read a daily newspaper, you must memorize approximately 3,000 of these logograms.": {
        "de": "Mandarin verwendet kein Alphabet, sondern tausende Schriftzeichen. Zum flüssigen Zeitunglesen braucht man rund 3 000 davon auswendig.",
        "es": "El chino mandarín no usa alfabeto, sino miles de caracteres. Para leer un periódico con fluidez hay que memorizar ~3 000 logograma.",
        "ko": "놀랍게도 중국어 보통화는 표준 알파벳이 아닌 수천 개의 개별 문자를 사용합니다. 일간 신문을 유창하게 읽으려면 약 3,000개의 표의문자를 암기해야 합니다.",
        "pt": "O mandarim não usa um alfabeto padrão, mas sim milhares de caracteres individuais. Para ler fluentemente um jornal diário, você deve memorizar aproximadamente 3.000 desses logograma.",
        "fr": "Le mandarin n'utilise pas un alphabet standard, mais plutôt des milliers de caractères individuels. Pour lire couramment un journal quotidien, vous devez mémoriser environ 3 000 de ces logogrammes.",
        "vi": "Tiếng Quan Thoại không dùng bảng chữ cái chuẩn mà dùng hàng nghìn ký tự riêng lẻ. Để đọc báo hằng ngày thành thạo, bạn phải thuộc ~3.000 chữ tượng hình.",
        "zh": "令人惊叹：普通话不使用标准字母，而是使用数千个个别汉字。要流利地阅读日报，您必须记住大约3,000个这样的象形文字。",
        "hi": "मंदारिन चीनी मानक वर्णमाला का उपयोग नहीं करती, बल्कि हजारों व्यक्तिगत अक्षरों का। दैनिक समाचार पत्र धाराप्रवाह पढ़ने के लिए आपको लगभग 3,000 लॉगोग्राम याद करने होंगे।",
    },
    "Historical irony: Despite being linguistic rivals today, French was actually the official language of the English royal court and nobility for nearly 300 years following the Norman Conquest in 1066.": {
        "de": "Trotz heutiger sprachlicher Rivalität war Französisch nach der normannischen Eroberung 1066 fast 300 Jahre lang die Sprache des englischen Hofes.",
        "es": "Pese a la rivalidad lingüística actual, el francés fue la lengua de la corte inglesa durante casi 300 años tras la conquista normanda de 1066.",
        "ko": "오늘날 언어적 경쟁자임에도 불구하고, 1066년 노르만 정복 이후 거의 300년 동안 프랑스어가 실제로 영국 왕실과 귀족의 공식 언어였습니다.",
        "pt": "Apesar de serem rivais linguísticos hoje, o francês foi a língua oficial da corte real inglesa e da nobreza por quase 300 anos após a Conquista Normanda em 1066.",
        "fr": "Malgré leur rivalité linguistique actuelle, le français était en fait la langue officielle de la cour royale anglaise et de la noblesse pendant près de 300 ans après la Conquête normande en 1066.",
        "vi": "Dù ngày nay là đối thủ ngôn ngữ, tiếng Pháp thực sự là ngôn ngữ chính thức của triều đình hoàng gia Anh và giới quý tộc gần 300 năm sau Cuộc chinh phục Norman năm 1066.",
        "zh": "尽管今天是语言竞争对手，但在1066年诺曼征服后，法语实际上是英国皇室和贵族的官方语言，长达近300年。",
        "hi": "आज भाषाई प्रतिद्वंद्वी होने के बावजूद, 1066 में नॉर्मन विजय के बाद लगभग 300 वर्षों तक फ्रेंच वास्तव में अंग्रेजी राजदरबार और कुलीनता की आधिकारिक भाषा थी।",
    },
    "Living in the present: The Finnish language completely lacks a grammatical future tense. Finns simply use the present tense for future events, relying entirely on conversational context to establish the timeframe.": {
        "de": "Das Finnische hat keine grammatische Zukunftsform. Finnen verwenden das Präsens für zukünftige Ereignisse und verlassen sich auf den Kontext.",
        "es": "El finlandés carece de tiempo futuro gramatical; los finlandeses usan el presente para eventos futuros y se apoyan en el contexto.",
        "ko": "핀란드어에는 문법적 미래 시제가 전혀 없습니다. 핀란드인들은 미래 사건에 현재 시제를 사용하며 시간적 맥락을 대화 컨텍스트에 완전히 의존합니다.",
        "pt": "O finlandês não tem tempo futuro gramatical. Os finlandeses simplesmente usam o tempo presente para eventos futuros, dependendo inteiramente do contexto conversacional.",
        "fr": "La langue finnoise n'a pas de temps futur grammatical. Les Finlandais utilisent simplement le temps présent pour les événements futurs, en se fiant entièrement au contexte conversationnel.",
        "vi": "Tiếng Phần Lan hoàn toàn không có thì tương lai ngữ pháp. Người Phần Lan đơn giản dùng thì hiện tại cho sự kiện tương lai, hoàn toàn dựa vào ngữ cảnh hội thoại.",
        "zh": "芬兰语完全缺乏语法上的将来时态。芬兰人简单地用现在时态来表示未来事件，完全依赖对话语境来建立时间框架。",
        "hi": "फ़िनिश भाषा में व्याकरणिक भविष्य काल पूरी तरह से नहीं है। फ़िन्स भविष्य की घटनाओं के लिए वर्तमान काल का उपयोग करते हैं, समय सीमा के लिए पूरी तरह बातचीत के संदर्भ पर निर्भर होते हैं।",
    },
    "Mind your punctuation: When writing a question in Greek, don't use a standard question mark. The official Greek question mark actually looks exactly like an English semicolon (;).": {
        "de": "Im Griechischen sieht das Fragezeichen wie ein englisches Semikolon aus (;) – nicht wie das übliche '?'.",
        "es": "En griego, el signo de interrogación oficial parece un punto y coma en inglés (;), no el usual «?».",
        "ko": "그리스어로 질문을 쓸 때 표준 물음표를 사용하지 마세요. 공식 그리스어 물음표는 영어 세미콜론(;)과 정확히 같이 생겼습니다.",
        "pt": "Ao escrever uma pergunta em grego, não use um ponto de interrogação padrão. O ponto de interrogação grego oficial parece exatamente um ponto e vírgula em inglês (;).",
        "fr": "Lors de l'écriture d'une question en grec, n'utilisez pas un point d'interrogation standard. Le point d'interrogation grec officiel ressemble exactement à un point-virgule anglais (;).",
        "vi": "Khi viết câu hỏi bằng tiếng Hy Lạp, đừng dùng dấu hỏi thông thường. Dấu hỏi chính thức của tiếng Hy Lạp trông giống hệt dấu chấm phẩy tiếng Anh (;).",
        "zh": "用希腊语写问题时，不要使用标准问号。官方希腊语问号实际上看起来与英语分号(;)完全相同。",
        "hi": "यूनानी में प्रश्न लिखते समय मानक प्रश्न चिह्न का उपयोग न करें। आधिकारिक यूनानी प्रश्न चिह्न वास्तव में अंग्रेजी अर्धविराम (;) जैसा दिखता है।",
    },
    "An absolute mystery: Euskara, spoken by the Basque people in Spain and France, is a language isolate. It has absolutely no known genealogical relationship to any other living language on Earth.": {
        "de": "Euskara (Baskisch) ist ein Sprachenklassat ohne bekannte genealogische Verwandtschaft zu einer anderen lebenden Sprache der Welt.",
        "es": "El euskera, lengua vasca de España y Francia, es un aislado lingüístico sin ningún parentesco genealógico conocido con otra lengua viva.",
        "ko": "스페인과 프랑스의 바스크 사람들이 사용하는 에우스카라는 언어 고립어입니다. 지구상의 다른 어떤 살아있는 언어와도 알려진 계통적 관계가 전혀 없습니다.",
        "pt": "O Euskara, falado pelo povo basco na Espanha e França, é um isolado linguístico. Não tem absolutamente nenhuma relação genealógica conhecida com qualquer outra língua viva na Terra.",
        "fr": "L'Euskara, parlé par le peuple basque en Espagne et en France, est un isolat linguistique. Il n'a absolument aucune relation généalogique connue avec aucune autre langue vivante sur Terre.",
        "vi": "Euskara, do người Basque ở Tây Ban Nha và Pháp nói, là một ngôn ngữ bị cô lập. Nó hoàn toàn không có quan hệ phả hệ đã biết với bất kỳ ngôn ngữ sống nào khác trên Trái Đất.",
        "zh": "由西班牙和法国巴斯克人使用的埃斯克语是一种语言孤立语言。它与地球上任何其他活着的语言完全没有已知的谱系关系。",
        "hi": "स्पेन और फ्रांस के बास्क लोगों द्वारा बोली जाने वाली एउस्कारा एक भाषाई पृथक्करण है। पृथ्वी पर किसी भी अन्य जीवित भाषा के साथ इसका कोई ज्ञात वंशावली संबंध नहीं है।",
    },
    "A singing culture: In the Indian village of Kongthong, residents don't use regular names. Instead, every person is assigned a unique melody composed by their mother, which is whistled to call them.": {
        "de": "Im indischen Dorf Kongthong haben Menschen keine Namen, sondern einzigartige Melodien, die ihre Mutter komponiert und zum Rufen gepfiffen wird.",
        "es": "En el pueblo indio de Kongthong, cada persona tiene una melodía única compuesta por su madre, que se silba para llamarla.",
        "ko": "인도 콩통 마을에서 주민들은 일반적인 이름을 사용하지 않습니다. 대신 모든 사람이 어머니가 작곡한 고유한 멜로디를 가지며, 이를 휘파람으로 불러 부릅니다.",
        "pt": "Na aldeia indiana de Kongthong, os residentes não usam nomes comuns. Em vez disso, cada pessoa recebe uma melodia única composta por sua mãe, que é assobiada para chamá-la.",
        "fr": "Dans le village indien de Kongthong, les résidents n'utilisent pas de noms ordinaires. Au lieu de cela, chaque personne se voit attribuer une mélodie unique composée par sa mère, sifflée pour les appeler.",
        "vi": "Ở làng Kongthong của Ấn Độ, cư dân không dùng tên thông thường. Thay vào đó, mỗi người được giao một giai điệu độc đáo do mẹ sáng tác, được huýt sáo để gọi họ.",
        "zh": "在印度村庄孔通，居民不使用普通名字。相反，每个人都被赋予一段由母亲创作的独特旋律，通过口哨声来呼唤他们。",
        "hi": "भारतीय गांव कोंगथोंग में, निवासी सामान्य नामों का उपयोग नहीं करते। इसके बजाय, हर व्यक्ति को उनकी माँ द्वारा रचित एक अनूठी धुन दी जाती है, जिसे सीटी बजाकर बुलाते हैं।",
    },
    "A completely different worldview: The Pirahã people of the Brazilian Amazon speak a language entirely lacking words for exact numbers or specific colors, relying only on concepts like 'few' or 'many'.": {
        "de": "Die Pirahã im brasilianischen Amazonas sprechen eine Sprache ohne exakte Zahlen oder Farbwörter – nur Konzepte wie 'wenige' oder 'viele'.",
        "es": "Los pirahã del Amazonas brasileño hablan una lengua sin palabras para números exactos ni colores concretos, solo «pocos» o «muchos».",
        "ko": "브라질 아마존의 피라항 사람들은 정확한 숫자나 특정 색상에 대한 단어가 전혀 없는 언어를 사용하며, '적은'이나 '많은' 같은 개념에만 의존합니다.",
        "pt": "O povo Pirahã do Amazonas brasileiro fala uma língua completamente desprovida de palavras para números exatos ou cores específicas, dependendo apenas de conceitos como 'poucos' ou 'muitos'.",
        "fr": "Le peuple Pirahã de l'Amazonie brésilienne parle une langue totalement dépourvue de mots pour les nombres exacts ou les couleurs spécifiques, se fiant uniquement à des concepts comme 'peu' ou 'beaucoup'.",
        "vi": "Người Pirahã ở Amazon Brazil nói một ngôn ngữ hoàn toàn thiếu từ cho số chính xác hay màu cụ thể, chỉ dựa vào các khái niệm như 'ít' hoặc 'nhiều'.",
        "zh": "巴西亚马逊的皮拉罕人说一种完全没有精确数字或特定颜色词汇的语言，只依赖'少'或'多'等概念。",
        "hi": "ब्राजील के अमेज़ॅन के पिराहा लोग एक ऐसी भाषा बोलते हैं जिसमें सटीक संख्याओं या विशिष्ट रंगों के लिए बिल्कुल कोई शब्द नहीं हैं।",
    },
    "A historical misunderstanding: The name 'Canada' stems from an explorer's mistake. He wrongly believed the Iroquoian word 'kanata'—which simply means 'village' or 'settlement'—was the specific name for the entire country.": {
        "de": "Der Name 'Kanada' geht auf einen Irrtum zurück: Ein Entdecker glaubte, das irokesische Wort 'kanata' (= Dorf) sei der Name des gesamten Landes.",
        "es": "«Canadá» nace de un error: un explorador creyó que la palabra iroquesa «kanata» (aldea) era el nombre del país entero.",
        "ko": "'캐나다'라는 이름은 탐험가의 실수에서 유래했습니다. 그는 이로쿼이어 단어 '카나타'—단순히 '마을'을 의미—가 나라 전체의 이름이라고 잘못 믿었습니다.",
        "pt": "O nome 'Canadá' vem de um erro de explorador. Ele erroneamente acreditou que a palavra iroquesa 'kanata'—que simplesmente significa 'aldeia'—era o nome específico do país inteiro.",
        "fr": "Le nom 'Canada' découle de l'erreur d'un explorateur. Il croyait à tort que le mot iroquois 'kanata'—qui signifie simplement 'village'—était le nom spécifique du pays entier.",
        "vi": "Tên 'Canada' xuất phát từ sai lầm của một nhà thám hiểm. Ông nhầm tưởng từ Iroquois 'kanata' — đơn giản có nghĩa là 'làng' — là tên riêng của cả quốc gia.",
        "zh": "'加拿大'这个名字来源于探险家的错误。他错误地认为易洛魁语词'kanata'——仅仅意为'村庄'——是整个国家的特定名称。",
        "hi": "'कनाडा' नाम एक खोजकर्ता की गलती से आया है। उसने गलत तरीके से सोचा कि इरोक्वोई शब्द 'कनाटा' — जिसका सीधा अर्थ है 'गांव' — पूरे देश का विशिष्ट नाम है।",
    },
    "A surprising greeting: The famous word 'Ciao', used today in Italian for both 'hello' and 'goodbye', originated in the Venetian dialect where it literally translated to 'I am your slave'.": {
        "de": "'Ciao' stammt aus dem venezianischen Dialekt und bedeutete ursprünglich 'Ich bin dein Sklave' – heute nutzt man es für Hallo und Tschüss.",
        "es": "«Ciao» viene del dialecto veneciano y significaba «soy tu esclavo»; hoy se usa en italiano para saludar y despedir.",
        "ko": "오늘날 이탈리아어에서 '안녕'과 '잘 가' 모두에 사용되는 'Ciao'는 '나는 당신의 노예입니다'를 의미했던 베네치아 방언에서 유래했습니다.",
        "pt": "A famosa palavra 'Ciao', usada hoje em italiano tanto para 'olá' quanto para 'tchau', originou-se no dialeto veneziano onde literalmente traduzia 'Sou seu escravo'.",
        "fr": "Le fameux mot 'Ciao', utilisé aujourd'hui en italien pour 'bonjour' et 'au revoir', est originaire du dialecte vénitien où il se traduisait littéralement par 'Je suis votre esclave'.",
        "vi": "Từ nổi tiếng 'Ciao', ngày nay dùng trong tiếng Ý cho cả 'xin chào' và 'tạm biệt', bắt nguồn từ phương ngữ Venice nơi nó nghĩa đen là 'Tôi là nô lệ của bạn'.",
        "zh": "著名的词'Ciao'，今天在意大利语中用作'你好'和'再见'，起源于威尼斯方言，字面意思是'我是你的奴隶'。",
        "hi": "प्रसिद्ध शब्द 'Ciao', आज इटालियन में 'हैलो' और 'अलविदा' दोनों के लिए उपयोग किया जाता है, वेनिशियन बोली में उत्पन्न हुआ जहाँ इसका शाब्दिक अर्थ था 'मैं आपका दास हूं'।",
    },
    "Culture encoded in law: The Kingdom of Bhutan measures national success by 'Gross National Happiness' rather than GDP. This Buddhist-inspired concept is officially enshrined directly in the country's constitution.": {
        "de": "Bhutan misst nationalen Erfolg am 'Bruttoinlandsglück' statt am BIP – ein buddhistisch inspiriertes Konzept, das direkt in der Verfassung verankert ist.",
        "es": "Bután mide el éxito nacional por la «Felicidad Nacional Bruta» en lugar del PIB, concepto budista consagrado en su constitución.",
        "ko": "부탄 왕국은 GDP 대신 '국민총행복'으로 국가 성공을 측정합니다. 이 불교에서 영감을 받은 개념은 공식적으로 국가 헌법에 명시되어 있습니다.",
        "pt": "O Reino do Butão mede o sucesso nacional pela 'Felicidade Nacional Bruta' em vez do PIB. Este conceito inspirado no Budismo é oficialmente consagrado na constituição do país.",
        "fr": "Le Royaume du Bhoutan mesure le succès national par le 'Bonheur National Brut' plutôt que par le PIB. Ce concept d'inspiration bouddhiste est officiellement inscrit dans la constitution du pays.",
        "vi": "Vương quốc Bhutan đo thành công quốc gia bằng 'Tổng Hạnh phúc Quốc gia' thay vì GDP. Khái niệm lấy cảm hứng từ Phật giáo này được chính thức ghi vào hiến pháp đất nước.",
        "zh": "不丹王国用'国民幸福总值'而非GDP来衡量国家成功。这个受佛教启发的概念被正式载入国家宪法。",
        "hi": "भूटान साम्राज्य GDP के बजाय 'सकल राष्ट्रीय खुशी' से राष्ट्रीय सफलता मापता है। यह बौद्ध-प्रेरित अवधारणा आधिकारिक रूप से देश के संविधान में निहित है।",
    },
    "A cartographical tongue-twister: The Welsh village of 'Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch' holds the record for Europe's longest place name. It meticulously describes the precise geographic location of the local parish church.": {
        "de": "Das walisische Dorf 'Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch' hält den Rekord für Europas längsten Ortsnamen und beschreibt die Lage der Pfarrkirche.",
        "es": "El pueblo galés «Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch» tiene el topónimo más largo de Europa y describe la ubicación de su iglesia parroquial.",
        "ko": "웨일스 마을 '란파이르풀그윈길고게리흐와이른드로뷜라안티실리오고고고흐'는 유럽에서 가장 긴 지명 기록을 보유합니다. 이는 지역 교구 교회의 정확한 지리적 위치를 세밀하게 묘사합니다.",
        "pt": "A aldeia galesa 'Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch' detém o recorde do nome de lugar mais longo da Europa. Descreve meticulosamente a localização geográfica precisa da igreja paroquial local.",
        "fr": "Le village gallois 'Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch' détient le record du plus long nom de lieu en Europe. Il décrit méticuleusement l'emplacement géographique précis de l'église paroissiale locale.",
        "vi": "Làng xứ Wales 'Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch' giữ kỷ lục tên địa danh dài nhất châu Âu. Nó mô tả tỉ mỉ vị trí địa lý chính xác của nhà thờ giáo xứ địa phương.",
        "zh": "威尔士村庄'Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch'保持着欧洲最长地名的记录。它详细描述了当地教区教堂的确切地理位置。",
        "hi": "वेल्श गांव 'Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch' यूरोप के सबसे लंबे स्थान नाम का रिकॉर्ड रखता है। यह स्थानीय पैरिश चर्च के सटीक भौगोलिक स्थान का सूक्ष्म वर्णन करता है।",
    },
    "A mark of inclusion: In 2006, New Zealand became the very first country in the world to make its national sign language (NZSL) an official state language, alongside English and Māori.": {
        "de": "Neuseeland wurde 2006 als erstes Land weltweit, das seine nationale Gebärdensprache (NZSL) neben Englisch und Māori zur Amtssprache erklärte.",
        "es": "En 2006, Nueva Zelanda fue el primer país en hacer oficial su lengua de señas (NZSL), junto al inglés y el māori.",
        "ko": "2006년, 뉴질랜드는 영어와 마오리어와 함께 국가 수화(NZSL)를 공식 국가 언어로 만든 세계 최초의 나라가 되었습니다.",
        "pt": "Em 2006, a Nova Zelândia tornou-se o primeiro país do mundo a tornar sua língua gestual nacional (NZSL) uma língua oficial do estado, ao lado do inglês e do māori.",
        "fr": "En 2006, la Nouvelle-Zélande est devenue le tout premier pays au monde à faire de sa langue des signes nationale (NZSL) une langue d'état officielle, aux côtés de l'anglais et du māori.",
        "vi": "Năm 2006, New Zealand trở thành quốc gia đầu tiên trên thế giới biến ngôn ngữ ký hiệu quốc gia (NZSL) thành ngôn ngữ chính thức, bên cạnh tiếng Anh và tiếng Māori.",
        "zh": "2006年，新西兰成为世界上第一个将国家手语(NZSL)与英语和毛利语并列为官方国家语言的国家。",
        "hi": "2006 में, न्यूजीलैंड दुनिया का पहला देश बना जिसने अपनी राष्ट्रीय सांकेतिक भाषा (NZSL) को अंग्रेजी और माओरी के साथ आधिकारिक राज्य भाषा बनाया।",
    },
    "Unique in typography: The letter 'ß' (Eszett) exists exclusively in written German. Interestingly, it isn't even used in German-speaking Switzerland, where writers consistently use a double 'ss' instead.": {
        "de": "Das 'ß' (Eszett) existiert nur im Deutschen – und nicht einmal im deutschsprachigen Schweiz, wo konsequent 'ss' geschrieben wird.",
        "es": "La letra «ß» (Eszett) existe únicamente en alemán y ni siquiera se usa en la Suiza germanófona, donde siempre se escribe «ss».",
        "ko": "'ß'(에스체트)는 독일어에서만 존재합니다. 흥미롭게도, 독일어권 스위스에서도 사용하지 않으며 대신 'ss'를 씁니다.",
        "pt": "A letra 'ß' (Eszett) existe exclusivamente no alemão escrito. Curiosamente, nem mesmo é usada na Suíça de língua alemã, onde os escritores consistentemente usam 'ss' duplo.",
        "fr": "La lettre 'ß' (Eszett) existe exclusivement en allemand écrit. De façon intéressante, elle n'est même pas utilisée en Suisse germanophone, où les écrivains utilisent systématiquement 'ss'.",
        "vi": "Chữ 'ß' (Eszett) chỉ tồn tại trong tiếng Đức viết. Thú vị là, nó không được dùng ở vùng nói tiếng Đức của Thụy Sĩ, nơi luôn viết 'ss' thay thế.",
        "zh": "'ß'(埃斯策特)字母仅存在于书面德语中。有趣的是，它甚至在德语区瑞士也不使用，那里的作者一致使用双'ss'。",
        "hi": "'ß' (एस्जेट) अक्षर विशेष रूप से लिखित जर्मन में मौजूद है। दिलचस्प बात यह है कि यह जर्मन-भाषी स्विट्जरलैंड में भी उपयोग नहीं किया जाता, जहां 'ss' लिखा जाता है।",
    },
    "No federal official language: Despite having the world's largest Spanish-speaking population, Spanish isn't Mexico's federal official language. Instead, 68 indigenous languages are recognized as co-equal national languages alongside it.": {
        "de": "Obwohl Mexiko die größte spanischsprachige Bevölkerung hat, ist Spanisch keine Bundesamtssprache – 68 indigene Sprachen sind gleichwertig anerkannt.",
        "es": "Pese a tener la mayor población hispanohablante, el español no es lengua federal oficial de México; 68 lenguas indígenas gozan del mismo rango.",
        "ko": "세계에서 가장 많은 스페인어 사용 인구를 가지고 있음에도 불구하고, 스페인어는 멕시코의 연방 공식 언어가 아닙니다. 대신 68개의 토착 언어가 동등한 국가 언어로 인정됩니다.",
        "pt": "Apesar de ter a maior população de língua espanhola do mundo, o espanhol não é a língua oficial federal do México. Em vez disso, 68 línguas indígenas são reconhecidas como línguas nacionais co-iguais.",
        "fr": "Malgré la plus grande population hispanophone du monde, l'espagnol n'est pas la langue officielle fédérale du Mexique. Au lieu de cela, 68 langues indigènes sont reconnues comme langues nationales co-égales.",
        "vi": "Dù có dân số nói tiếng Tây Ban Nha lớn nhất thế giới, tiếng Tây Ban Nha không phải là ngôn ngữ chính thức liên bang của Mexico. Thay vào đó, 68 ngôn ngữ bản địa được công nhận bình đẳng.",
        "zh": "尽管拥有世界上最大的西班牙语人口，西班牙语并非墨西哥的联邦官方语言。相反，68种土著语言被承认为同等的国家语言。",
        "hi": "दुनिया की सबसे बड़ी स्पेनिश-भाषी आबादी होने के बावजूद, स्पेनिश मेक्सिको की संघीय आधिकारिक भाषा नहीं है। इसके बजाय, 68 स्वदेशी भाषाओं को सह-समान राष्ट्रीय भाषाओं के रूप में मान्यता है।",
    },
    "Linguistic distance: Despite being in Central Europe, Hungarian belongs to the Uralic language family. Distantly related to Finnish, it is completely incomprehensible to all of Hungary's direct geographical neighbors.": {
        "de": "Ungarisch gehört zur uralischen Sprachfamilie und ist entfernt mit Finnisch verwandt – für alle direkten Nachbarländer völlig unverständlich.",
        "es": "El húngaro pertenece a la familia uralica y está emparentado lejosamente con el finlandés; es incomprensible para todos los vecinos de Hungría.",
        "ko": "중부 유럽에 있음에도 불구하고, 헝가리어는 우랄어족에 속합니다. 핀란드어와 먼 친척 관계에 있으며, 헝가리의 모든 직접적인 지리적 이웃 국가에게 완전히 이해하기 어렵습니다.",
        "pt": "Apesar de estar na Europa Central, o húngaro pertence à família linguística urálica. Distantemente relacionado ao finlandês, é completamente incompreensível para todos os vizinhos geográficos diretos da Hungria.",
        "fr": "Malgré sa situation en Europe centrale, le hongrois appartient à la famille linguistique ouralique. Lointainement lié au finnois, il est totalement incompréhensible pour tous les voisins géographiques directs de la Hongrie.",
        "vi": "Dù ở Trung Âu, tiếng Hungary thuộc ngữ hệ Uralic. Có quan hệ xa với tiếng Phần Lan, nó hoàn toàn không thể hiểu được đối với tất cả các nước láng giềng địa lý trực tiếp của Hungary.",
        "zh": "尽管位于中欧，匈牙利语属于乌拉尔语系。与芬兰语有远亲关系，对匈牙利所有直接地理邻国来说完全无法理解。",
        "hi": "मध्य यूरोप में होने के बावजूद, हंगेरियन उराल भाषा परिवार से संबंधित है। फिनिश से दूर का संबंध रखते हुए, यह हंगरी के सभी प्रत्यक्ष भौगोलिक पड़ोसियों के लिए पूरी तरह से समझ से बाहर है।",
    },

    # ================================================================= #
    # configuration.py – AIPlanHelperDialog
    # ================================================================= #

    # ================================================================= #
    # configuration.py – LearningPlanConfigDialog
    # ================================================================= #
    "Add": {
        "de": "Hinzufügen",
        "es": "Añadir",
        "ko": "추가",
        "pt": "Adicionar",
        "fr": "Ajouter",
        "vi": "Thêm",
        "zh": "添加",
        "hi": "जोड़ें",
    },
    "Remove Selected": {
        "de": "Ausgewählte entfernen",
        "es": "Eliminar seleccionados",
        "ko": "선택 항목 제거",
        "pt": "Remover selecionados",
        "fr": "Supprimer la sélection",
        "vi": "Xóa đã chọn",
        "zh": "删除所选",
        "hi": "चुने हुए हटाएं",
    },
    "Deadlines": {
        "de": "Fristen",
        "es": "Plazos",
        "ko": "마감일",
        "pt": "Prazos",
        "fr": "Échéances",
        "vi": "Hạn chót",
        "zh": "截止日期",
        "hi": "समय सीमाएं",
    },
    "Configure Deadlines": {
        "de": "Fristen konfigurieren",
        "es": "Configurar plazos",
        "ko": "마감일 설정",
        "pt": "Configurar prazos",
        "fr": "Configurer les échéances",
        "vi": "Cấu hình hạn chót",
        "zh": "配置截止日期",
        "hi": "समय सीमाएं कॉन्फ़िगर करें",
    },

    # ================================================================= #
    # configuration.py – StudyPlanTimelineDialog
    # ================================================================= #
    "Study Plan Timeline": {
        "de": "Lernplan-Zeitstrahl",
        "es": "Línea de tiempo del plan de estudio",
        "ko": "학습 계획 타임라인",
        "pt": "Linha do tempo do plano de estudos",
        "fr": "Chronologie du plan d\'étude",
        "vi": "Dòng thời gian kế hoạch học tập",
        "zh": "学习计划时间轴",
        "hi": "अध्ययन योजना टाइमलाइन",
    },

    # ================================================================= #
    # configuration.py – DeadlineConfigDialog
    # ================================================================= #
    "If no deadline is set as default, the nearest upcoming one is shown automatically.": {
        "de": "Wenn keine Frist als Standard gesetzt ist, wird automatisch die nächste bevorstehende angezeigt.",
        "es": "Si no se establece ningún plazo como predeterminado, se muestra automáticamente el más próximo.",
        "ko": "기본 마감일이 설정되지 않으면 가장 가까운 마감일이 자동으로 표시됩니다.",
        "pt": "Se nenhum prazo estiver definido como padrão, o mais próximo será exibido automaticamente.",
        "fr": "Si aucune échéance n\'est définie par défaut, la plus proche est affichée automatiquement.",
        "vi": "Nếu không có hạn chót nào được đặt làm mặc định, hạn chót sắp tới gần nhất sẽ được hiển thị tự động.",
        "zh": "如果没有设置默认截止日期，将自动显示最近的截止日期。",
        "hi": "यदि कोई समय सीमा डिफ़ॉल्ट के रूप में सेट नहीं है, तो निकटतम आगामी समय सीमा स्वचालित रूप से दिखाई जाती है।",
    },
    "Name": {
        "de": "Name",
        "es": "Nombre",
        "ko": "이름",
        "pt": "Nome",
        "fr": "Nom",
        "vi": "Tên",
        "zh": "名称",
        "hi": "नाम",
    },
    "+ Add": {
        "de": "+ Hinzufügen",
        "es": "+ Añadir",
        "ko": "+ 추가",
        "pt": "+ Adicionar",
        "fr": "+ Ajouter",
        "vi": "+ Thêm",
        "zh": "+ 添加",
        "hi": "+ जोड़ें",
    },
    "Start:": {
        "de": "Start:",
        "es": "Inicio:",
        "ko": "시작:",
        "pt": "Início:",
        "fr": "Début :",
        "vi": "Bắt đầu:",
        "zh": "开始：",
        "hi": "शुरू:",
    },
    "End:": {
        "de": "Ende:",
        "es": "Fin:",
        "ko": "종료:",
        "pt": "Fim:",
        "fr": "Fin :",
        "vi": "Kết thúc:",
        "zh": "结束：",
        "hi": "अंत:",
    },
    "Always show this deadline (uncheck = auto-select nearest upcoming)": {
        "de": "Diese Frist immer anzeigen (deaktivieren = nächste bevorstehende automatisch wählen)",
        "es": "Mostrar siempre este plazo (desmarcar = seleccionar automáticamente el más próximo)",
        "ko": "이 마감일 항상 표시 (해제 = 가장 가까운 마감일 자동 선택)",
        "pt": "Sempre mostrar este prazo (desmarcar = selecionar automaticamente o mais próximo)",
        "fr": "Toujours afficher cette échéance (décocher = sélection automatique de la plus proche)",
        "vi": "Luôn hiển thị hạn chót này (bỏ chọn = tự động chọn hạn chót sắp tới gần nhất)",
        "zh": "始终显示此截止日期（取消勾选 = 自动选择最近的截止日期）",
        "hi": "इस समय सीमा को हमेशा दिखाएं (अनचेक = निकटतम आगामी स्वचालित रूप से चुनें)",
    },
    # ================================================================= #
    # configuration.py – DeadlineViewDialog
    # ================================================================= #
    "Your Deadlines": {
        "de": "Deine Fristen",
        "es": "Tus plazos",
        "ko": "나의 마감일",
        "pt": "Seus prazos",
        "fr": "Vos échéances",
        "vi": "Hạn chót của bạn",
        "zh": "你的截止日期",
        "hi": "आपकी समय सीमाएं",
    },
    "No deadlines configured yet.\nUse \'Configure Deadlines\' to add one.": {
        "de": "Noch keine Fristen konfiguriert.\nVerwende \'Fristen konfigurieren\', um eine hinzuzufügen.",
        "es": "Aún no hay plazos configurados.\nUsa \'Configurar plazos\' para añadir uno.",
        "ko": "아직 마감일이 설정되지 않았습니다.\n\'마감일 설정\'을 사용하여 추가하세요.",
        "pt": "Nenhum prazo configurado ainda.\nUse \'Configurar prazos\' para adicionar um.",
        "fr": "Aucune échéance configurée.\nUtilisez \'Configurer les échéances\' pour en ajouter une.",
        "vi": "Chưa có hạn chót nào được cấu hình.\nDùng \'Cấu hình hạn chót\' để thêm.",
        "zh": "尚未配置截止日期。\n使用\'配置截止日期\'添加一个。",
        "hi": "अभी तक कोई समय सीमा कॉन्फ़िगर नहीं की गई।\n\'समय सीमाएं कॉन्फ़िगर करें\' का उपयोग करके एक जोड़ें।",
    },
    "Close": {
        "de": "Schließen",
        "es": "Cerrar",
        "ko": "닫기",
        "pt": "Fechar",
        "fr": "Fermer",
        "vi": "Đóng",
        "zh": "关闭",
        "hi": "बंद करें",
    },

    # ================================================================= #
    # background_music.py
    # ================================================================= #
    "Import Track": {
        "de": "Track importieren",
        "es": "Importar pista",
        "ko": "트랙 가져오기",
        "pt": "Importar faixa",
        "fr": "Importer une piste",
        "vi": "Nhập bản nhạc",
        "zh": "导入音轨",
        "hi": "ट्रैक आयात करें",
    },
    "Title:": {
        "de": "Titel:",
        "es": "Título:",
        "ko": "제목:",
        "pt": "Título:",
        "fr": "Titre :",
        "vi": "Tiêu đề:",
        "zh": "标题：",
        "hi": "शीर्षक:",
    },
    "Track name\u2026": {
        "de": "Trackname\u2026",
        "es": "Nombre de la pista\u2026",
        "ko": "트랙 이름\u2026",
        "pt": "Nome da faixa\u2026",
        "fr": "Nom de la piste\u2026",
        "vi": "Tên bản nhạc\u2026",
        "zh": "音轨名称\u2026",
        "hi": "ट्रैक नाम\u2026",
    },
    "File:": {
        "de": "Datei:",
        "es": "Archivo:",
        "ko": "파일:",
        "pt": "Arquivo:",
        "fr": "Fichier :",
        "vi": "Tệp:",
        "zh": "文件：",
        "hi": "फ़ाइल:",
    },
    "No file selected": {
        "de": "Keine Datei ausgewählt",
        "es": "Ningún archivo seleccionado",
        "ko": "선택된 파일 없음",
        "pt": "Nenhum arquivo selecionado",
        "fr": "Aucun fichier sélectionné",
        "vi": "Chưa chọn tệp",
        "zh": "未选择文件",
        "hi": "कोई फ़ाइल नहीं चुनी",
    },
    "Browse\u2026": {
        "de": "Durchsuchen\u2026",
        "es": "Explorar\u2026",
        "ko": "찾아보기\u2026",
        "pt": "Procurar\u2026",
        "fr": "Parcourir\u2026",
        "vi": "Duyệt\u2026",
        "zh": "浏览\u2026",
        "hi": "ब्राउज़ करें\u2026",
    },
    "Import": {
        "de": "Importieren",
        "es": "Importar",
        "ko": "가져오기",
        "pt": "Importar",
        "fr": "Importer",
        "vi": "Nhập",
        "zh": "导入",
        "hi": "आयात करें",
    },

    # ================================================================= #
    # changelog_manager.py
    # ================================================================= #

    # ================================================================= #
    # mindmap_sidebar.py
    # ================================================================= #
    "Error: QtWebEngine not available.": {
        "de": "Fehler: QtWebEngine nicht verfügbar.",
        "es": "Error: QtWebEngine no disponible.",
        "ko": "오류: QtWebEngine을 사용할 수 없습니다.",
        "pt": "Erro: QtWebEngine não disponível.",
        "fr": "Erreur : QtWebEngine non disponible.",
        "vi": "Lỗi: QtWebEngine không khả dụng.",
        "zh": "错误：QtWebEngine 不可用。",
        "hi": "त्रुटि: QtWebEngine उपलब्ध नहीं है।",
    },

    # ================================================================= #
    # notebook_sidebar.py
    # ================================================================= #

    # ================================================================= #
    # onboarding_dialog.py
    # ================================================================= #
    "Smart Study": {
        "de": "Smart Study",
        "es": "Smart Study",
        "ko": "Smart Study",
        "pt": "Smart Study",
        "fr": "Smart Study",
        "vi": "Smart Study",
        "zh": "Smart Study",
        "hi": "Smart Study",
    },

    # ================================================================= #
    # version_check_dialog.py
    # ================================================================= #

    # ================================================================= #
    # web_notebook/index.html  (Notebook tool UI strings)
    # ================================================================= #
    "Delete": {
        "de": "Löschen",
        "es": "Eliminar",
        "ko": "삭제",
        "pt": "Excluir",
        "fr": "Supprimer",
        "vi": "Xóa",
        "zh": "删除",
        "hi": "हटाएं",
    },
    "List": {
        "de": "Liste",
        "es": "Lista",
        "ko": "목록",
        "pt": "Lista",
        "fr": "Liste",
        "vi": "Danh sách",
        "zh": "列表",
        "hi": "सूची",
    },
    "Code": {
        "de": "Code",
        "es": "Código",
        "ko": "코드",
        "pt": "Código",
        "fr": "Code",
        "vi": "Mã",
        "zh": "代码",
        "hi": "कोड",
    },

    # ================================================================= #
    # web_notebook/todo.html  (Todo tool UI strings)
    # ================================================================= #
    "Open": {
        "de": "Offen",
        "es": "Pendientes",
        "ko": "미완료",
        "pt": "Abertos",
        "fr": "En cours",
        "vi": "Chưa xong",
        "zh": "未完成",
        "hi": "खुले",
    },

    # ================================================================= #
    # web_notebook/pdf_viewer.html  (PDF tool UI strings)
    # ================================================================= #
    "Back": {
        "de": "Zurück",
        "es": "Atrás",
        "ko": "뒤로",
        "pt": "Voltar",
        "fr": "Retour",
        "vi": "Quay lại",
        "zh": "返回",
        "hi": "वापस",
    },
    "Front": {
        "de": "Vorderseite",
        "es": "Anverso",
        "ko": "앞면",
        "pt": "Frente",
        "fr": "Recto",
        "vi": "Mặt trước",
        "zh": "正面",
        "hi": "सामने",
    },
    "Source": {
        "de": "Quelle",
        "es": "Fuente",
        "ko": "출처",
        "pt": "Fonte",
        "fr": "Source",
        "vi": "Nguồn",
        "zh": "来源",
        "hi": "स्रोत",
    },
    "Pages": {
        "de": "Seiten",
        "es": "Páginas",
        "ko": "페이지",
        "pt": "Páginas",
        "fr": "Pages",
        "vi": "Trang",
        "zh": "页",
        "hi": "पृष्ठ",
    },

    # ================================================================= #
    # web_notebook/pdf_viewer.html – Relink & tooltip strings
    # ================================================================= #
    "Open page": {
        "de": "Seite öffnen",
        "es": "Abrir página",
        "ko": "페이지 열기",
        "pt": "Abrir página",
        "fr": "Ouvrir la page",
        "vi": "Mở trang",
        "zh": "打开页面",
        "hi": "पेज खोलें",
    },
    "Remove": {
        "de": "Entfernen",
        "es": "Eliminar",
        "ko": "제거",
        "pt": "Remover",
        "fr": "Supprimer",
        "vi": "Xóa",
        "zh": "移除",
        "hi": "हटाएं",
    },

    # ================================================================= #
    # ai_assistant.py – loading / error page strings
    # ================================================================= #
    "Retry": {
        "de": "Erneut versuchen",
        "es": "Reintentar",
        "ko": "다시 시도",
        "pt": "Tentar novamente",
        "fr": "Réessayer",
        "vi": "Thử lại",
        "zh": "重试",
        "hi": "पुनः प्रयास करें",
    },

    # ================================================================= #
    # background_music.py – Linux audio backend error
    # ================================================================= #

    # ================================================================= #
    # mindmap_sidebar.py / index.html – Mindmap UI strings
    # ================================================================= #
    "New": {
        "de": "Neu", "es": "Nuevo", "ko": "새로 만들기", "pt": "Novo",
        "fr": "Nouveau", "vi": "Mới", "zh": "新建", "hi": "नया",
    },
    "Menu": {
        "de": "Menü", "es": "Menú", "ko": "메뉴", "pt": "Menu",
        "fr": "Menu", "vi": "Menu", "zh": "菜单", "hi": "मेनू",
    },
    "Export": {
        "de": "Exportieren", "es": "Exportar", "ko": "내보내기", "pt": "Exportar",
        "fr": "Exporter", "vi": "Xuất", "zh": "导出", "hi": "निर्यात करें",
    },
    "Fullscreen": {
        "de": "Vollbild", "es": "Pantalla completa", "ko": "전체 화면", "pt": "Tela cheia",
        "fr": "Plein écran", "vi": "Toàn màn hình", "zh": "全屏", "hi": "पूर्ण स्क्रीन",
    },
    "Random": {
        "de": "Zufällig", "es": "Aleatorio", "ko": "무작위", "pt": "Aleatório",
        "fr": "Aléatoire", "vi": "Ngẫu nhiên", "zh": "随机", "hi": "यादृच्छिक",
    },

    # ── Measurable daily challenges (gamification) ─────────────────────────
    "Review {} cards today.": {
        "de": "Wiederhole heute {} Karten.", "es": "Repasa {} tarjetas hoy.", "ko": "오늘 카드 {}장을 복습하세요.", "pt": "Revise {} cartões hoje.",
        "fr": "Révisez {} cartes aujourd'hui.", "vi": "Ôn {} thẻ hôm nay.", "zh": "今天复习 {} 张卡片。", "hi": "आज {} कार्ड दोहराएं।",
    },
    "Learn {} new cards today.": {
        "de": "Lerne heute {} neue Karten.", "es": "Aprende {} tarjetas nuevas hoy.", "ko": "오늘 새 카드 {}장을 학습하세요.", "pt": "Aprenda {} cartões novos hoje.",
        "fr": "Apprenez {} nouvelles cartes aujourd'hui.", "vi": "Học {} thẻ mới hôm nay.", "zh": "今天学习 {} 张新卡片。", "hi": "आज {} नए कार्ड सीखें।",
    },
    "Study for {} minutes today.": {
        "de": "Lerne heute {} Minuten.", "es": "Estudia {} minutos hoy.", "ko": "오늘 {}분 동안 공부하세요.", "pt": "Estude por {} minutos hoje.",
        "fr": "Étudiez {} minutes aujourd'hui.", "vi": "Học {} phút hôm nay.", "zh": "今天学习 {} 分钟。", "hi": "आज {} मिनट पढ़ाई करें।",
    },
    "Review cards from {} different decks today.": {
        "de": "Wiederhole heute Karten aus {} verschiedenen Stapeln.", "es": "Repasa hoy tarjetas de {} mazos diferentes.",
        "ko": "오늘 서로 다른 덱 {}개의 카드를 복습하세요.", "pt": "Revise hoje cartões de {} baralhos diferentes.",
        "fr": "Révisez aujourd'hui des cartes de {} paquets différents.", "vi": "Hôm nay ôn thẻ từ {} bộ thẻ khác nhau.",
        "zh": "今天复习来自 {} 个不同牌组的卡片。", "hi": "आज {} अलग-अलग डेक के कार्ड दोहराएं।",
    },
    "Challenge not completed yet ({}/{}).": {
        "de": "Challenge noch nicht geschafft ({}/{}).", "es": "Desafío aún no completado ({}/{}).", "ko": "아직 챌린지를 완료하지 못했습니다 ({}/{}).",
        "pt": "Desafio ainda não concluído ({}/{}).", "fr": "Défi pas encore accompli ({}/{}).", "vi": "Thử thách chưa hoàn thành ({}/{}).",
        "zh": "挑战尚未完成（{}/{}）。", "hi": "चुनौती अभी पूरी नहीं हुई ({}/{})।",
    },
    "Claim +{} XP": {
        "de": "+{} XP abholen", "es": "Reclamar +{} XP", "ko": "+{} XP 받기", "pt": "Resgatar +{} XP",
        "fr": "Récupérer +{} XP", "vi": "Nhận +{} XP", "zh": "领取 +{} XP", "hi": "+{} XP प्राप्त करें",
    },

    # ── Focus Music player ────────────────────────────────────────────────
    "Previous track": {
        "de": "Vorheriger Titel", "es": "Pista anterior", "ko": "이전 트랙", "pt": "Faixa anterior",
        "fr": "Piste précédente", "vi": "Bản trước", "zh": "上一曲", "hi": "पिछला ट्रैक",
    },
    "Next track": {
        "de": "Nächster Titel", "es": "Pista siguiente", "ko": "다음 트랙", "pt": "Próxima faixa",
        "fr": "Piste suivante", "vi": "Bản tiếp theo", "zh": "下一曲", "hi": "अगला ट्रैक",
    },

    # ── Pomodoro (single-page dialog) ─────────────────────────────────────
    "sessions": {
        "de": "Einheiten", "es": "sesiones", "ko": "세션", "pt": "sessões",
        "fr": "sessions", "vi": "phiên", "zh": "次", "hi": "सत्र",
    },

    # ── Ollama setup assistant (AI Assistant) ─────────────────────────────
    "AI Assistant is not available (missing Qt/Anki components).": {
        "de": "KI-Assistent ist nicht verfügbar (fehlende Qt-/Anki-Komponenten).", "es": "El asistente de IA no está disponible (faltan componentes de Qt/Anki).",
        "ko": "AI 어시스턴트를 사용할 수 없습니다 (Qt/Anki 구성 요소 없음).", "pt": "O assistente de IA não está disponível (componentes Qt/Anki ausentes).",
        "fr": "L'assistant IA n'est pas disponible (composants Qt/Anki manquants).", "vi": "Trợ lý AI không khả dụng (thiếu thành phần Qt/Anki).",
        "zh": "AI 助手不可用（缺少 Qt/Anki 组件）。", "hi": "AI असिस्टेंट उपलब्ध नहीं है (Qt/Anki घटक अनुपलब्ध)।",
    },
    "AI Assistant setup error: {}": {
        "de": "Fehler beim Einrichten des KI-Assistenten: {}", "es": "Error al configurar el asistente de IA: {}",
        "ko": "AI 어시스턴트 설정 오류: {}", "pt": "Erro na configuração do assistente de IA: {}",
        "fr": "Erreur de configuration de l'assistant IA : {}", "vi": "Lỗi thiết lập trợ lý AI: {}",
        "zh": "AI 助手设置错误：{}", "hi": "AI असिस्टेंट सेटअप त्रुटि: {}",
    },
    "Local": {
        "de": "Lokal", "es": "Local", "ko": "로컬", "pt": "Local",
        "fr": "Local", "vi": "Cục bộ", "zh": "本地", "hi": "लोकल",
    },
    "Custom URL…": {
        "de": "Eigene URL…", "es": "URL personalizada…", "ko": "사용자 지정 URL…", "pt": "URL personalizada…",
        "fr": "URL personnalisée…", "vi": "URL tùy chỉnh…", "zh": "自定义 URL…", "hi": "कस्टम URL…",
    },
    "Please paste a valid SoundCloud URL.": {
        "de": "Bitte füge eine gültige SoundCloud-URL ein.", "es": "Pega una URL válida de SoundCloud.",
        "ko": "유효한 SoundCloud URL을 붙여넣으세요.", "pt": "Cole uma URL válida do SoundCloud.",
        "fr": "Veuillez coller une URL SoundCloud valide.", "vi": "Vui lòng dán URL SoundCloud hợp lệ.",
        "zh": "请粘贴有效的 SoundCloud 链接。", "hi": "कृपया एक मान्य SoundCloud URL पेस्ट करें।",
    },
    "You can save up to {count} custom SoundCloud URLs.": {
        "de": "Du kannst bis zu {count} eigene SoundCloud-URLs speichern.", "es": "Puedes guardar hasta {count} URL personalizadas de SoundCloud.",
        "ko": "사용자 지정 SoundCloud URL은 최대 {count}개까지 저장할 수 있습니다.", "pt": "Você pode salvar até {count} URLs personalizadas do SoundCloud.",
        "fr": "Vous pouvez enregistrer jusqu’à {count} URL SoundCloud personnalisées.", "vi": "Bạn có thể lưu tối đa {count} URL SoundCloud tùy chỉnh.",
        "zh": "最多可以保存 {count} 个自定义 SoundCloud 链接。", "hi": "आप अधिकतम {count} कस्टम SoundCloud URL सहेज सकते हैं।",
    },
    "SoundCloud could not load this URL.": {
        "de": "SoundCloud konnte diese URL nicht laden.", "es": "SoundCloud no pudo cargar esta URL.",
        "ko": "SoundCloud에서 이 URL을 불러올 수 없습니다.", "pt": "O SoundCloud não conseguiu carregar esta URL.",
        "fr": "SoundCloud n’a pas pu charger cette URL.", "vi": "SoundCloud không thể tải URL này.",
        "zh": "SoundCloud 无法加载此链接。", "hi": "SoundCloud इस URL को लोड नहीं कर सका।",
    },
    "Requires QtWebEngine (not available in this Anki build).": {
        "de": "Benötigt QtWebEngine (in dieser Anki-Version nicht verfügbar).", "es": "Requiere QtWebEngine (no disponible en esta versión de Anki).",
        "ko": "QtWebEngine이 필요합니다 (이 Anki 빌드에서는 사용 불가).", "pt": "Requer QtWebEngine (não disponível nesta versão do Anki).",
        "fr": "Nécessite QtWebEngine (indisponible dans cette version d'Anki).", "vi": "Cần QtWebEngine (không có trong bản Anki này).",
        "zh": "需要 QtWebEngine（此 Anki 版本不可用）。", "hi": "QtWebEngine आवश्यक है (इस Anki बिल्ड में उपलब्ध नहीं)।",
    },
    "SoundCloud player file is missing.": {
        "de": "SoundCloud-Player-Datei fehlt.", "es": "Falta el archivo del reproductor de SoundCloud.",
        "ko": "SoundCloud 플레이어 파일이 없습니다.", "pt": "O arquivo do player do SoundCloud está ausente.",
        "fr": "Le fichier du lecteur SoundCloud est manquant.", "vi": "Thiếu tệp trình phát SoundCloud.",
        "zh": "缺少 SoundCloud 播放器文件。", "hi": "SoundCloud प्लेयर फ़ाइल गायब है।",
    },

    # ── Misc previously untranslated UI strings ────────────────────────────
    "My Deadline": {
        "de": "Meine Deadline", "es": "Mi fecha límite", "ko": "내 마감일", "pt": "Meu prazo",
        "fr": "Mon échéance", "vi": "Hạn chót của tôi", "zh": "我的截止日期", "hi": "मेरी समय-सीमा",
    },
    "Learn": {
        "de": "Lernen", "es": "Aprender", "ko": "학습", "pt": "Aprender",
        "fr": "Apprendre", "vi": "Học", "zh": "学习", "hi": "सीखें",
    },
    "Review": {
        "de": "Wiederholen", "es": "Repasar", "ko": "복습", "pt": "Revisar",
        "fr": "Réviser", "vi": "Ôn tập", "zh": "复习", "hi": "दोहराएं",
    },
    "Back to Anki": {
        "de": "Zurück zu Anki", "es": "Volver a Anki", "ko": "Anki로 돌아가기", "pt": "Voltar ao Anki",
        "fr": "Retour à Anki", "vi": "Quay lại Anki", "zh": "返回 Anki", "hi": "Anki पर वापस",
    },
    "Start": {
        "de": "Start", "es": "Iniciar", "ko": "시작", "pt": "Iniciar",
        "fr": "Démarrer", "vi": "Bắt đầu", "zh": "开始", "hi": "शुरू करें",
    },
    "PDF Files (*.pdf)": {
        "de": "PDF-Dateien (*.pdf)", "es": "Archivos PDF (*.pdf)", "ko": "PDF 파일 (*.pdf)", "pt": "Arquivos PDF (*.pdf)",
        "fr": "Fichiers PDF (*.pdf)", "vi": "Tệp PDF (*.pdf)", "zh": "PDF 文件 (*.pdf)", "hi": "PDF फ़ाइलें (*.pdf)",
    },
    "Open in main window": {
        "de": "Im Hauptfenster öffnen", "es": "Abrir en la ventana principal", "ko": "메인 창에서 열기", "pt": "Abrir na janela principal",
        "fr": "Ouvrir dans la fenêtre principale", "vi": "Mở trong cửa sổ chính", "zh": "在主窗口中打开", "hi": "मुख्य विंडो में खोलें",
    },
    "Web": {
        "de": "Web", "es": "Web", "ko": "웹", "pt": "Web",
        "fr": "Web", "vi": "Web", "zh": "网页", "hi": "वेब",
    },

    # ── Native settings dialog (fallback without WebEngine) ────────────────
    "Appearance": {
        "de": "Erscheinungsbild", "es": "Apariencia", "ko": "모양", "pt": "Aparência",
        "fr": "Apparence", "vi": "Giao diện", "zh": "外观", "hi": "रूप-रंग",
    },
    "Dashboard": {
        "de": "Dashboard", "es": "Panel", "ko": "대시보드", "pt": "Painel",
        "fr": "Tableau de bord", "vi": "Bảng điều khiển", "zh": "仪表板", "hi": "डैशबोर्ड",
    },
    "Minimalist Dashboard": {
        "de": "Minimalistisches Dashboard", "es": "Panel minimalista", "ko": "미니멀 대시보드", "pt": "Painel minimalista",
        "fr": "Tableau de bord minimaliste", "vi": "Bảng điều khiển tối giản", "zh": "极简仪表板", "hi": "मिनिमल डैशबोर्ड",
    },
    "Shows level, streak, challenge, study plan, deadline and key statistics in one compact panel.": {
        "de": "Zeigt Level, Streak, Challenge, Lernplan, Deadline und die wichtigsten Statistiken in einem kompakten Panel.",
        "es": "Muestra el nivel, la racha, el reto, el plan de estudio, la fecha límite y las estadísticas clave en un panel compacto.",
        "ko": "레벨, 스트릭, 챌린지, 학습 계획, 마감일과 핵심 통계를 하나의 간결한 패널에 표시합니다.",
        "pt": "Mostra nível, sequência, desafio, plano de estudos, prazo e estatísticas principais em um painel compacto.",
        "fr": "Affiche le niveau, la série, le défi, le plan d’étude, l’échéance et les statistiques clés dans un panneau compact.",
        "vi": "Hiển thị cấp độ, chuỗi ngày, thử thách, kế hoạch học, thời hạn và thống kê chính trong một bảng gọn.",
        "zh": "在一个紧凑面板中显示等级、连续学习、挑战、学习计划、截止日期和关键统计。",
        "hi": "स्तर, स्ट्रीक, चुनौती, अध्ययन योजना, समयसीमा और मुख्य आँकड़े एक कॉम्पैक्ट पैनल में दिखाता है।",
    },
    "Language": {
        "de": "Sprache", "es": "Idioma", "ko": "언어", "pt": "Idioma",
        "fr": "Langue", "vi": "Ngôn ngữ", "zh": "语言", "hi": "भाषा",
    },
    "Color Theme": {
        "de": "Farbschema", "es": "Tema de color", "ko": "색상 테마", "pt": "Tema de cores",
        "fr": "Thème de couleur", "vi": "Chủ đề màu", "zh": "颜色主题", "hi": "रंग थीम",
    },
    "Background Style": {
        "de": "Hintergrund-Stil", "es": "Estilo de fondo", "ko": "배경 스타일", "pt": "Estilo de fundo",
        "fr": "Style d'arrière-plan", "vi": "Kiểu nền", "zh": "背景样式", "hi": "पृष्ठभूमि शैली",
    },
    "Daily Fact Topic": {
        "de": "Thema des täglichen Fakts", "es": "Tema del dato diario", "ko": "오늘의 상식 주제", "pt": "Tema do fato diário",
        "fr": "Thème du fait du jour", "vi": "Chủ đề sự thật hằng ngày", "zh": "每日知识主题", "hi": "दैनिक तथ्य विषय",
    },
    "Study Plan Widget": {
        "de": "Lernplan-Widget", "es": "Widget del plan de estudio",
        "ko": "학습 계획 위젯", "pt": "Widget do plano de estudos",
        "fr": "Widget du plan d’étude", "vi": "Widget kế hoạch học tập",
        "zh": "学习计划小部件", "hi": "अध्ययन योजना विजेट",
    },
    "Your daily study plan.": {
        "de": "Dein täglicher Lernplan.", "es": "Tu plan de estudio diario.",
        "ko": "오늘의 학습 계획입니다.", "pt": "Seu plano de estudos diário.",
        "fr": "Votre plan d’étude quotidien.", "vi": "Kế hoạch học tập hằng ngày của bạn.",
        "zh": "你的每日学习计划。", "hi": "आपकी दैनिक अध्ययन योजना।",
    },
    "Daily Fact Widget": {
        "de": "Widget für den täglichen Fakt", "es": "Widget del dato diario",
        "ko": "오늘의 상식 위젯", "pt": "Widget do fato diário",
        "fr": "Widget du fait du jour", "vi": "Widget sự thật hằng ngày",
        "zh": "每日知识小部件", "hi": "दैनिक तथ्य विजेट",
    },
    "A new fact on your Anki home screen each day.": {
        "de": "Jeden Tag ein neuer Fakt auf deiner Anki-Startseite.",
        "es": "Cada día, un dato nuevo en la pantalla de inicio de Anki.",
        "ko": "매일 Anki 홈 화면에 새로운 상식이 표시됩니다.",
        "pt": "Um novo fato por dia na tela inicial do Anki.",
        "fr": "Chaque jour, un nouveau fait sur l’écran d’accueil d’Anki.",
        "vi": "Mỗi ngày một sự thật mới trên màn hình chính Anki.",
        "zh": "每天在 Anki 主屏幕上显示一条新知识。",
        "hi": "हर दिन Anki होम स्क्रीन पर एक नया तथ्य।",
    },
    "Gamification Widgets": {
        "de": "Gamification-Widgets", "es": "Widgets de gamificación", "ko": "게이미피케이션 위젯", "pt": "Widgets de gamificação",
        "fr": "Widgets de gamification", "vi": "Widget trò chơi hóa", "zh": "游戏化小部件", "hi": "गेमिफ़िकेशन विजेट",
    },
    "Sidebar Visibility": {
        "de": "Sichtbarkeit der Seitenleiste", "es": "Visibilidad de la barra lateral", "ko": "사이드바 표시", "pt": "Visibilidade da barra lateral",
        "fr": "Visibilité de la barre latérale", "vi": "Hiển thị thanh bên", "zh": "侧边栏可见性", "hi": "साइडबार दृश्यता",
    },
    "Statistics Time Range": {
        "de": "Zeitraum der Statistiken", "es": "Rango de tiempo de estadísticas", "ko": "통계 기간", "pt": "Período das estatísticas",
        "fr": "Période des statistiques", "vi": "Khoảng thời gian thống kê", "zh": "统计时间范围", "hi": "आंकड़ों की समय-सीमा",
    },
    "Language, the period of the Memory chart and when the left bar is shown.": {
        "de": "Sprache, Zeitraum des Gedächtnis-Diagramms und wann die linke Leiste angezeigt wird.",
        "es": "Idioma, el período del gráfico de memoria y cuándo se muestra la barra izquierda.",
        "ko": "언어, 기억 차트의 기간, 왼쪽 막대를 표시할 시점.",
        "pt": "Idioma, o período do gráfico de memória e quando a barra esquerda é exibida.",
        "fr": "Langue, période du graphique de mémoire et affichage de la barre de gauche.",
        "vi": "Ngôn ngữ, khoảng thời gian của biểu đồ ghi nhớ và khi nào hiển thị thanh bên trái.",
        "zh": "语言、记忆图表的时间范围以及何时显示左侧栏。",
        "hi": "भाषा, मेमोरी चार्ट की अवधि और बायाँ बार कब दिखे।",
    },
    "Interface language. \"Auto\" follows your Anki language.": {
        "de": "Sprache der Oberfläche. \"Auto\" folgt deiner Anki-Sprache.",
        "es": "Idioma de la interfaz. \"Auto\" sigue el idioma de Anki.",
        "ko": "인터페이스 언어. \"Auto\"는 Anki 언어를 따릅니다.",
        "pt": "Idioma da interface. \"Auto\" segue o idioma do Anki.",
        "fr": "Langue de l'interface. \"Auto\" suit la langue d'Anki.",
        "vi": "Ngôn ngữ giao diện. \"Auto\" theo ngôn ngữ Anki của bạn.",
        "zh": "界面语言。\"Auto\"跟随您的 Anki 语言。",
        "hi": "इंटरफ़ेस भाषा। \"Auto\" आपकी Anki भाषा का अनुसरण करता है।",
    },
    "Subject the daily fact on the home screen is drawn from.": {
        "de": "Fachgebiet, aus dem der tägliche Fakt auf dem Startbildschirm stammt.",
        "es": "Tema del que se extrae el dato diario de la pantalla de inicio.",
        "ko": "홈 화면의 오늘의 상식이 나오는 분야.",
        "pt": "Assunto de onde vem o fato diário da tela inicial.",
        "fr": "Sujet dont provient le fait du jour de l'écran d'accueil.",
        "vi": "Chủ đề mà sự thật hằng ngày trên màn hình chính được lấy từ đó.",
        "zh": "主屏幕每日知识的来源主题。",
        "hi": "जिस विषय से होम स्क्रीन का दैनिक तथ्य लिया जाता है।",
    },
    "Period of the Memory chart (also under Home).": {
        "de": "Zeitraum des Gedächtnis-Diagramms (auch unter Start).",
        "es": "Período del gráfico de memoria (también en Inicio).",
        "ko": "기억 차트의 기간 (홈에도 있음).",
        "pt": "Período do gráfico de memória (também em Início).",
        "fr": "Période du graphique de mémoire (aussi sous Accueil).",
        "vi": "Khoảng thời gian của biểu đồ ghi nhớ (cũng có ở Trang chủ).",
        "zh": "记忆图表的时间范围（主页中也可设置）。",
        "hi": "मेमोरी चार्ट की अवधि (होम में भी)।",
    },
    "Show the left bar with the tabs always, or hide it while you review.": {
        "de": "Linke Leiste mit den Reitern immer anzeigen oder beim Wiederholen ausblenden.",
        "es": "Mostrar siempre la barra izquierda con las pestañas u ocultarla mientras repasas.",
        "ko": "탭이 있는 왼쪽 막대를 항상 표시하거나 복습 중에는 숨깁니다.",
        "pt": "Mostrar sempre a barra esquerda com as abas ou ocultá-la durante a revisão.",
        "fr": "Toujours afficher la barre de gauche avec les onglets, ou la masquer pendant la révision.",
        "vi": "Luôn hiển thị thanh bên trái có các thẻ, hoặc ẩn khi bạn ôn tập.",
        "zh": "始终显示带标签的左侧栏，或在复习时隐藏。",
        "hi": "टैब वाला बायाँ बार हमेशा दिखाएं, या समीक्षा के दौरान छिपाएं।",
    },
    "Choose the accent colour used across Smart Study and the background style.": {
        "de": "Wähle die Akzentfarbe für Smart Study und den Hintergrund-Stil.",
        "es": "Elige el color de acento de Smart Study y el estilo de fondo.",
        "ko": "Smart Study 전체에 사용할 강조 색상과 배경 스타일을 선택하세요.",
        "pt": "Escolha a cor de destaque do Smart Study e o estilo de fundo.",
        "fr": "Choisissez la couleur d'accent de Smart Study et le style d'arrière-plan.",
        "vi": "Chọn màu nhấn dùng trong Smart Study và kiểu nền.",
        "zh": "选择 Smart Study 使用的强调色和背景样式。",
        "hi": "Smart Study में उपयोग होने वाला एक्सेंट रंग और पृष्ठभूमि शैली चुनें।",
    },
    "Accent colour for buttons, highlights and widgets.": {
        "de": "Akzentfarbe für Buttons, Hervorhebungen und Widgets.",
        "es": "Color de acento para botones, resaltados y widgets.",
        "ko": "버튼, 강조 표시 및 위젯의 강조 색상.",
        "pt": "Cor de destaque para botões, realces e widgets.",
        "fr": "Couleur d'accent pour les boutons, surlignages et widgets.",
        "vi": "Màu nhấn cho nút, phần tô sáng và widget.",
        "zh": "按钮、高亮和小部件的强调色。",
        "hi": "बटन, हाइलाइट और विजेट के लिए एक्सेंट रंग।",
    },
    "Overall background of the add-on screens.": {
        "de": "Gesamter Hintergrund der Add-on-Bildschirme.",
        "es": "Fondo general de las pantallas del complemento.",
        "ko": "애드온 화면의 전체 배경.",
        "pt": "Fundo geral das telas do complemento.",
        "fr": "Arrière-plan général des écrans du module.",
        "vi": "Nền tổng thể của các màn hình tiện ích.",
        "zh": "插件界面的整体背景。",
        "hi": "ऐड-ऑन स्क्रीन की समग्र पृष्ठभूमि।",
    },
    "Widgets shown on the Anki home screen (the deck list).": {
        "de": "Widgets auf dem Anki-Startbildschirm (der Stapelliste).",
        "es": "Widgets mostrados en la pantalla de inicio de Anki (la lista de mazos).",
        "ko": "Anki 홈 화면(덱 목록)에 표시되는 위젯.",
        "pt": "Widgets exibidos na tela inicial do Anki (a lista de baralhos).",
        "fr": "Widgets affichés sur l'écran d'accueil d'Anki (la liste des paquets).",
        "vi": "Widget hiển thị trên màn hình chính Anki (danh sách bộ thẻ).",
        "zh": "显示在 Anki 主屏幕（牌组列表）上的小部件。",
        "hi": "Anki होम स्क्रीन (डेक सूची) पर दिखने वाले विजेट।",
    },
    "The screen shown after you click a deck, before studying.": {
        "de": "Der Bildschirm nach dem Klick auf einen Stapel, vor dem Lernen.",
        "es": "La pantalla que aparece al hacer clic en un mazo, antes de estudiar.",
        "ko": "덱을 클릭한 후 학습 전에 표시되는 화면.",
        "pt": "A tela exibida após clicar em um baralho, antes de estudar.",
        "fr": "L'écran affiché après un clic sur un paquet, avant l'étude.",
        "vi": "Màn hình hiện ra sau khi bạn nhấn vào bộ thẻ, trước khi học.",
        "zh": "点击牌组后、学习前显示的界面。",
        "hi": "डेक पर क्लिक करने के बाद, पढ़ाई से पहले दिखने वाली स्क्रीन।",
    },
    "Tools available in the launcher bar on the side of Anki.": {
        "de": "Werkzeuge in der Launcher-Leiste an der Seite von Anki.",
        "es": "Herramientas disponibles en la barra lateral de Anki.",
        "ko": "Anki 측면 런처 바에서 사용할 수 있는 도구.",
        "pt": "Ferramentas disponíveis na barra lateral do Anki.",
        "fr": "Outils disponibles dans la barre latérale d'Anki.",
        "vi": "Công cụ có trong thanh khởi chạy bên cạnh Anki.",
        "zh": "Anki 侧边启动栏中可用的工具。",
        "hi": "Anki के किनारे लॉन्चर बार में उपलब्ध उपकरण।",
    },
    "Your level, XP and daily streak.": {
        "de": "Dein Level, XP und deine tägliche Serie.", "es": "Tu nivel, XP y racha diaria.",
        "ko": "내 레벨, XP, 일일 스트릭.", "pt": "Seu nível, XP e sequência diária.",
        "fr": "Votre niveau, XP et série quotidienne.", "vi": "Cấp độ, XP và chuỗi ngày của bạn.",
        "zh": "您的等级、XP 和每日连击。", "hi": "आपका स्तर, XP और दैनिक स्ट्रीक।",
    },
    "A countdown bar towards your exam or deadline.": {
        "de": "Ein Countdown-Balken bis zu deiner Prüfung oder Deadline.", "es": "Una barra de cuenta regresiva hacia tu examen o fecha límite.",
        "ko": "시험이나 마감일까지의 카운트다운 바.", "pt": "Uma barra de contagem regressiva até sua prova ou prazo.",
        "fr": "Une barre de compte à rebours vers votre examen ou échéance.", "vi": "Thanh đếm ngược đến kỳ thi hoặc hạn chót của bạn.",
        "zh": "距离考试或截止日期的倒计时条。", "hi": "आपकी परीक्षा या समय-सीमा तक की उलटी गिनती पट्टी।",
    },
    "An extra panel with detailed review statistics.": {
        "de": "Ein zusätzliches Panel mit detaillierten Wiederholungsstatistiken.", "es": "Un panel adicional con estadísticas detalladas de repaso.",
        "ko": "자세한 복습 통계가 있는 추가 패널.", "pt": "Um painel extra com estatísticas detalhadas de revisão.",
        "fr": "Un panneau supplémentaire avec des statistiques de révision détaillées.", "vi": "Bảng bổ sung với thống kê ôn tập chi tiết.",
        "zh": "包含详细复习统计的额外面板。", "hi": "विस्तृत रिव्यू आंकड़ों वाला अतिरिक्त पैनल।",
    },
    "Replaces the standard overview with a modern dashboard showing retention, hard cards and more.": {
        "de": "Ersetzt die Standard-Übersicht durch ein modernes Dashboard mit Retention, schweren Karten und mehr.",
        "es": "Reemplaza la vista estándar por un panel moderno con retención, tarjetas difíciles y más.",
        "ko": "기본 개요를 리텐션, 어려운 카드 등을 보여주는 현대적인 대시보드로 교체합니다.",
        "pt": "Substitui a visão padrão por um painel moderno com retenção, cartões difíceis e mais.",
        "fr": "Remplace l'aperçu standard par un tableau de bord moderne avec rétention, cartes difficiles et plus.",
        "vi": "Thay thế màn hình tổng quan chuẩn bằng bảng điều khiển hiện đại với tỷ lệ ghi nhớ, thẻ khó và hơn thế.",
        "zh": "用显示记忆保持率、难卡等的现代仪表板替换标准概览。",
        "hi": "मानक ओवरव्यू को रिटेंशन, कठिन कार्ड आदि दिखाने वाले आधुनिक डैशबोर्ड से बदलता है।",
    },
    "Progress, rewards and motivation panel.": {
        "de": "Panel für Fortschritt, Belohnungen und Motivation.", "es": "Panel de progreso, recompensas y motivación.",
        "ko": "진행 상황, 보상, 동기 부여 패널.", "pt": "Painel de progresso, recompensas e motivação.",
        "fr": "Panneau de progression, récompenses et motivation.", "vi": "Bảng tiến độ, phần thưởng và động lực.",
        "zh": "进度、奖励和激励面板。", "hi": "प्रगति, पुरस्कार और प्रेरणा पैनल।",
    },
    "Background music while you study.": {
        "de": "Hintergrundmusik beim Lernen.", "es": "Música de fondo mientras estudias.", "ko": "공부할 때 듣는 배경 음악.", "pt": "Música de fundo enquanto você estuda.",
        "fr": "Musique de fond pendant vos études.", "vi": "Nhạc nền khi bạn học.", "zh": "学习时的背景音乐。", "hi": "पढ़ाई के दौरान पृष्ठभूमि संगीत।",
    },
    "A focus timer with work and break intervals.": {
        "de": "Ein Fokus-Timer mit Arbeits- und Pausenintervallen.", "es": "Un temporizador de concentración con intervalos de trabajo y descanso.",
        "ko": "작업과 휴식 간격이 있는 집중 타이머.", "pt": "Um cronômetro de foco com intervalos de trabalho e pausa.",
        "fr": "Un minuteur de concentration avec intervalles de travail et de pause.", "vi": "Bộ đếm giờ tập trung với các khoảng làm việc và nghỉ.",
        "zh": "带工作和休息间隔的专注计时器。", "hi": "कार्य और विराम अंतराल वाला फोकस टाइमर।",
    },
    "ChatGPT, Claude, Gemini or NotebookLM next to your cards, with your own account.": {
        "de": "ChatGPT, Claude, Gemini oder NotebookLM neben deinen Karten, mit deinem eigenen Konto.",
        "es": "ChatGPT, Claude, Gemini o NotebookLM junto a tus tarjetas, con tu propia cuenta.",
        "ko": "카드 옆에서 ChatGPT, Claude, Gemini 또는 NotebookLM을 내 계정으로 사용합니다.",
        "pt": "ChatGPT, Claude, Gemini ou NotebookLM ao lado dos seus cartões, com a sua própria conta.",
        "fr": "ChatGPT, Claude, Gemini ou NotebookLM à côté de tes cartes, avec ton propre compte.",
        "vi": "ChatGPT, Claude, Gemini hoặc NotebookLM cạnh thẻ của bạn, bằng tài khoản của bạn.",
        "zh": "在卡片旁使用 ChatGPT、Claude、Gemini 或 NotebookLM，使用你自己的账号。",
        "hi": "आपके कार्ड के पास ChatGPT, Claude, Gemini या NotebookLM, आपके अपने खाते से।",
    },
    "Open websites in a panel without leaving Anki.": {
        "de": "Webseiten in einem Panel öffnen, ohne Anki zu verlassen.", "es": "Abre sitios web en un panel sin salir de Anki.",
        "ko": "Anki를 떠나지 않고 패널에서 웹사이트 열기.", "pt": "Abra sites em um painel sem sair do Anki.",
        "fr": "Ouvrez des sites web dans un panneau sans quitter Anki.", "vi": "Mở trang web trong bảng mà không rời Anki.",
        "zh": "无需离开 Anki 即可在面板中打开网站。", "hi": "Anki छोड़े बिना पैनल में वेबसाइटें खोलें।",
    },
    "Ocean": {
        "de": "Ozean", "es": "Océano", "ko": "오션", "pt": "Oceano",
        "fr": "Océan", "vi": "Đại dương", "zh": "海洋", "hi": "महासागर",
    },
    "Orchid": {
        "de": "Orchidee", "es": "Orquídea", "ko": "오키드", "pt": "Orquídea",
        "fr": "Orchidée", "vi": "Phong lan", "zh": "兰花", "hi": "ऑर्किड",
    },
    "Forest": {
        "de": "Wald", "es": "Bosque", "ko": "포레스트", "pt": "Floresta",
        "fr": "Forêt", "vi": "Rừng", "zh": "森林", "hi": "वन",
    },
    "Deluge": {
        "de": "Deluge", "es": "Diluvio", "ko": "델루지", "pt": "Dilúvio",
        "fr": "Déluge", "vi": "Deluge", "zh": "深紫", "hi": "डेल्यूज",
    },
    "Horizon": {
        "de": "Horizont", "es": "Horizonte", "ko": "허라이즌", "pt": "Horizonte",
        "fr": "Horizon", "vi": "Chân trời", "zh": "地平线", "hi": "क्षितिज",
    },
    "Dusty": {
        "de": "Dusty", "es": "Dusty", "ko": "더스티", "pt": "Dusty",
        "fr": "Dusty", "vi": "Dusty", "zh": "灰青", "hi": "डस्टी",
    },
    "Custom Color…": {
        "de": "Eigene Farbe…", "es": "Color personalizado…", "ko": "사용자 지정 색상…", "pt": "Cor personalizada…",
        "fr": "Couleur personnalisée…", "vi": "Màu tùy chỉnh…", "zh": "自定义颜色…", "hi": "कस्टम रंग…",
    },
    "Cards": {
        "de": "Karten", "es": "Tarjetas", "ko": "카드", "pt": "Cartões",
        "fr": "Cartes", "vi": "Thẻ", "zh": "卡片", "hi": "कार्ड",
    },
    "Edit": {
        "de": "Bearbeiten", "es": "Editar", "ko": "편집", "pt": "Editar",
        "fr": "Modifier", "vi": "Chỉnh sửa", "zh": "编辑", "hi": "संपादित करें",
    },

    # ── Sidebar keyboard shortcuts ─────────────────────────────────────────
    "Keyboard Shortcut": {
        "de": "Tastenkürzel", "es": "Atajo de teclado", "ko": "키보드 단축키", "pt": "Atalho de teclado",
        "fr": "Raccourci clavier", "vi": "Phím tắt", "zh": "键盘快捷键", "hi": "कीबोर्ड शॉर्टकट",
    },
    "Press the desired key combination.": {
        "de": "Drücke die gewünschte Tastenkombination.", "es": "Pulsa la combinación de teclas deseada.", "ko": "원하는 키 조합을 누르세요.", "pt": "Pressione a combinação de teclas desejada.",
        "fr": "Appuyez sur la combinaison de touches souhaitée.", "vi": "Nhấn tổ hợp phím mong muốn.", "zh": "请按下所需的组合键。", "hi": "अपना इच्छित कुंजी संयोजन दबाएँ।",
    },
    "Use Ctrl, Alt, Command or a function key.": {
        "de": "Verwende Strg, Alt, Command oder eine Funktionstaste.", "es": "Usa Ctrl, Alt, Comando o una tecla de función.", "ko": "Ctrl, Alt, Command 또는 기능 키를 사용하세요.", "pt": "Use Ctrl, Alt, Command ou uma tecla de função.",
        "fr": "Utilisez Ctrl, Alt, Commande ou une touche de fonction.", "vi": "Sử dụng Ctrl, Alt, Command hoặc một phím chức năng.", "zh": "请使用 Ctrl、Alt、Command 或功能键。", "hi": "Ctrl, Alt, Command या फ़ंक्शन कुंजी का उपयोग करें।",
    },
    "Clear Shortcut": {
        "de": "Tastenkürzel entfernen", "es": "Borrar atajo", "ko": "단축키 지우기", "pt": "Limpar atalho",
        "fr": "Effacer le raccourci", "vi": "Xóa phím tắt", "zh": "清除快捷键", "hi": "शॉर्टकट हटाएँ",
    },
    "This shortcut is already assigned to {feature}.": {
        "de": "Dieses Tastenkürzel ist bereits {feature} zugewiesen.", "es": "Este atajo ya está asignado a {feature}.", "ko": "이 단축키는 이미 {feature}에 지정되어 있습니다.", "pt": "Este atalho já está atribuído a {feature}.",
        "fr": "Ce raccourci est déjà attribué à {feature}.", "vi": "Phím tắt này đã được gán cho {feature}.", "zh": "此快捷键已分配给 {feature}。", "hi": "यह शॉर्टकट पहले से {feature} को दिया गया है।",
    },
    "This shortcut is already used by Anki: {action}.": {
        "de": "Dieses Tastenkürzel wird bereits von Anki verwendet: {action}.", "es": "Anki ya usa este atajo: {action}.", "ko": "이 단축키는 Anki에서 이미 사용 중입니다: {action}.", "pt": "Este atalho já é usado pelo Anki: {action}.",
        "fr": "Ce raccourci est déjà utilisé par Anki : {action}.", "vi": "Phím tắt này đã được Anki sử dụng: {action}.", "zh": "Anki 已使用此快捷键：{action}。", "hi": "यह शॉर्टकट Anki पहले से उपयोग कर रहा है: {action}।",
    },
    "Shortcut {shortcut} for {feature} conflicts with another Anki shortcut.": {
        "de": "Das Tastenkürzel {shortcut} für {feature} kollidiert mit einem anderen Anki-Tastenkürzel.", "es": "El atajo {shortcut} de {feature} entra en conflicto con otro atajo de Anki.", "ko": "{feature}의 단축키 {shortcut}이 다른 Anki 단축키와 충돌합니다.", "pt": "O atalho {shortcut} de {feature} entra em conflito com outro atalho do Anki.",
        "fr": "Le raccourci {shortcut} de {feature} entre en conflit avec un autre raccourci Anki.", "vi": "Phím tắt {shortcut} cho {feature} xung đột với một phím tắt Anki khác.", "zh": "{feature} 的快捷键 {shortcut} 与另一个 Anki 快捷键冲突。", "hi": "{feature} का शॉर्टकट {shortcut} किसी अन्य Anki शॉर्टकट से टकराता है।",
    },
    "Could not open this sidebar tool.": {
        "de": "Dieses Sidebar-Werkzeug konnte nicht geöffnet werden.", "es": "No se pudo abrir esta herramienta de la barra lateral.", "ko": "이 사이드바 도구를 열 수 없습니다.", "pt": "Não foi possível abrir esta ferramenta da barra lateral.",
        "fr": "Impossible d’ouvrir cet outil de la barre latérale.", "vi": "Không thể mở công cụ thanh bên này.", "zh": "无法打开此侧边栏工具。", "hi": "यह साइडबार टूल नहीं खुल सका।",
    },
    "Enable or disable this sidebar tool.": {
        "de": "Dieses Sidebar-Werkzeug ein- oder ausschalten.", "es": "Activa o desactiva esta herramienta de la barra lateral.", "ko": "이 사이드바 도구를 켜거나 끕니다.", "pt": "Ative ou desative esta ferramenta da barra lateral.",
        "fr": "Activez ou désactivez cet outil de la barre latérale.", "vi": "Bật hoặc tắt công cụ thanh bên này.", "zh": "启用或禁用此侧边栏工具。", "hi": "इस साइडबार टूल को चालू या बंद करें।",
    },
    "Click and press a keyboard shortcut.": {
        "de": "Klicke hier und drücke ein Tastenkürzel.", "es": "Haz clic y pulsa un atajo de teclado.", "ko": "클릭한 다음 키보드 단축키를 누르세요.", "pt": "Clique e pressione um atalho de teclado.",
        "fr": "Cliquez puis appuyez sur un raccourci clavier.", "vi": "Nhấp rồi nhấn một phím tắt.", "zh": "点击后按下键盘快捷键。", "hi": "क्लिक करें और कीबोर्ड शॉर्टकट दबाएँ।",
    },
    "Shortcuts apply immediately after saving. Restart Anki after enabling or disabling sidebar tools.": {
        "de": "Tastenkürzel gelten direkt nach dem Speichern. Starte Anki neu, nachdem du Sidebar-Werkzeuge ein- oder ausgeschaltet hast.", "es": "Los atajos se aplican inmediatamente después de guardar. Reinicia Anki tras activar o desactivar herramientas de la barra lateral.", "ko": "단축키는 저장 후 즉시 적용됩니다. 사이드바 도구를 켜거나 끈 뒤에는 Anki를 다시 시작하세요.", "pt": "Os atalhos são aplicados imediatamente após salvar. Reinicie o Anki depois de ativar ou desativar ferramentas da barra lateral.",
        "fr": "Les raccourcis s’appliquent dès l’enregistrement. Redémarrez Anki après avoir activé ou désactivé des outils de la barre latérale.", "vi": "Phím tắt được áp dụng ngay sau khi lưu. Hãy khởi động lại Anki sau khi bật hoặc tắt các công cụ thanh bên.", "zh": "快捷键保存后立即生效。启用或禁用侧边栏工具后请重启 Anki。", "hi": "शॉर्टकट सेव करने के तुरंत बाद लागू होते हैं। साइडबार टूल चालू या बंद करने के बाद Anki पुनः शुरू करें।",
    },
    "Anki action": {
        "de": "Anki-Aktion", "es": "acción de Anki", "ko": "Anki 작업", "pt": "ação do Anki",
        "fr": "action Anki", "vi": "tác vụ Anki", "zh": "Anki 操作", "hi": "Anki क्रिया",
    },
    "Anki shortcut": {
        "de": "Anki-Tastenkürzel", "es": "atajo de Anki", "ko": "Anki 단축키", "pt": "atalho do Anki",
        "fr": "raccourci Anki", "vi": "phím tắt Anki", "zh": "Anki 快捷键", "hi": "Anki शॉर्टकट",
    },

    # ── Release 1.3 UI additions ──────────────────────────────────────────
    "+{} XP earned": {
        "de": "+{} XP verdient", "es": "+{} XP obtenidos", "ko": "+{} XP 획득", "pt": "+{} XP ganhos",
        "fr": "+{} XP gagnés", "vi": "Đã nhận +{} XP", "zh": "已获得 +{} XP", "hi": "+{} XP अर्जित",
    },
    "Add your own track": {
        "de": "Eigenen Titel hinzufügen", "es": "Añadir tu propia pista", "ko": "내 트랙 추가", "pt": "Adicionar sua própria faixa",
        "fr": "Ajouter votre propre piste", "vi": "Thêm bản nhạc của bạn", "zh": "添加自己的曲目", "hi": "अपना ट्रैक जोड़ें",
    },
    "Celebration popups": {
        "de": "Erfolgs-Pop-ups", "es": "Ventanas de celebración", "ko": "축하 팝업", "pt": "Pop-ups de comemoração",
        "fr": "Fenêtres de célébration", "vi": "Cửa sổ chúc mừng", "zh": "庆祝弹窗", "hi": "उपलब्धि पॉप-अप",
    },
    "Claim your +{} XP in the sidebar.": {
        "de": "Hole deine +{} XP in der Seitenleiste ab.", "es": "Reclama tus +{} XP en la barra lateral.", "ko": "사이드바에서 +{} XP를 받으세요.", "pt": "Resgate seus +{} XP na barra lateral.",
        "fr": "Récupérez vos +{} XP dans la barre latérale.", "vi": "Nhận +{} XP trong thanh bên.", "zh": "在侧边栏领取 +{} XP。", "hi": "साइडबार में अपने +{} XP प्राप्त करें।",
    },
    "Daily Challenge completed!": {
        "de": "Tages-Challenge geschafft!", "es": "¡Desafío diario completado!", "ko": "일일 챌린지 완료!", "pt": "Desafio diário concluído!",
        "fr": "Défi quotidien terminé !", "vi": "Đã hoàn thành thử thách hằng ngày!", "zh": "每日挑战已完成！", "hi": "दैनिक चुनौती पूरी हुई!",
    },
    "Level Up!": {
        "de": "Levelaufstieg!", "es": "¡Subida de nivel!", "ko": "레벨 업!", "pt": "Subiu de nível!",
        "fr": "Niveau supérieur !", "vi": "Lên cấp!", "zh": "升级了！", "hi": "लेवल बढ़ा!",
    },
    "Level {} reached": {
        "de": "Level {} erreicht", "es": "Nivel {} alcanzado", "ko": "레벨 {} 달성", "pt": "Nível {} alcançado",
        "fr": "Niveau {} atteint", "vi": "Đã đạt cấp {}", "zh": "已达到 {} 级", "hi": "लेवल {} प्राप्त",
    },
    "My Tracks": {
        "de": "Meine Titel", "es": "Mis pistas", "ko": "내 트랙", "pt": "Minhas faixas",
        "fr": "Mes pistes", "vi": "Nhạc của tôi", "zh": "我的曲目", "hi": "मेरे ट्रैक",
    },
    "New Rank!": {
        "de": "Neuer Rang!", "es": "¡Nuevo rango!", "ko": "새 랭크!", "pt": "Novo ranking!",
        "fr": "Nouveau rang !", "vi": "Hạng mới!", "zh": "新段位！", "hi": "नई रैंक!",
    },
    "PDF": {
        "de": "PDF", "es": "PDF", "ko": "PDF", "pt": "PDF", "fr": "PDF", "vi": "PDF", "zh": "PDF", "hi": "PDF",
    },
    "Play / Pause": {
        "de": "Wiedergabe / Pause", "es": "Reproducir / Pausar", "ko": "재생 / 일시정지", "pt": "Reproduzir / Pausar",
        "fr": "Lecture / Pause", "vi": "Phát / Tạm dừng", "zh": "播放 / 暂停", "hi": "चलाएँ / रोकें",
    },
    "Player loads below": {
        "de": "Player wird unten geladen", "es": "El reproductor se carga abajo", "ko": "아래에 플레이어가 로드됩니다", "pt": "O player carrega abaixo",
        "fr": "Le lecteur se charge ci-dessous", "vi": "Trình phát tải ở bên dưới", "zh": "播放器将在下方加载", "hi": "प्लेयर नीचे लोड होगा",
    },
    "QtWebEngine is required for the music player.": {
        "de": "Für den Musikplayer wird QtWebEngine benötigt.", "es": "El reproductor de música requiere QtWebEngine.", "ko": "음악 플레이어에는 QtWebEngine이 필요합니다.", "pt": "O player de música requer QtWebEngine.",
        "fr": "QtWebEngine est requis pour le lecteur de musique.", "vi": "Trình phát nhạc yêu cầu QtWebEngine.", "zh": "音乐播放器需要 QtWebEngine。", "hi": "म्यूज़िक प्लेयर के लिए QtWebEngine आवश्यक है।",
    },
    "Reddit": {
        "de": "Reddit", "es": "Reddit", "ko": "Reddit", "pt": "Reddit", "fr": "Reddit", "vi": "Reddit", "zh": "Reddit", "hi": "Reddit",
    },
    "Remove this track": {
        "de": "Diesen Titel entfernen", "es": "Eliminar esta pista", "ko": "이 트랙 제거", "pt": "Remover esta faixa",
        "fr": "Supprimer cette piste", "vi": "Xóa bản nhạc này", "zh": "移除此曲目", "hi": "यह ट्रैक हटाएँ",
    },
    "Resume playback on startup": {
        "de": "Wiedergabe beim Start fortsetzen", "es": "Reanudar al iniciar", "ko": "시작할 때 재생 재개", "pt": "Retomar reprodução ao iniciar",
        "fr": "Reprendre la lecture au démarrage", "vi": "Tiếp tục phát khi khởi động", "zh": "启动时继续播放", "hi": "शुरू होने पर प्लेबैक जारी रखें",
    },
    "Session Summary": {
        "de": "Sitzungsübersicht", "es": "Resumen de la sesión", "ko": "세션 요약", "pt": "Resumo da sessão",
        "fr": "Résumé de la session", "vi": "Tóm tắt phiên", "zh": "学习总结", "hi": "सत्र सारांश",
    },
    "Sounds": {
        "de": "Klänge", "es": "Sonidos", "ko": "소리", "pt": "Sons", "fr": "Sons", "vi": "Âm thanh", "zh": "声音", "hi": "ध्वनियाँ",
    },
    "The start date must not be after the end date.": {
        "de": "Das Startdatum darf nicht nach dem Enddatum liegen.", "es": "La fecha de inicio no puede ser posterior a la fecha final.", "ko": "시작 날짜는 종료 날짜보다 늦을 수 없습니다.", "pt": "A data inicial não pode ser posterior à data final.",
        "fr": "La date de début ne peut pas être postérieure à la date de fin.", "vi": "Ngày bắt đầu không được sau ngày kết thúc.", "zh": "开始日期不能晚于结束日期。", "hi": "शुरुआत की तारीख समाप्ति की तारीख के बाद नहीं हो सकती।",
    },
    "Volume": {
        "de": "Lautstärke", "es": "Volumen", "ko": "볼륨", "pt": "Volume", "fr": "Volume", "vi": "Âm lượng", "zh": "音量", "hi": "आवाज़",
    },
    "in {}": {
        "de": "in {}", "es": "en {}", "ko": "{} 후", "pt": "em {}", "fr": "dans {}", "vi": "trong {}", "zh": "{}后", "hi": "{} में",
    },
    "{} XP to next level": {
        "de": "{} XP bis zum nächsten Level", "es": "{} XP para el siguiente nivel", "ko": "다음 레벨까지 {} XP", "pt": "{} XP para o próximo nível",
        "fr": "{} XP avant le niveau suivant", "vi": "Còn {} XP đến cấp tiếp theo", "zh": "距离下一级还需 {} XP", "hi": "अगले लेवल तक {} XP",
    },
    "{} cards": {
        "de": "{} Karten", "es": "{} tarjetas", "ko": "카드 {}장", "pt": "{} cartões", "fr": "{} cartes", "vi": "{} thẻ", "zh": "{} 张卡片", "hi": "{} कार्ड",
    },
    "<p>Earn XP, level up, and climb the ranks while studying!</p><p><b>How to Earn XP</b></p><ul><li><b>Study Time:</b> 10 XP per minute.</li><li><b>Daily Challenge:</b> Bonus XP based on level.</li><li><b>Streak:</b> 20 XP × current streak day.</li></ul><p><b>Leveling &amp; Ranks</b></p><ul><li>Max Level: 100.</li><li>New Rank every 5 levels.</li></ul><p class=\"tip\">Tip: Consistency is key!</p>": {
        "de": "<p>Sammle beim Lernen XP, steige Level auf und erreiche neue Ränge!</p><p><b>So verdienst du XP</b></p><ul><li><b>Lernzeit:</b> 10 XP pro Minute.</li><li><b>Tages-Challenge:</b> Bonus-XP abhängig vom Level.</li><li><b>Streak:</b> 20 XP × aktueller Streak-Tag.</li></ul><p><b>Level &amp; Ränge</b></p><ul><li>Maximales Level: 100.</li><li>Alle 5 Level ein neuer Rang.</li></ul><p class=\"tip\">Tipp: Regelmäßigkeit ist entscheidend!</p>",
        "es": "<p>¡Gana XP, sube de nivel y avanza de rango mientras estudias!</p><p><b>Cómo ganar XP</b></p><ul><li><b>Tiempo de estudio:</b> 10 XP por minuto.</li><li><b>Desafío diario:</b> XP extra según el nivel.</li><li><b>Racha:</b> 20 XP × día actual de racha.</li></ul><p><b>Niveles y rangos</b></p><ul><li>Nivel máximo: 100.</li><li>Nuevo rango cada 5 niveles.</li></ul><p class=\"tip\">Consejo: ¡La constancia es clave!</p>",
        "ko": "<p>공부하며 XP를 얻고 레벨과 랭크를 올리세요!</p><p><b>XP 획득 방법</b></p><ul><li><b>학습 시간:</b> 분당 10 XP.</li><li><b>일일 챌린지:</b> 레벨에 따른 보너스 XP.</li><li><b>연속 학습:</b> 현재 연속 일수 × 20 XP.</li></ul><p><b>레벨과 랭크</b></p><ul><li>최대 레벨: 100.</li><li>5레벨마다 새 랭크.</li></ul><p class=\"tip\">팁: 꾸준함이 중요합니다!</p>",
        "pt": "<p>Ganhe XP, suba de nível e avance no ranking enquanto estuda!</p><p><b>Como ganhar XP</b></p><ul><li><b>Tempo de estudo:</b> 10 XP por minuto.</li><li><b>Desafio diário:</b> XP bônus conforme o nível.</li><li><b>Sequência:</b> 20 XP × dia atual da sequência.</li></ul><p><b>Níveis e rankings</b></p><ul><li>Nível máximo: 100.</li><li>Novo ranking a cada 5 níveis.</li></ul><p class=\"tip\">Dica: consistência é essencial!</p>",
        "fr": "<p>Gagnez de l’XP, montez de niveau et progressez dans les rangs en étudiant !</p><p><b>Comment gagner de l’XP</b></p><ul><li><b>Temps d’étude :</b> 10 XP par minute.</li><li><b>Défi quotidien :</b> XP bonus selon le niveau.</li><li><b>Série :</b> 20 XP × jour actuel de la série.</li></ul><p><b>Niveaux et rangs</b></p><ul><li>Niveau maximal : 100.</li><li>Nouveau rang tous les 5 niveaux.</li></ul><p class=\"tip\">Conseil : la régularité est essentielle !</p>",
        "vi": "<p>Kiếm XP, lên cấp và tăng hạng trong khi học!</p><p><b>Cách kiếm XP</b></p><ul><li><b>Thời gian học:</b> 10 XP mỗi phút.</li><li><b>Thử thách hằng ngày:</b> XP thưởng theo cấp.</li><li><b>Chuỗi:</b> 20 XP × ngày chuỗi hiện tại.</li></ul><p><b>Cấp &amp; hạng</b></p><ul><li>Cấp tối đa: 100.</li><li>Hạng mới mỗi 5 cấp.</li></ul><p class=\"tip\">Mẹo: sự đều đặn là chìa khóa!</p>",
        "zh": "<p>学习时赚取 XP、升级并提升段位！</p><p><b>如何赚取 XP</b></p><ul><li><b>学习时间：</b>每分钟 10 XP。</li><li><b>每日挑战：</b>根据等级获得额外 XP。</li><li><b>连续学习：</b>20 XP × 当前连续天数。</li></ul><p><b>等级与段位</b></p><ul><li>最高等级：100。</li><li>每 5 级获得新段位。</li></ul><p class=\"tip\">提示：坚持最重要！</p>",
        "hi": "<p>पढ़ते समय XP कमाएँ, लेवल बढ़ाएँ और नई रैंक पाएँ!</p><p><b>XP कैसे कमाएँ</b></p><ul><li><b>अध्ययन समय:</b> प्रति मिनट 10 XP.</li><li><b>दैनिक चुनौती:</b> लेवल के आधार पर बोनस XP.</li><li><b>स्ट्रीक:</b> 20 XP × वर्तमान स्ट्रीक दिन.</li></ul><p><b>लेवल और रैंक</b></p><ul><li>अधिकतम लेवल: 100.</li><li>हर 5 लेवल पर नई रैंक.</li></ul><p class=\"tip\">सुझाव: निरंतरता सबसे महत्वपूर्ण है!</p>",
    },

    # Statistics widget and its dedicated settings dialog
    "Last year": {"de":"Letztes Jahr","es":"Último año","ko":"지난 1년","pt":"Último ano","fr":"Année écoulée","vi":"Năm qua","zh":"过去一年","hi":"पिछला वर्ष"},
    "Choose Background Image": {"de":"Hintergrundbild auswählen","es":"Elegir imagen de fondo","ko":"배경 이미지 선택","pt":"Escolher imagem de fundo","fr":"Choisir une image d’arrière-plan","vi":"Chọn ảnh nền","zh":"选择背景图片","hi":"पृष्ठभूमि चित्र चुनें"},
    "Images (*.jpg *.jpeg *.png *.webp)": {"de":"Bilder (*.jpg *.jpeg *.png *.webp)","es":"Imágenes (*.jpg *.jpeg *.png *.webp)","ko":"이미지 (*.jpg *.jpeg *.png *.webp)","pt":"Imagens (*.jpg *.jpeg *.png *.webp)","fr":"Images (*.jpg *.jpeg *.png *.webp)","vi":"Hình ảnh (*.jpg *.jpeg *.png *.webp)","zh":"图片 (*.jpg *.jpeg *.png *.webp)","hi":"चित्र (*.jpg *.jpeg *.png *.webp)"},
    "The image must be smaller than 20 MB.": {"de":"Das Bild muss kleiner als 20 MB sein.","es":"La imagen debe tener menos de 20 MB.","ko":"이미지는 20MB보다 작아야 합니다.","pt":"A imagem deve ter menos de 20 MB.","fr":"L’image doit faire moins de 20 Mo.","vi":"Ảnh phải nhỏ hơn 20 MB.","zh":"图片必须小于 20 MB。","hi":"चित्र 20 MB से छोटा होना चाहिए।"},
    "Please choose a valid PNG, JPEG or WebP image.": {"de":"Bitte wähle ein gültiges PNG-, JPEG- oder WebP-Bild.","es":"Elige una imagen PNG, JPEG o WebP válida.","ko":"유효한 PNG, JPEG 또는 WebP 이미지를 선택하세요.","pt":"Escolha uma imagem PNG, JPEG ou WebP válida.","fr":"Choisissez une image PNG, JPEG ou WebP valide.","vi":"Hãy chọn ảnh PNG, JPEG hoặc WebP hợp lệ.","zh":"请选择有效的 PNG、JPEG 或 WebP 图片。","hi":"मान्य PNG, JPEG या WebP चित्र चुनें।"},
    "Animated images are not supported.": {"de":"Animierte Bilder werden nicht unterstützt.","es":"Las imágenes animadas no son compatibles.","ko":"애니메이션 이미지는 지원되지 않습니다.","pt":"Imagens animadas não são suportadas.","fr":"Les images animées ne sont pas prises en charge.","vi":"Không hỗ trợ ảnh động.","zh":"不支持动画图片。","hi":"एनिमेटेड चित्र समर्थित नहीं हैं।"},
    "The image dimensions could not be read.": {"de":"Die Bildabmessungen konnten nicht gelesen werden.","es":"No se pudieron leer las dimensiones de la imagen.","ko":"이미지 크기를 읽을 수 없습니다.","pt":"Não foi possível ler as dimensões da imagem.","fr":"Les dimensions de l’image n’ont pas pu être lues.","vi":"Không thể đọc kích thước ảnh.","zh":"无法读取图片尺寸。","hi":"चित्र के आयाम पढ़े नहीं जा सके।"},
    "The image is too large. Use an image below 40 megapixels.": {"de":"Das Bild ist zu groß. Verwende ein Bild unter 40 Megapixeln.","es":"La imagen es demasiado grande. Usa una imagen de menos de 40 megapíxeles.","ko":"이미지가 너무 큽니다. 4천만 화소 미만 이미지를 사용하세요.","pt":"A imagem é grande demais. Use uma imagem com menos de 40 megapixels.","fr":"L’image est trop grande. Utilisez une image de moins de 40 mégapixels.","vi":"Ảnh quá lớn. Hãy dùng ảnh dưới 40 megapixel.","zh":"图片过大。请使用低于 4000 万像素的图片。","hi":"चित्र बहुत बड़ा है। 40 मेगापिक्सेल से छोटा चित्र उपयोग करें।"},
    "The image could not be decoded.": {"de":"Das Bild konnte nicht dekodiert werden.","es":"No se pudo decodificar la imagen.","ko":"이미지를 디코딩할 수 없습니다.","pt":"Não foi possível decodificar a imagem.","fr":"L’image n’a pas pu être décodée.","vi":"Không thể giải mã ảnh.","zh":"无法解码图片。","hi":"चित्र डिकोड नहीं किया जा सका।"},
    "The optimized background could not be saved.": {"de":"Der optimierte Hintergrund konnte nicht gespeichert werden.","es":"No se pudo guardar el fondo optimizado.","ko":"최적화된 배경을 저장할 수 없습니다.","pt":"Não foi possível salvar o fundo otimizado.","fr":"L’arrière-plan optimisé n’a pas pu être enregistré.","vi":"Không thể lưu nền đã tối ưu.","zh":"无法保存优化后的背景。","hi":"अनुकूलित पृष्ठभूमि सहेजी नहीं जा सकी।"},

}

# Gamification sidebar settings.
# Assistant: chatbot picker and Google sign-in window
TRANSLATIONS.update({
    "Sign in with Google": {"de": "Mit Google anmelden", "es": "Iniciar sesión con Google", "ko": "Google로 로그인", "pt": "Entrar com o Google", "fr": "Se connecter avec Google", "vi": "Đăng nhập bằng Google", "zh": "使用 Google 登录", "hi": "Google से साइन इन करें"},
    "Sign in once here – Gemini, NotebookLM and YouTube Music then use this Google account.": {"de": "Melde dich hier einmal an – Gemini, NotebookLM und YouTube Music nutzen dann dieses Google-Konto.", "es": "Inicia sesión aquí una vez: Gemini, NotebookLM y YouTube Music usarán esta cuenta de Google.", "ko": "여기서 한 번 로그인하면 Gemini, NotebookLM, YouTube Music이 이 Google 계정을 사용합니다.", "pt": "Entre aqui uma vez – o Gemini, o NotebookLM e o YouTube Music passam a usar esta conta Google.", "fr": "Connecte-toi ici une fois – Gemini, NotebookLM et YouTube Music utiliseront ensuite ce compte Google.", "vi": "Đăng nhập một lần tại đây – Gemini, NotebookLM và YouTube Music sẽ dùng tài khoản Google này.", "zh": "在这里登录一次——之后 Gemini、NotebookLM 和 YouTube Music 都会使用这个 Google 账号。", "hi": "यहाँ एक बार साइन इन करें – फिर Gemini, NotebookLM और YouTube Music इसी Google खाते का उपयोग करेंगे।"},
    "Choose the chatbot": {"de": "Chatbot wählen", "es": "Elegir el chatbot", "ko": "챗봇 선택", "pt": "Escolher o chatbot", "fr": "Choisir le chatbot", "vi": "Chọn chatbot", "zh": "选择聊天机器人", "hi": "चैटबॉट चुनें"},
})

TRANSLATIONS.update({
    "Streak sensitivity": {
        "de": "Streak-Empfindlichkeit"
    },
    "Minimum reviews per day": {
        "de": "Mindestzahl Wiederholungen pro Tag"
    },
    "Creating cards can also count": {
        "de": "Auch das Erstellen von Karten zählt"
    },
    "Minimum new cards per day": {
        "de": "Mindestzahl neuer Karten pro Tag"
    },
    "A day counts when either enabled goal is reached. Anki’s day boundary applies. Changes recalculate your current streak, including past days; earned XP and badges stay yours.": {
        "de": "Ein Tag zählt, sobald eines der aktivierten Ziele erreicht ist. Es gilt Ankis Tagesgrenze. Änderungen berechnen deine aktuelle Streak auch rückwirkend neu; verdiente XP und Abzeichen bleiben erhalten."
    },
    "Uses creation dates of cards still in your collection, including imported cards. Deleted cards no longer count.": {
        "de": "Es zählen die Erstellungsdaten der noch vorhandenen Karten, auch bei importierten Karten. Gelöschte Karten zählen nicht mehr."
    },
    "Your streak counts consecutive qualifying Anki days. Today remains open until the next day begins. Choose your daily criteria in Settings. Achievement badges keep their own study criteria.": {
        "de": "Deine Streak zählt aufeinanderfolgende Anki-Tage, an denen du dein Ziel erreichst. Für heute hast du bis zum nächsten Tagesbeginn Zeit. Deine Tagesziele legst du in den Einstellungen fest. Für Abzeichen gelten weiterhin ihre eigenen Lernkriterien."
    }
})

# Deck Overview customization.
TRANSLATIONS.update({
    "Classic": {
        "de": "Klassisch"
    },
    "Focus": {
        "de": "Fokus"
    },
    "Overview": {
        "de": "Übersicht"
    },
    "Last 7 days": {
        "de": "Letzte 7 Tage"
    },
    "Last 30 days": {
        "de": "Letzte 30 Tage"
    },
    "All time": {
        "de": "Gesamter Zeitraum"
    },
    "Recall indicator": {
        "de": "Lernindikator (Smiley)"
    },
    "Green from (%)": {
        "de": "Grün ab (%)"
    },
    "Orange from (%)": {
        "de": "Orange ab (%)"
    },
    "The green threshold must be higher than the orange threshold.": {
        "de": "Der Grenzwert für Grün muss höher sein als der für Orange."
    },
    "Not enough reviews yet": {
        "de": "Noch zu wenige Wiederholungen"
    },
    "Customize Deck Overview": {
        "de": "Deckübersicht anpassen"
    },
    "Remembered answers across all learning and review steps. Period: {}.": {
        "de": "Erinnerte Antworten aus Lernschritten und Wiederholungen. Zeitraum: {}."
    },
    "Mature cards have an interval of at least 21 days. They still need reviews.": {
        "de": "Diese Karten haben ein Intervall von mindestens 21 Tagen. Sie müssen weiterhin wiederholt werden."
    },
    "Remembered review answers in the last 30 days; Again counts as forgotten. Green from {}%, orange from {}%, red below. Neutral until 20 reviews. This describes recent recall, not effort or ability.": {
        "de": "Erinnerte Wiederholungsantworten der letzten 30 Tage; „Nochmal“ zählt als vergessen. Grün ab {} %, Orange ab {} %, darunter Rot. Unter 20 Wiederholungen bleibt die Anzeige neutral. Sie beschreibt die letzte Erinnerungsleistung, nicht deinen Einsatz oder deine Fähigkeiten."
    }
})

TRANSLATIONS.update({
    "Period": {"de": "Zeitraum"},
    "Period for the retention rate. The smiley uses the last 30 days; the graph shows the last 14 days.": {"de": "Zeitraum für die Behaltensrate. Der Smiley nutzt die letzten 30 Tage, der Graph zeigt die letzten 14 Tage."},
    "How to set the smiley": {"de": "Smiley einstellen – kurz erklärt"},
    "The smiley reflects remembered review answers over 30 days, not effort. With green at 85 and orange at 70: 90% is green, 80% orange, 60% red. Lower the thresholds for a more forgiving indicator. Fewer than 20 answers are not rated.": {"de": "Der Smiley zeigt, wie viele Wiederholungsantworten du in 30 Tagen erinnert hast, nicht deinen Einsatz. Bei Grün ab 85 und Orange ab 70 gilt: 90 % sind grün, 80 % orange, 60 % rot. Niedrigere Grenzen machen die Anzeige toleranter. Weniger als 20 Antworten werden noch nicht bewertet."}
})

TRANSLATIONS.update({
 "Confident": {"de":"Sicher"},
 "Still practicing": {"de":"Noch am Üben"},
 "Needs work": {"de":"Noch unsicher"},
 "Could not save the smiley. Please try again.": {"de":"Der Smiley konnte nicht gespeichert werden. Bitte versuche es erneut."}
})

TRANSLATIONS.update({
 "Auto": {"de":"Auto"},
 "Show indicator in Deck Browser for this deck": {"de":"Punkt für dieses Deck in der Deckübersicht anzeigen"},
 "Choose how you feel about this deck. Your choice stays until you change it or return to Auto.": {"de":"Wähle, wie sicher du dich mit diesem Deck fühlst. Deine Auswahl bleibt, bis du sie änderst oder zu Auto zurückkehrst."},
 "Could not save the setting. Please try again.": {"de":"Die Einstellung konnte nicht gespeichert werden. Bitte versuche es erneut."}
})

TRANSLATIONS.update({
 "Show indicators in Deck Browser for all decks": {"de":"Punkte für alle Decks in der Deckübersicht anzeigen"},
 "Remaining": {"de":"Verbleibend"},
 "No cards waiting right now": {"de":"Gerade stehen keine Karten an"},
 "Reviews · last 14 days": {"de":"Wiederholungen · letzte 14 Tage"},
 "No reviews in the last 14 days": {"de":"Keine Wiederholungen in den letzten 14 Tagen"},
 "All decks are enabled in Settings.": {"de":"In den Einstellungen sind alle Decks aktiviert."},
})

TRANSLATIONS.update({
 "Indicator hidden: {}/20 review answers in the last 30 days.": {"de":"Punkt noch ausgeblendet: {}/20 Wiederholungsantworten in den letzten 30 Tagen."}
})

TRANSLATIONS.update({
 "Auto appears after 20 review answers in 30 days. Manual smileys appear immediately.": {"de":"Auto erscheint ab 20 Wiederholungsantworten in 30 Tagen. Manuell gewählte Smileys erscheinen sofort als Punkt."},
 "Off: enable individual decks via the smiley. On: show all eligible decks. Auto requires 20 review answers in the last 30 days. Manual smileys appear immediately.": {"de":"Aus: Einzelne Decks über den Smiley aktivieren. An: Alle geeigneten Decks anzeigen. Auto benötigt 20 Wiederholungsantworten in den letzten 30 Tagen. Manuelle Smileys erscheinen sofort als Punkt."}
})

TRANSLATIONS.update({
 "Wide Deck List": {"de":"Breite Deckliste"},
 "Match the deck list width to the widgets. Turn off for a compact deck list.": {"de":"Breite der Deckliste an die Widgets anpassen. Für eine kompakte Deckliste ausschalten."},
})

TRANSLATIONS.update({
    "Timer": {"de": "Timer", "es": "Temporizador", "ko": "타이머", "pt": "Temporizador", "fr": "Minuterie", "vi": "Bộ đếm giờ", "zh": "计时器", "hi": "टाइमर"},
    "Pomodoro Statistics": {"de": "Pomodoro-Statistiken", "es": "Estadísticas Pomodoro", "ko": "포모도로 통계", "pt": "Estatísticas Pomodoro", "fr": "Statistiques Pomodoro", "vi": "Thống kê Pomodoro", "zh": "番茄钟统计", "hi": "पोमोडोरो आँकड़े"},
})

TRANSLATIONS.update({
})

TRANSLATIONS.update({
    "Analytics": {"de":"Analytics","es":"Análisis","ko":"분석","pt":"Análise","fr":"Analyse","vi":"Phân tích","zh":"分析","hi":"विश्लेषण"},
    "Study time": {"de":"Lernzeit","es":"Tiempo de estudio","ko":"학습 시간","pt":"Tempo de estudo","fr":"Temps d’étude","vi":"Thời gian học","zh":"学习时间","hi":"अध्ययन समय"},
    "Study time · Last 30 days": {"de":"Lernzeit · Letzte 30 Tage","es":"Tiempo de estudio · Últimos 30 días","ko":"학습 시간 · 최근 30일","pt":"Tempo de estudo · Últimos 30 dias","fr":"Temps d’étude · 30 derniers jours","vi":"Thời gian học · 30 ngày qua","zh":"学习时间 · 最近30天","hi":"अध्ययन समय · पिछले 30 दिन"},
    "Total study time": {"de":"Gesamte Lernzeit","es":"Tiempo total de estudio","ko":"총 학습 시간","pt":"Tempo total de estudo","fr":"Temps d’étude total","vi":"Tổng thời gian học","zh":"总学习时间","hi":"कुल अध्ययन समय"},
    "About this study time": {"de":"Wie wird die Lernzeit berechnet?","es":"Cómo se calcula este tiempo","ko":"학습 시간 계산 방법","pt":"Como este tempo é calculado","fr":"Comment ce temps est-il calculé ?","vi":"Cách tính thời gian học","zh":"学习时间如何计算？","hi":"यह समय कैसे मापा जाता है?"},
    "Loading study time…": {"de":"Lernzeit wird geladen…","es":"Cargando tiempo de estudio…","ko":"학습 시간 불러오는 중…","pt":"Carregando tempo de estudo…","fr":"Chargement du temps d’étude…","vi":"Đang tải thời gian học…","zh":"正在加载学习时间…","hi":"अध्ययन समय लोड हो रहा है…"},
    "Study time could not be loaded.": {"de":"Die Lernzeit konnte nicht geladen werden.","es":"No se pudo cargar el tiempo de estudio.","ko":"학습 시간을 불러올 수 없습니다.","pt":"Não foi possível carregar o tempo de estudo.","fr":"Impossible de charger le temps d’étude.","vi":"Không thể tải thời gian học.","zh":"无法加载学习时间。","hi":"अध्ययन समय लोड नहीं हो सका।"},
    "No recorded study time in the last 30 days.": {"de":"In den letzten 30 Tagen wurde keine Lernzeit aufgezeichnet.","es":"No hay tiempo de estudio registrado en los últimos 30 días.","ko":"최근 30일 동안 기록된 학습 시간이 없습니다.","pt":"Nenhum tempo de estudo registrado nos últimos 30 dias.","fr":"Aucun temps d’étude enregistré au cours des 30 derniers jours.","vi":"Không có thời gian học được ghi lại trong 30 ngày qua.","zh":"最近30天没有记录到学习时间。","hi":"पिछले 30 दिनों में कोई अध्ययन समय दर्ज नहीं हुआ।"},
    "Recorded answer time, capped by your Anki deck settings. Includes learning and review cards, not breaks or card editing. Parent decks include their subdecks; totals count each answer once. Cards are grouped by their current deck; deleted cards are excluded.": {
        "de":"Aufgezeichnete Antwortzeit, begrenzt durch deine Anki-Deck-Einstellungen. Enthält Lern- und Wiederholungskarten, keine Pausen oder Kartenbearbeitung. Übergeordnete Decks enthalten ihre Unterdecks; jede Antwort zählt insgesamt nur einmal. Karten werden ihrem aktuellen Deck zugeordnet; gelöschte Karten sind nicht enthalten.",
        "es":"Tiempo de respuesta registrado, limitado por los ajustes de Anki. Incluye tarjetas de aprendizaje y repaso, no pausas ni edición. Los mazos principales incluyen sus submazos; cada respuesta cuenta una sola vez en el total. Se usa el mazo actual de cada tarjeta; se excluyen las tarjetas eliminadas.",
        "ko":"Anki 덱 설정에 따라 상한이 적용된 응답 시간입니다. 학습 및 복습 카드를 포함하며 휴식이나 카드 편집 시간은 제외합니다. 상위 덱은 하위 덱을 포함하며 총합에서 각 응답은 한 번만 계산됩니다. 카드는 현재 덱으로 분류하며 삭제된 카드는 제외합니다.",
        "pt":"Tempo de resposta registrado, limitado pelas configurações do Anki. Inclui cartões em aprendizado e revisão, não pausas ou edição. Baralhos principais incluem os sub-baralhos; cada resposta é contada apenas uma vez no total. Os cartões são agrupados pelo baralho atual; cartões excluídos não são incluídos.",
        "fr":"Temps de réponse enregistré, plafonné par les réglages d’Anki. Inclut les cartes en apprentissage et en révision, pas les pauses ni la modification. Les paquets parents incluent leurs sous-paquets ; chaque réponse compte une seule fois dans le total. Les cartes sont regroupées selon leur paquet actuel ; les cartes supprimées sont exclues.",
        "vi":"Thời gian trả lời đã ghi, giới hạn theo cài đặt bộ thẻ Anki. Bao gồm thẻ đang học và ôn tập, không gồm nghỉ giải lao hay chỉnh sửa thẻ. Bộ thẻ cha bao gồm bộ thẻ con; mỗi câu trả lời chỉ được tính một lần trong tổng. Thẻ được nhóm theo bộ thẻ hiện tại; không gồm thẻ đã xóa.",
        "zh":"记录的作答时间，上限由 Anki 牌组设置决定。包括学习和复习卡片，不包括休息或编辑卡片。父牌组包含子牌组；总计中每次作答只计一次。卡片按当前牌组归类；已删除的卡片不计入。",
        "hi":"दर्ज उत्तर समय, जिसकी सीमा Anki डेक सेटिंग्स तय करती हैं। इसमें सीखने और दोहराने वाले कार्ड शामिल हैं, विराम या कार्ड संपादन नहीं। मुख्य डेक में उपडेक शामिल हैं; कुल में हर उत्तर एक बार गिना जाता है। कार्ड उनके वर्तमान डेक के अनुसार समूहित हैं; हटाए गए कार्ड शामिल नहीं हैं।"
    },
})

# Consistent feature branding; preserve legacy translation keys for callers.
for _brand_key, _brand_values in list(TRANSLATIONS.items()):
    if "Mind Map" in _brand_key:
        TRANSLATIONS[_brand_key.replace("Mind Map", "MindMap")] = {
            lang: value.replace("Mind Map", "MindMap").replace("Mindmap", "MindMap")
            for lang, value in _brand_values.items()
        }
TRANSLATIONS["MindMap"] = {lang: "MindMap" for lang in ("de", "es", "ko", "pt", "fr", "vi", "zh", "hi", "pl")}
TRANSLATIONS["FreeMap"] = {lang: "FreeMap" for lang in TRANSLATIONS["MindMap"]}

# Optional study background.
TRANSLATIONS.update({'Show while studying': {'de': 'Beim Lernen anzeigen',
                         'es': 'Mostrar al estudiar',
                         'ko': '학습 중 표시',
                         'pt': 'Mostrar ao estudar',
                         'fr': 'Afficher pendant l’étude',
                         'vi': 'Hiển thị khi học',
                         'zh': '学习时显示',
                         'hi': 'पढ़ते समय दिखाएँ'},
 'Use the same image behind your learning cards.': {'de': 'Dasselbe Bild hinter deinen Lernkarten verwenden.',
                                                    'es': 'Usa la misma imagen detrás de tus tarjetas.',
                                                    'ko': '학습 카드 뒤에 같은 이미지를 사용합니다.',
                                                    'pt': 'Use a mesma imagem atrás dos cartões.',
                                                    'fr': 'Utilisez la même image derrière vos cartes.',
                                                    'vi': 'Dùng cùng hình ảnh phía sau thẻ học.',
                                                    'zh': '在学习卡片后使用同一张图片。',
                                                    'hi': 'अपने कार्ड के पीछे उसी चित्र का उपयोग करें।'},
 'Background intensity': {'de': 'Hintergrundintensität',
                          'es': 'Intensidad del fondo',
                          'ko': '배경 강도',
                          'pt': 'Intensidade do fundo',
                          'fr': 'Intensité du fond',
                          'vi': 'Độ đậm của nền',
                          'zh': '背景强度',
                          'hi': 'पृष्ठभूमि की तीव्रता'},
 'Lower values make the image lighter in Light Mode and darker in Dark Mode.': {'de': 'Niedrigere Werte '
                                                                                      'machen das Bild im '
                                                                                      'Light Mode heller und '
                                                                                      'im Dark Mode dunkler.',
                                                                                'es': 'Los valores bajos '
                                                                                      'aclaran la imagen en '
                                                                                      'modo claro y la '
                                                                                      'oscurecen en modo '
                                                                                      'oscuro.',
                                                                                'ko': '값이 낮을수록 라이트 모드에서는 '
                                                                                      '밝아지고 다크 모드에서는 어두워집니다.',
                                                                                'pt': 'Valores menores '
                                                                                      'clareiam a imagem no '
                                                                                      'modo claro e '
                                                                                      'escurecem no modo '
                                                                                      'escuro.',
                                                                                'fr': 'Une valeur faible '
                                                                                      'éclaircit l’image en '
                                                                                      'mode clair et '
                                                                                      'l’assombrit en mode '
                                                                                      'sombre.',
                                                                                'vi': 'Giá trị thấp làm ảnh '
                                                                                      'sáng hơn ở chế độ '
                                                                                      'sáng và tối hơn ở chế '
                                                                                      'độ tối.',
                                                                                'zh': '较低的值让图片在浅色模式下更亮，在深色模式下更暗。',
                                                                                'hi': 'कम मान चित्र को लाइट '
                                                                                      'मोड में हल्का और '
                                                                                      'डार्क मोड में गहरा '
                                                                                      'बनाते हैं।'},
 'Study background blur': {'de': 'Unschärfe beim Lernen',
                           'es': 'Desenfoque al estudiar',
                           'ko': '학습 배경 흐림',
                           'pt': 'Desfoque ao estudar',
                           'fr': 'Flou pendant l’étude',
                           'vi': 'Độ mờ nền khi học',
                           'zh': '学习背景模糊',
                           'hi': 'अध्ययन पृष्ठभूमि का धुंधलापन'},
 'Softens only the background. Card content stays sharp.': {'de': 'Macht nur den Hintergrund weicher. '
                                                                  'Karteninhalte bleiben scharf.',
                                                            'es': 'Suaviza solo el fondo. El contenido sigue '
                                                                  'nítido.',
                                                            'ko': '배경만 흐려집니다. 카드 내용은 선명하게 유지됩니다.',
                                                            'pt': 'Suaviza apenas o fundo. O conteúdo '
                                                                  'permanece nítido.',
                                                            'fr': 'Adoucit uniquement le fond. Le contenu '
                                                                  'reste net.',
                                                            'vi': 'Chỉ làm mờ nền. Nội dung thẻ vẫn rõ nét.',
                                                            'zh': '仅柔化背景，卡片内容保持清晰。',
                                                            'hi': 'केवल पृष्ठभूमि धुंधली होती है। कार्ड की '
                                                                  'सामग्री स्पष्ट रहती है।'},
 'Card preview': {'de': 'Kartenvorschau',
                  'es': 'Vista previa de tarjeta',
                  'ko': '카드 미리보기',
                  'pt': 'Prévia do cartão',
                  'fr': 'Aperçu de carte',
                  'vi': 'Xem trước thẻ',
                  'zh': '卡片预览',
                  'hi': 'कार्ड पूर्वावलोकन'},
 'Card templates with their own backgrounds may cover the image or look different. You can turn this off at any time.': {'de': 'Kartenvorlagen '
                                                                                                                               'mit '
                                                                                                                               'eigenen '
                                                                                                                               'Hintergründen '
                                                                                                                               'können '
                                                                                                                               'das '
                                                                                                                               'Bild '
                                                                                                                               'verdecken '
                                                                                                                               'oder '
                                                                                                                               'anders '
                                                                                                                               'aussehen. '
                                                                                                                               'Du '
                                                                                                                               'kannst '
                                                                                                                               'die '
                                                                                                                               'Option '
                                                                                                                               'jederzeit '
                                                                                                                               'ausschalten.',
                                                                                                                         'es': 'Las '
                                                                                                                               'plantillas '
                                                                                                                               'con '
                                                                                                                               'fondos '
                                                                                                                               'propios '
                                                                                                                               'pueden '
                                                                                                                               'cubrir '
                                                                                                                               'la '
                                                                                                                               'imagen '
                                                                                                                               'o '
                                                                                                                               'verse '
                                                                                                                               'diferentes. '
                                                                                                                               'Puedes '
                                                                                                                               'desactivar '
                                                                                                                               'esta '
                                                                                                                               'opción '
                                                                                                                               'en '
                                                                                                                               'cualquier '
                                                                                                                               'momento.',
                                                                                                                         'ko': '자체 '
                                                                                                                               '배경이 '
                                                                                                                               '있는 '
                                                                                                                               '카드 '
                                                                                                                               '템플릿은 '
                                                                                                                               '이미지를 '
                                                                                                                               '가리거나 '
                                                                                                                               '다르게 '
                                                                                                                               '보일 '
                                                                                                                               '수 '
                                                                                                                               '있습니다. '
                                                                                                                               '언제든 '
                                                                                                                               '끌 '
                                                                                                                               '수 '
                                                                                                                               '있습니다.',
                                                                                                                         'pt': 'Modelos '
                                                                                                                               'com '
                                                                                                                               'fundos '
                                                                                                                               'próprios '
                                                                                                                               'podem '
                                                                                                                               'cobrir '
                                                                                                                               'a '
                                                                                                                               'imagem '
                                                                                                                               'ou '
                                                                                                                               'ter '
                                                                                                                               'outra '
                                                                                                                               'aparência. '
                                                                                                                               'Você '
                                                                                                                               'pode '
                                                                                                                               'desativar '
                                                                                                                               'a '
                                                                                                                               'opção '
                                                                                                                               'a '
                                                                                                                               'qualquer '
                                                                                                                               'momento.',
                                                                                                                         'fr': 'Les '
                                                                                                                               'modèles '
                                                                                                                               'avec '
                                                                                                                               'leur '
                                                                                                                               'propre '
                                                                                                                               'fond '
                                                                                                                               'peuvent '
                                                                                                                               'masquer '
                                                                                                                               'l’image '
                                                                                                                               'ou '
                                                                                                                               'modifier '
                                                                                                                               'son '
                                                                                                                               'apparence. '
                                                                                                                               'Vous '
                                                                                                                               'pouvez '
                                                                                                                               'désactiver '
                                                                                                                               'cette '
                                                                                                                               'option '
                                                                                                                               'à '
                                                                                                                               'tout '
                                                                                                                               'moment.',
                                                                                                                         'vi': 'Mẫu '
                                                                                                                               'thẻ '
                                                                                                                               'có '
                                                                                                                               'nền '
                                                                                                                               'riêng '
                                                                                                                               'có '
                                                                                                                               'thể '
                                                                                                                               'che '
                                                                                                                               'ảnh '
                                                                                                                               'hoặc '
                                                                                                                               'hiển '
                                                                                                                               'thị '
                                                                                                                               'khác. '
                                                                                                                               'Bạn '
                                                                                                                               'có '
                                                                                                                               'thể '
                                                                                                                               'tắt '
                                                                                                                               'tùy '
                                                                                                                               'chọn '
                                                                                                                               'bất '
                                                                                                                               'cứ '
                                                                                                                               'lúc '
                                                                                                                               'nào.',
                                                                                                                         'zh': '自带背景的卡片模板可能遮住图片或呈现不同效果。你可以随时关闭此选项。',
                                                                                                                         'hi': 'अपने '
                                                                                                                               'बैकग्राउंड '
                                                                                                                               'वाले '
                                                                                                                               'कार्ड '
                                                                                                                               'टेम्पलेट '
                                                                                                                               'चित्र '
                                                                                                                               'को '
                                                                                                                               'ढक '
                                                                                                                               'सकते '
                                                                                                                               'हैं '
                                                                                                                               'या '
                                                                                                                               'अलग '
                                                                                                                               'दिख '
                                                                                                                               'सकते '
                                                                                                                               'हैं। '
                                                                                                                               'इसे '
                                                                                                                               'कभी '
                                                                                                                               'भी '
                                                                                                                               'बंद '
                                                                                                                               'कर '
                                                                                                                               'सकते '
                                                                                                                               'हैं।'},
 'A background for studying': {'de': 'Ein Hintergrund fürs Lernen',
                               'es': 'Un fondo para estudiar',
                               'ko': '학습용 배경',
                               'pt': 'Um fundo para estudar',
                               'fr': 'Un fond pour étudier',
                               'vi': 'Hình nền khi học',
                               'zh': '学习背景',
                               'hi': 'पढ़ाई के लिए पृष्ठभूमि'},
 'Some card templates use their own colours, images or panels. These may cover the background or change how it looks. This can be due to the card design, rather than a Smart Study error.': {'de': 'Manche '
                                                                                                                                                                                                   'Kartenvorlagen '
                                                                                                                                                                                                   'verwenden '
                                                                                                                                                                                                   'eigene '
                                                                                                                                                                                                   'Farben, '
                                                                                                                                                                                                   'Bilder '
                                                                                                                                                                                                   'oder '
                                                                                                                                                                                                   'Flächen. '
                                                                                                                                                                                                   'Diese '
                                                                                                                                                                                                   'können '
                                                                                                                                                                                                   'den '
                                                                                                                                                                                                   'Hintergrund '
                                                                                                                                                                                                   'verdecken '
                                                                                                                                                                                                   'oder '
                                                                                                                                                                                                   'seine '
                                                                                                                                                                                                   'Darstellung '
                                                                                                                                                                                                   'verändern. '
                                                                                                                                                                                                   'Das '
                                                                                                                                                                                                   'kann '
                                                                                                                                                                                                   'am '
                                                                                                                                                                                                   'Kartendesign '
                                                                                                                                                                                                   'liegen '
                                                                                                                                                                                                   'und '
                                                                                                                                                                                                   'muss '
                                                                                                                                                                                                   'kein '
                                                                                                                                                                                                   'Fehler '
                                                                                                                                                                                                   'von '
                                                                                                                                                                                                   'Smart Study '
                                                                                                                                                                                                   'sein.',
                                                                                                                                                                                             'es': 'Algunas '
                                                                                                                                                                                                   'plantillas '
                                                                                                                                                                                                   'usan '
                                                                                                                                                                                                   'colores, '
                                                                                                                                                                                                   'imágenes '
                                                                                                                                                                                                   'o '
                                                                                                                                                                                                   'paneles '
                                                                                                                                                                                                   'propios. '
                                                                                                                                                                                                   'Pueden '
                                                                                                                                                                                                   'cubrir '
                                                                                                                                                                                                   'el '
                                                                                                                                                                                                   'fondo '
                                                                                                                                                                                                   'o '
                                                                                                                                                                                                   'cambiar '
                                                                                                                                                                                                   'su '
                                                                                                                                                                                                   'aspecto. '
                                                                                                                                                                                                   'Esto '
                                                                                                                                                                                                   'puede '
                                                                                                                                                                                                   'deberse '
                                                                                                                                                                                                   'al '
                                                                                                                                                                                                   'diseño '
                                                                                                                                                                                                   'de '
                                                                                                                                                                                                   'la '
                                                                                                                                                                                                   'tarjeta '
                                                                                                                                                                                                   'y '
                                                                                                                                                                                                   'no '
                                                                                                                                                                                                   'a '
                                                                                                                                                                                                   'un '
                                                                                                                                                                                                   'error '
                                                                                                                                                                                                   'de '
                                                                                                                                                                                                   'Smart Study.',
                                                                                                                                                                                             'ko': '일부 '
                                                                                                                                                                                                   '카드 '
                                                                                                                                                                                                   '템플릿은 '
                                                                                                                                                                                                   '자체 '
                                                                                                                                                                                                   '색상, '
                                                                                                                                                                                                   '이미지 '
                                                                                                                                                                                                   '또는 '
                                                                                                                                                                                                   '패널을 '
                                                                                                                                                                                                   '사용합니다. '
                                                                                                                                                                                                   '배경을 '
                                                                                                                                                                                                   '가리거나 '
                                                                                                                                                                                                   '모양을 '
                                                                                                                                                                                                   '바꿀 '
                                                                                                                                                                                                   '수 '
                                                                                                                                                                                                   '있습니다. '
                                                                                                                                                                                                   '이는 '
                                                                                                                                                                                                   'Smart Study '
                                                                                                                                                                                                   '오류가 '
                                                                                                                                                                                                   '아니라 '
                                                                                                                                                                                                   '카드 '
                                                                                                                                                                                                   '디자인 '
                                                                                                                                                                                                   '때문일 '
                                                                                                                                                                                                   '수 '
                                                                                                                                                                                                   '있습니다.',
                                                                                                                                                                                             'pt': 'Alguns '
                                                                                                                                                                                                   'modelos '
                                                                                                                                                                                                   'usam '
                                                                                                                                                                                                   'cores, '
                                                                                                                                                                                                   'imagens '
                                                                                                                                                                                                   'ou '
                                                                                                                                                                                                   'painéis '
                                                                                                                                                                                                   'próprios. '
                                                                                                                                                                                                   'Eles '
                                                                                                                                                                                                   'podem '
                                                                                                                                                                                                   'cobrir '
                                                                                                                                                                                                   'o '
                                                                                                                                                                                                   'fundo '
                                                                                                                                                                                                   'ou '
                                                                                                                                                                                                   'mudar '
                                                                                                                                                                                                   'sua '
                                                                                                                                                                                                   'aparência. '
                                                                                                                                                                                                   'Isso '
                                                                                                                                                                                                   'pode '
                                                                                                                                                                                                   'ser '
                                                                                                                                                                                                   'causado '
                                                                                                                                                                                                   'pelo '
                                                                                                                                                                                                   'design '
                                                                                                                                                                                                   'do '
                                                                                                                                                                                                   'cartão, '
                                                                                                                                                                                                   'e '
                                                                                                                                                                                                   'não '
                                                                                                                                                                                                   'por '
                                                                                                                                                                                                   'um '
                                                                                                                                                                                                   'erro '
                                                                                                                                                                                                   'do '
                                                                                                                                                                                                   'Smart Study.',
                                                                                                                                                                                             'fr': 'Certains '
                                                                                                                                                                                                   'modèles '
                                                                                                                                                                                                   'utilisent '
                                                                                                                                                                                                   'leurs '
                                                                                                                                                                                                   'propres '
                                                                                                                                                                                                   'couleurs, '
                                                                                                                                                                                                   'images '
                                                                                                                                                                                                   'ou '
                                                                                                                                                                                                   'panneaux. '
                                                                                                                                                                                                   'Ils '
                                                                                                                                                                                                   'peuvent '
                                                                                                                                                                                                   'masquer '
                                                                                                                                                                                                   'le '
                                                                                                                                                                                                   'fond '
                                                                                                                                                                                                   'ou '
                                                                                                                                                                                                   'modifier '
                                                                                                                                                                                                   'son '
                                                                                                                                                                                                   'apparence. '
                                                                                                                                                                                                   'Cela '
                                                                                                                                                                                                   'peut '
                                                                                                                                                                                                   'venir '
                                                                                                                                                                                                   'du '
                                                                                                                                                                                                   'modèle '
                                                                                                                                                                                                   'de '
                                                                                                                                                                                                   'carte '
                                                                                                                                                                                                   'plutôt '
                                                                                                                                                                                                   'que '
                                                                                                                                                                                                   'd’une '
                                                                                                                                                                                                   'erreur '
                                                                                                                                                                                                   'de '
                                                                                                                                                                                                   'Smart Study.',
                                                                                                                                                                                             'vi': 'Một '
                                                                                                                                                                                                   'số '
                                                                                                                                                                                                   'mẫu '
                                                                                                                                                                                                   'thẻ '
                                                                                                                                                                                                   'dùng '
                                                                                                                                                                                                   'màu, '
                                                                                                                                                                                                   'ảnh '
                                                                                                                                                                                                   'hoặc '
                                                                                                                                                                                                   'khung '
                                                                                                                                                                                                   'riêng. '
                                                                                                                                                                                                   'Chúng '
                                                                                                                                                                                                   'có '
                                                                                                                                                                                                   'thể '
                                                                                                                                                                                                   'che '
                                                                                                                                                                                                   'nền '
                                                                                                                                                                                                   'hoặc '
                                                                                                                                                                                                   'thay '
                                                                                                                                                                                                   'đổi '
                                                                                                                                                                                                   'cách '
                                                                                                                                                                                                   'hiển '
                                                                                                                                                                                                   'thị. '
                                                                                                                                                                                                   'Điều '
                                                                                                                                                                                                   'này '
                                                                                                                                                                                                   'có '
                                                                                                                                                                                                   'thể '
                                                                                                                                                                                                   'do '
                                                                                                                                                                                                   'thiết '
                                                                                                                                                                                                   'kế '
                                                                                                                                                                                                   'thẻ, '
                                                                                                                                                                                                   'không '
                                                                                                                                                                                                   'phải '
                                                                                                                                                                                                   'lỗi '
                                                                                                                                                                                                   'Smart Study.',
                                                                                                                                                                                             'zh': '部分卡片模板使用自己的颜色、图片或面板，可能遮住背景或改变显示效果。这可能源于卡片设计，而不一定是 '
                                                                                                                                                                                                   'Smart Study '
                                                                                                                                                                                                   '的错误。',
                                                                                                                                                                                             'hi': 'कुछ '
                                                                                                                                                                                                   'कार्ड '
                                                                                                                                                                                                   'टेम्पलेट '
                                                                                                                                                                                                   'अपने '
                                                                                                                                                                                                   'रंग, '
                                                                                                                                                                                                   'चित्र '
                                                                                                                                                                                                   'या '
                                                                                                                                                                                                   'पैनल '
                                                                                                                                                                                                   'इस्तेमाल '
                                                                                                                                                                                                   'करते '
                                                                                                                                                                                                   'हैं। '
                                                                                                                                                                                                   'वे '
                                                                                                                                                                                                   'पृष्ठभूमि '
                                                                                                                                                                                                   'ढक '
                                                                                                                                                                                                   'सकते '
                                                                                                                                                                                                   'हैं '
                                                                                                                                                                                                   'या '
                                                                                                                                                                                                   'उसका '
                                                                                                                                                                                                   'रूप '
                                                                                                                                                                                                   'बदल '
                                                                                                                                                                                                   'सकते '
                                                                                                                                                                                                   'हैं। '
                                                                                                                                                                                                   'यह '
                                                                                                                                                                                                   'Smart Study '
                                                                                                                                                                                                   'की '
                                                                                                                                                                                                   'त्रुटि '
                                                                                                                                                                                                   'के '
                                                                                                                                                                                                   'बजाय '
                                                                                                                                                                                                   'कार्ड '
                                                                                                                                                                                                   'के '
                                                                                                                                                                                                   'डिज़ाइन '
                                                                                                                                                                                                   'के '
                                                                                                                                                                                                   'कारण '
                                                                                                                                                                                                   'हो '
                                                                                                                                                                                                   'सकता '
                                                                                                                                                                                                   'है।'},
 'Start with a subtle background. If a card becomes harder to read, lower the intensity or turn this option off. Your cards are not modified.': {'de': 'Beginne '
                                                                                                                                                       'mit '
                                                                                                                                                       'einem '
                                                                                                                                                       'dezenten '
                                                                                                                                                       'Hintergrund. '
                                                                                                                                                       'Wenn '
                                                                                                                                                       'eine '
                                                                                                                                                       'Karte '
                                                                                                                                                       'schlechter '
                                                                                                                                                       'lesbar '
                                                                                                                                                       'wird, '
                                                                                                                                                       'reduziere '
                                                                                                                                                       'die '
                                                                                                                                                       'Intensität '
                                                                                                                                                       'oder '
                                                                                                                                                       'schalte '
                                                                                                                                                       'die '
                                                                                                                                                       'Option '
                                                                                                                                                       'aus. '
                                                                                                                                                       'Deine '
                                                                                                                                                       'Karten '
                                                                                                                                                       'werden '
                                                                                                                                                       'nicht '
                                                                                                                                                       'verändert.',
                                                                                                                                                 'es': 'Empieza '
                                                                                                                                                       'con '
                                                                                                                                                       'un '
                                                                                                                                                       'fondo '
                                                                                                                                                       'sutil. '
                                                                                                                                                       'Si '
                                                                                                                                                       'una '
                                                                                                                                                       'tarjeta '
                                                                                                                                                       'es '
                                                                                                                                                       'difícil '
                                                                                                                                                       'de '
                                                                                                                                                       'leer, '
                                                                                                                                                       'reduce '
                                                                                                                                                       'la '
                                                                                                                                                       'intensidad '
                                                                                                                                                       'o '
                                                                                                                                                       'desactiva '
                                                                                                                                                       'la '
                                                                                                                                                       'opción. '
                                                                                                                                                       'Tus '
                                                                                                                                                       'tarjetas '
                                                                                                                                                       'no '
                                                                                                                                                       'se '
                                                                                                                                                       'modifican.',
                                                                                                                                                 'ko': '은은한 '
                                                                                                                                                       '배경으로 '
                                                                                                                                                       '시작하세요. '
                                                                                                                                                       '카드가 '
                                                                                                                                                       '읽기 '
                                                                                                                                                       '어려워지면 '
                                                                                                                                                       '강도를 '
                                                                                                                                                       '낮추거나 '
                                                                                                                                                       '끄세요. '
                                                                                                                                                       '카드는 '
                                                                                                                                                       '수정되지 '
                                                                                                                                                       '않습니다.',
                                                                                                                                                 'pt': 'Comece '
                                                                                                                                                       'com '
                                                                                                                                                       'um '
                                                                                                                                                       'fundo '
                                                                                                                                                       'discreto. '
                                                                                                                                                       'Se '
                                                                                                                                                       'a '
                                                                                                                                                       'leitura '
                                                                                                                                                       'ficar '
                                                                                                                                                       'difícil, '
                                                                                                                                                       'reduza '
                                                                                                                                                       'a '
                                                                                                                                                       'intensidade '
                                                                                                                                                       'ou '
                                                                                                                                                       'desative '
                                                                                                                                                       'a '
                                                                                                                                                       'opção. '
                                                                                                                                                       'Seus '
                                                                                                                                                       'cartões '
                                                                                                                                                       'não '
                                                                                                                                                       'são '
                                                                                                                                                       'modificados.',
                                                                                                                                                 'fr': 'Commencez '
                                                                                                                                                       'par '
                                                                                                                                                       'un '
                                                                                                                                                       'fond '
                                                                                                                                                       'discret. '
                                                                                                                                                       'Si '
                                                                                                                                                       'une '
                                                                                                                                                       'carte '
                                                                                                                                                       'devient '
                                                                                                                                                       'difficile '
                                                                                                                                                       'à '
                                                                                                                                                       'lire, '
                                                                                                                                                       'réduisez '
                                                                                                                                                       'l’intensité '
                                                                                                                                                       'ou '
                                                                                                                                                       'désactivez '
                                                                                                                                                       'l’option. '
                                                                                                                                                       'Vos '
                                                                                                                                                       'cartes '
                                                                                                                                                       'ne '
                                                                                                                                                       'sont '
                                                                                                                                                       'pas '
                                                                                                                                                       'modifiées.',
                                                                                                                                                 'vi': 'Hãy '
                                                                                                                                                       'bắt '
                                                                                                                                                       'đầu '
                                                                                                                                                       'với '
                                                                                                                                                       'nền '
                                                                                                                                                       'nhẹ. '
                                                                                                                                                       'Nếu '
                                                                                                                                                       'thẻ '
                                                                                                                                                       'khó '
                                                                                                                                                       'đọc '
                                                                                                                                                       'hơn, '
                                                                                                                                                       'giảm '
                                                                                                                                                       'độ '
                                                                                                                                                       'đậm '
                                                                                                                                                       'hoặc '
                                                                                                                                                       'tắt '
                                                                                                                                                       'tùy '
                                                                                                                                                       'chọn. '
                                                                                                                                                       'Thẻ '
                                                                                                                                                       'của '
                                                                                                                                                       'bạn '
                                                                                                                                                       'không '
                                                                                                                                                       'bị '
                                                                                                                                                       'chỉnh '
                                                                                                                                                       'sửa.',
                                                                                                                                                 'zh': '建议从淡背景开始。如果卡片变得难以阅读，请降低强度或关闭此选项。你的卡片不会被修改。',
                                                                                                                                                 'hi': 'हल्की '
                                                                                                                                                       'पृष्ठभूमि '
                                                                                                                                                       'से '
                                                                                                                                                       'शुरू '
                                                                                                                                                       'करें। '
                                                                                                                                                       'यदि '
                                                                                                                                                       'कार्ड '
                                                                                                                                                       'पढ़ना '
                                                                                                                                                       'कठिन '
                                                                                                                                                       'हो, '
                                                                                                                                                       'तो '
                                                                                                                                                       'तीव्रता '
                                                                                                                                                       'घटाएँ '
                                                                                                                                                       'या '
                                                                                                                                                       'विकल्प '
                                                                                                                                                       'बंद '
                                                                                                                                                       'करें। '
                                                                                                                                                       'आपके '
                                                                                                                                                       'कार्ड '
                                                                                                                                                       'बदले '
                                                                                                                                                       'नहीं '
                                                                                                                                                       'जाते।'},
 'Enable': {'de': 'Aktivieren',
            'es': 'Activar',
            'ko': '활성화',
            'pt': 'Ativar',
            'fr': 'Activer',
            'vi': 'Bật',
            'zh': '启用',
            'hi': 'सक्षम करें'}})

TRANSLATIONS["Edit Dashboard Surfaces"] = {"de":"Dashboard-Flächen bearbeiten","es":"Editar superficies del panel","ko":"대시보드 표면 편집","pt":"Editar superfícies do painel","fr":"Modifier les surfaces du tableau de bord","vi":"Chỉnh sửa bề mặt bảng điều khiển","zh":"编辑仪表盘表面","hi":"डैशबोर्ड सतहें संपादित करें"}



# Deck Overview title color preferences.
TRANSLATIONS.update({
    "Deck name color": {"de":"Farbe des Decknamens", "es":"Color del nombre del mazo", "fr":"Couleur du nom du paquet", "pt":"Cor do nome do baralho", "ko":"덱 이름 색상", "vi":"Màu tên bộ thẻ", "zh":"牌组名称颜色", "hi":"डेक के नाम का रंग"},
    "Use primary color": {"de":"Primärfarbe verwenden", "es":"Usar color principal", "fr":"Utiliser la couleur principale", "pt":"Usar cor principal", "ko":"기본 색상 사용", "vi":"Dùng màu chủ đạo", "zh":"使用主题色", "hi":"प्राथमिक रंग का उपयोग करें"},
    "Custom color": {"de":"Eigene Farbe", "es":"Color personalizado", "fr":"Couleur personnalisée", "pt":"Cor personalizada", "ko":"사용자 지정 색상", "vi":"Màu tùy chỉnh", "zh":"自定义颜色", "hi":"कस्टम रंग"},
    "Custom deck name color": {"de":"Eigene Farbe für den Decknamen", "es":"Color personalizado del nombre del mazo", "fr":"Couleur personnalisée du nom du paquet", "pt":"Cor personalizada do nome do baralho", "ko":"덱 이름 사용자 지정 색상", "vi":"Màu tùy chỉnh cho tên bộ thẻ", "zh":"自定义牌组名称颜色", "hi":"डेक के नाम का कस्टम रंग"},
})

# Smart Study 2.8.2: browser layout and saved passwords
TRANSLATIONS.update({
    "Split view": {"de": "Geteilte Ansicht"},
    "Layout": {"de": "Ansicht"},
    "Smooth scrolling": {"de": "Flüssiges Scrollen"},
    "After a quick swipe on the touchpad, pages in the browser keep gliding and slow down.": {"de": "Nach einem schnellen Wischen auf dem Touchpad gleiten Seiten im Browser weiter und werden langsamer."},
    "Split view (cards | browser)": {"de": "Geteilt (Karten | Browser)"},
    "Main window": {"de": "Hauptfenster"},
    "Own window": {"de": "Eigenes Fenster"},
    "Browser layout": {"de": "Browser-Ansicht"},
    "Save password?": {"de": "Passwort speichern?"},
    "Update the saved password for {}?": {"de": "Gespeichertes Passwort für {} aktualisieren?"},
    "Save the password for {}?": {"de": "Passwort für {} speichern?"},
    "User name: {}": {"de": "Benutzername: {}"},
    "It is stored in your system keyring (e.g. KWallet, GNOME Keyring, macOS Keychain, Windows Credential Manager). Next time the login page is filled in for you – you only click “Log in”.": {"de": "Es wird im Passwortspeicher deines Systems abgelegt (z. B. KWallet, GNOME Keyring, macOS-Schlüsselbund, Windows-Anmeldeinformationsverwaltung). Beim nächsten Mal wird die Anmeldeseite für dich ausgefüllt – du klickst nur noch auf „Anmelden“."},
    "Never for this site": {"de": "Nie für diese Seite"},
    "Could not save the password (system keyring not reachable).": {"de": "Passwort konnte nicht gespeichert werden (Passwortspeicher des Systems nicht erreichbar)."},
    "Save and fill in passwords": {"de": "Passwörter speichern und ausfüllen"},
    "Needs a system keyring (on Linux: secret-tool with KWallet, GNOME Keyring or KeePassXC).": {"de": "Braucht einen Passwortspeicher des Systems (unter Linux: secret-tool mit KWallet, GNOME Keyring oder KeePassXC)."},
    "Delete saved passwords…": {"de": "Gespeicherte Passwörter löschen…"},
    "Delete all passwords saved by the Smart Study browser?": {"de": "Alle vom Smart-Study-Browser gespeicherten Passwörter löschen?"},
})

# Side panel (Smart Study's own look)
TRANSLATIONS.update({
    "Assistant": {"de": "Assistent"},
    "New in": {"de": "Neu in"},
    "What changed in this version, and things worth knowing.": {"de": "Was sich in dieser Version geändert hat und was du wissen solltest."},
    "Show or hide the side panel": {"de": "Seitenleiste ein- oder ausblenden"},
    "Side panel": {"de": "Seitenleiste"},
    "Search settings": {"de": "Einstellungen durchsuchen"},
    "No setting matches your search.": {"de": "Keine Einstellung passt zu deiner Suche."},
    "What Smart Study shows next to your decks. The deck list itself always stays.": {"de": "Was Smart Study neben deinen Stapeln zeigt. Die Stapelliste selbst bleibt immer."},
    "Side panel on the right, or the classic widgets above the deck list. Applies after restarting Anki.": {"de": "Seitenleiste rechts oder die klassischen Kästen über der Stapelliste. Gilt nach einem Neustart von Anki."},
    "Today panel": {"de": "Heute-Seite"},
    "The first tab of the side panel.": {"de": "Der erste Reiter der Seitenleiste."},
    "The three charts under the plan. Each one has its own period.": {"de": "Die drei Diagramme unter dem Plan. Jedes hat seinen eigenen Zeitraum."},
    "Classic widgets": {"de": "Klassische Kästen"},
    "Countdown to the next exam": {"de": "Countdown zur nächsten Prüfung"},
    "Days left, taken from your study plan.": {"de": "Verbleibende Tage, aus deinem Lernplan."},
    "Tick off plan items without opening the study plan.": {"de": "Plan-Punkte abhaken, ohne den Lernplan zu öffnen."},
    "Small, next to the countdown.": {"de": "Klein, neben dem Countdown."},
    "Your goal for today with its progress.": {"de": "Dein Ziel für heute mit Fortschritt."},
    "One short fact per day under the plan.": {"de": "Ein kurzer Fakt pro Tag unter dem Plan."},
    "Cards coming up, one bar per day.": {"de": "Anstehende Karten, ein Balken pro Tag."},
    "Cards you answered per day.": {"de": "Beantwortete Karten pro Tag."},
    "Share you remembered, and share of cards still unseen.": {"de": "Anteil gewusst und Anteil noch ungesehener Karten."},
    "The tabs of the side panel, the timer and the music player.": {"de": "Die Reiter der Seitenleiste, der Timer und der Musikplayer."},
    "3 items": {"de": "3 Punkte"},
    "4 items": {"de": "4 Punkte"},
    "5 items": {"de": "5 Punkte"},
    "6 items": {"de": "6 Punkte"},
    "8 items": {"de": "8 Punkte"},
    "Next 7 days": {"de": "Nächste 7 Tage"},
    "Next 14 days": {"de": "Nächste 14 Tage"},
    "Next 30 days": {"de": "Nächste 30 Tage"},
    "Last 90 Days": {"de": "Letzte 90 Tage"},
    "last 24 hours": {"de": "letzte 24 Stunden"},
    "Petrol": {"de": "Petrol"},
    "Trophies": {"de": "Trophäen"},
    "Smart Study settings": {"de": "Smart-Study-Einstellungen"},
    "Pomodoro: reset, skip, settings": {"de": "Pomodoro: zurücksetzen, überspringen, Einstellungen"},
    "Show or hide the Smart Study panel.": {"de": "Smart-Study-Leiste ein- oder ausblenden."},
    "Break": {"de": "Pause"},
    "days until": {"de": "Tage bis"},
    "day until": {"de": "Tag bis"},
    "day streak": {"de": "Tage in Folge"},
    "done": {"de": "erledigt"},
    "of": {"de": "von"},
    "left": {"de": "übrig"},
    "about": {"de": "etwa"},
    "more, open plan": {"de": "weitere, Plan öffnen"},
    "Open study plan": {"de": "Lernplan öffnen"},
    "No study plan yet": {"de": "Noch kein Lernplan"},
    "Create a plan and today's items appear here.": {"de": "Lege einen Plan an, dann stehen hier die Punkte für heute."},
    "Nothing planned for today.": {"de": "Für heute ist nichts geplant."},
    "Everything for today is done.": {"de": "Für heute ist alles erledigt."},
    "Memory": {"de": "Gedächtnis"},
    "next {} days": {"de": "nächste {} Tage"},
    "last {} days": {"de": "letzte {} Tage"},
    "last year": {"de": "letztes Jahr"},
    "today": {"de": "heute"},
    "remembered": {"de": "gewusst"},
    "still unseen": {"de": "noch ungesehen"},
    "Daily challenge": {"de": "Tages-Challenge"},
    "Claim": {"de": "Abholen"},
    "Choose what this page shows": {"de": "Auswählen, was diese Seite zeigt"},
    "What do these numbers mean?": {"de": "Was bedeuten diese Zahlen?"},
    "Anki checks this off.": {"de": "Das hakt Anki ab."},
    "Study": {"de": "Lernen"},
    "Exam today": {"de": "Prüfung heute"},
    "Countdown": {"de": "Countdown"},
    "Today's plan": {"de": "Plan für heute"},
    "Level and streak": {"de": "Level und Serie"},
    "All settings": {"de": "Alle Einstellungen"},
    "Due: reviews that are waiting today or become due on each of the next days. New cards are not counted.": {"de": "Fällig: Wiederholungen, die heute warten oder an den nächsten Tagen fällig werden. Neue Karten zählen nicht mit."},
    "Reviews: how many cards you answered per day.": {"de": "Wiederholungen: wie viele Karten du pro Tag beantwortet hast."},
    "Remembered: share of review cards you answered correctly. Still unseen: share of your cards you have never studied.": {"de": "Gewusst: Anteil der Wiederholungskarten, die du richtig hattest. Noch ungesehen: Anteil deiner Karten, die du noch nie gelernt hast."},
    "No reviews in this period.": {"de": "Keine Wiederholungen in diesem Zeitraum."},
    "cards": {"de": "Karten"},
    "No matching cards (left).": {"de": "Keine passenden Karten (mehr) gefunden."},
})

# retired_tools.py – notice after the notebook and the mind map were removed (3.1)
TRANSLATIONS.update({
    "This PDF link belonged to the notebook, which was removed in Smart Study 3.1.": {"de": "Dieser PDF-Link gehörte zum Notizbuch, das in Smart Study 3.1 entfernt wurde."},
    "The notebook (notes, to-dos, PDFs) and the mind map were removed in Smart Study 3.1.\n\nYour data was not deleted. It is still here:\n\n{}\n\nTo keep using these tools, install Smart Study 3.0.5 again from:\n{}": {"de": "Das Notizbuch (Notizen, To-dos, PDFs) und die Mindmap wurden in Smart Study 3.1 entfernt.\n\nDeine Daten wurden nicht gelöscht. Sie liegen weiterhin hier:\n\n{}\n\nUm diese Werkzeuge weiter zu nutzen, installiere Smart Study 3.0.5 erneut von:\n{}"},
    "Notebook and mind map were removed": {"de": "Notizbuch und Mindmap wurden entfernt"},
    "Notes, to-dos and linked PDFs": {"de": "Notizen, To-dos und verknüpfte PDFs"},
    "Mind maps": {"de": "Mindmaps"},
    "Free maps": {"de": "Free Maps"},
})


def translate_standard_buttons(button_box):
    """Use the add-on language for its own Qt button boxes, not the OS locale."""
    from aqt.qt import QDialogButtonBox
    labels = {'Ok': 'OK', 'Save': 'Save', 'Open': 'Open', 'Cancel': 'Cancel',
              'Close': 'Close', 'Apply': 'Apply', 'Reset': 'Reset', 'Help': 'Help',
              'RestoreDefaults': 'Restore Defaults', 'Yes': 'Yes', 'No': 'No',
              'Discard': 'Discard'}
    for name, source in labels.items():
        button = button_box.button(getattr(QDialogButtonBox.StandardButton, name))
        if button is not None:
            button.setText(_(source))
