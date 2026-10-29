# -*- coding: utf-8 -*-
"""Translations for the built-in add-ons, the update notes and the new web modes.

Keys are the English texts.  Missing languages fall back to Smart Study's
catalogue and then to English.
"""
from __future__ import annotations

from typing import Dict

try:
    from ..locales import _ as _smartstudy, _current_lang
except ImportError:  # outside Anki
    def _smartstudy(text: str) -> str:
        return text

    def _current_lang() -> str:
        return "en"


DE: Dict[str, str] = {
    "Copy selections with pictures as an image": "Auswahl mit Bildern als Bild kopieren",
    "When you select part of a card that contains pictures (with the mouse, Ctrl+A or Shift+arrows), the selection is copied as one image. Paste it into ChatGPT, Claude or a chat with Ctrl+V and the pictures come along – pasting normally only keeps the text. Selections without pictures are not changed.": "Wenn du einen Teil einer Karte mit Bildern markierst (mit der Maus, Strg+A oder Umschalt+Pfeiltasten), wird die Auswahl als ein Bild kopiert. Mit Strg+V in ChatGPT, Claude oder einen Chat einfügen – die Bilder kommen mit, beim normalen Einfügen bleibt nur der Text. Auswahlen ohne Bilder bleiben unverändert.",
    "Review heatmap": "Lern-Heatmap",
    "A calendar of your reviews with your streak on the deck list, the deck overview and the statistics.": "Ein Kalender deiner Wiederholungen mit Serie in der Stapelübersicht, der Stapelansicht und den Statistiken.",
    "Progress bar": "Fortschrittsleiste",
    "A bar at the top of the reviewer that shows how much of today's reviews is done.": "Eine Leiste oben beim Lernen, die zeigt, wie viel von den heutigen Karten geschafft ist.",
    "Controller support": "Controller-Steuerung",
    "Study with a gamepad, e.g. the 8BitDo Zero 2. Buttons can be set for every screen. If a controller cannot be recognised reliably, you are asked once which one it is.": "Lernen mit einem Gamepad, z. B. dem 8BitDo Zero 2. Die Tasten lassen sich für jeden Bildschirm belegen. Kann ein Controller nicht sicher erkannt werden, wirst du einmal gefragt, welcher es ist.",
    "Life Drain": "Life Drain",
    "A life bar that drains while you think about a card and refills when you answer – keeps you from lingering on one card.": "Ein Lebensbalken, der beim Nachdenken über eine Karte abläuft und sich beim Antworten wieder füllt – damit du nicht an einer Karte hängen bleibst.",
    "The change takes effect after restarting Anki. Close Anki now?": "Die Änderung wirkt nach einem Neustart von Anki. Anki jetzt schließen?",
    "Built-in add-ons": "Eingebaute Add-ons",
    "Smart Study includes these add-ons, so you do not have to install them separately. Switch off what you do not need. Changes take effect after restarting Anki.": "Smart Study enthält diese Add-ons, du musst sie nicht extra installieren. Schalte aus, was du nicht brauchst. Änderungen wirken nach einem Neustart von Anki.",
    "Options…": "Optionen…",
    "A separately installed copy is active, so the built-in one stays off. You can turn it off under Tools → Add-ons.": "Eine separat installierte Version ist aktiv, deshalb bleibt die eingebaute aus. Du kannst sie unter Extras → Erweiterungen deaktivieren.",
    "Could not be started. Details are in the Anki console.": "Konnte nicht gestartet werden. Details stehen in der Anki-Konsole.",
    "Forget which controller I picked": "Gewählten Controller vergessen",
    "Done. You will be asked again when the controller connects.": "Erledigt. Beim nächsten Verbinden wirst du wieder gefragt.",
    "Add-ons already installed": "Add-ons bereits installiert",
    "Smart Study now includes these add-ons. You also have them installed separately. Only one copy can run – which one do you want?": "Smart Study enthält jetzt diese Add-ons. Du hast sie zusätzlich separat installiert. Es kann nur eine Version laufen – welche möchtest du?",
    "Use the version built into Smart Study (recommended) – your separate add-on is switched off": "Die in Smart Study eingebaute Version nutzen (empfohlen) – dein separates Add-on wird deaktiviert",
    "Keep my separate add-on – the built-in version stays off": "Mein separates Add-on behalten – die eingebaute Version bleibt aus",
    "Your settings are kept either way. You can change this later under Tools → Smart Study → Built-in add-ons.": "Deine Einstellungen bleiben in beiden Fällen erhalten. Du kannst das später unter Extras → Smart Study → Eingebaute Add-ons ändern.",
    "Copied as image – paste it with {keys}.": "Als Bild kopiert – mit {keys} einfügen.",
    "8BitDo Zero 2": "8BitDo Zero 2",
    "Something else (keep automatic detection)": "Etwas anderes (automatische Erkennung behalten)",
    "Which controller is this?": "Welcher Controller ist das?",
    "Your controller reports itself as\n{id}\n\nMany controllers use this name, so it cannot be recognised reliably. Which one is it?": "Dein Controller meldet sich als\n{id}\n\nDiesen Namen verwenden viele Controller, deshalb kann er nicht sicher erkannt werden. Welcher ist es?",
    "Open in browser": "Im Browser öffnen",
    "Spotify only plays in its own app or a normal browser: its web player needs a copy protection (Widevine) that Anki's built-in browser does not include. Start your music there – it keeps playing while you study.": "Spotify spielt nur in der eigenen App oder in einem normalen Browser: Der Web-Player braucht einen Kopierschutz (Widevine), den Ankis eingebauter Browser nicht hat. Starte deine Musik dort – sie läuft weiter, während du lernst.",
    "Open the Spotify app": "Spotify-App öffnen",
    "Open Spotify in the browser": "Spotify im Browser öffnen",
    "YouTube Music plays here without signing in. Google does not allow signing in inside apps like Anki – for your own playlists, open YouTube Music in your browser with ↗.": "YouTube Music spielt hier ohne Anmeldung. Google erlaubt keine Anmeldung in Apps wie Anki – für deine eigenen Playlists öffne YouTube Music mit ↗ im Browser.",
    "Music": "Musik",
    "What's new in Smart Study": "Neu in Smart Study",
    "Smart Study was updated. Here is what changed – where something new was switched on, you can keep it or switch it off right here.": "Smart Study wurde aktualisiert. Das hat sich geändert – wo etwas Neues eingeschaltet wurde, kannst du es hier gleich behalten oder ausschalten.",
    "Keep switched on": "Eingeschaltet lassen",
    "Switch on": "Einschalten",
    "API chat": "API-Chat",
    "Sign in with your own account – no API key needed. Use your e-mail address: Google does not allow “Sign in with Google” inside apps like Anki. Gemini also works without signing in.": "Mit deinem eigenen Account anmelden – kein API-Schlüssel nötig. Nutze deine E-Mail-Adresse: Google erlaubt „Mit Google anmelden“ nicht in Apps wie Anki. Gemini funktioniert auch ohne Anmeldung.",
    "Streaming": "Streaming",
    "YouTube Music or Spotify": "YouTube Music oder Spotify",
    "Built-in add-ons: you no longer need to install them separately. Switch them on or off under Tools → Smart Study → Built-in add-ons.": "Eingebaute Add-ons: Du musst sie nicht mehr extra installieren. Ein- und ausschalten unter Extras → Smart Study → Eingebaute Add-ons.",
    "Copy selections with pictures as an image – paste card pictures into ChatGPT or Claude.": "Auswahl mit Bildern als Bild kopieren – Kartenbilder in ChatGPT oder Claude einfügen.",
    "Review heatmap on the deck list (based on Review Heatmap by Glutanimate).": "Lern-Heatmap in der Stapelübersicht (basiert auf Review Heatmap von Glutanimate).",
    "Progress bar in the reviewer (based on Progress bar by Shigeyuki).": "Fortschrittsleiste beim Lernen (basiert auf Progress bar von Shigeyuki).",
    "Controller support (based on Contanki), with better detection: if a controller such as the 8BitDo Zero 2 cannot be recognised reliably, you are asked once which one it is.": "Controller-Steuerung (basiert auf Contanki) mit besserer Erkennung: Kann ein Controller wie der 8BitDo Zero 2 nicht sicher erkannt werden, wirst du einmal gefragt, welcher es ist.",
    "Life Drain (based on Life Drain by Yutsuten) – off by default.": "Life Drain (basiert auf Life Drain von Yutsuten) – standardmäßig aus.",
    "AI assistant: use ChatGPT, Claude or Gemini with your own account, without an API key.": "KI-Assistent: ChatGPT, Claude oder Gemini mit deinem eigenen Account nutzen, ohne API-Schlüssel.",
    "Music: YouTube Music in a sidebar; Spotify opens in its app.": "Musik: YouTube Music in einer Seitenleiste; Spotify öffnet sich in der App.",
    "The website sidebar no longer crashes Anki when you search.": "Die Website-Seitenleiste lässt Anki beim Suchen nicht mehr abstürzen.",
    "New": "Neu",
    "Fix": "Behoben",
    "Changed": "Geändert",
    "Highlight": "Highlight",
}


def tr(text: str) -> str:
    if _current_lang() == "de" and text in DE:
        return DE[text]
    return _smartstudy(text)
