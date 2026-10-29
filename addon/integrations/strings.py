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
    "Review heatmap": "Lern-Heatmap",
    "Progress bar": "Fortschrittsleiste",
    "Controller support": "Controller-Steuerung",
    "Life Drain": "Life Drain",
    "Built-in add-ons": "Eingebaute Add-ons",
    "Options…": "Optionen…",
    "Forget which controller I picked": "Gewählten Controller vergessen",
    "Done. You will be asked again when the controller connects.": "Erledigt. Beim nächsten Verbinden wirst du wieder gefragt.",
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
    "The windows for built-in add-ons, already installed add-ons and updates have the Smart Study look: clear groups, switches and short texts. Separately installed copies can be deleted right there (“Take over & delete old ones”).": "Die Fenster für eingebaute Add-ons, bereits installierte Add-ons und Updates haben jetzt den Smart-Study-Look: klare Gruppen, Schalter und kurze Texte. Separat installierte Versionen lassen sich dort direkt löschen („Übernehmen & alte löschen“).",
    "New": "Neu",
    "Fix": "Behoben",
    "Changed": "Geändert",
    "Highlight": "Highlight",
    "Select part of a card with pictures – it is copied as one image, so ChatGPT or Claude get the pictures when you paste.": "Markiere einen Teil einer Karte mit Bildern – er wird als ein Bild kopiert, so kommen die Bilder beim Einfügen in ChatGPT oder Claude mit.",
    "Your reviews and streak as a calendar on the deck list.": "Deine Wiederholungen und Serie als Kalender in der Stapelübersicht.",
    "Shows how much of today's reviews is done.": "Zeigt, wie viel von den heutigen Karten geschafft ist.",
    "Study with a gamepad, e.g. the 8BitDo Zero 2.": "Lernen mit Gamepad, z. B. dem 8BitDo Zero 2.",
    "A life bar that drains while you think about a card.": "Ein Lebensbalken, der beim Nachdenken über eine Karte abläuft.",
    "Included in Smart Study – no separate installs. Changes apply after restarting Anki.": "In Smart Study enthalten – keine separaten Installationen. Änderungen gelten nach einem Neustart von Anki.",
    "Your separately installed copy is active.": "Deine separat installierte Version ist aktiv.",
    "Could not be started.": "Konnte nicht gestartet werden.",
    "Credits": "Credits",
    "Cancel": "Abbrechen",
    "Save": "Speichern",
    "Already installed": "Bereits installiert",
    "Smart Study now includes these add-ons. Only one copy can run – keep the built-in one or yours?": "Smart Study enthält jetzt diese Add-ons. Es kann nur eine Version laufen – eingebaute nutzen oder deine behalten?",
    "Built-in": "Eingebaut",
    "Keep mine": "Meins behalten",
    "Restart Anki": "Anki neu starten",
    "The change takes effect after restarting Anki.": "Die Änderung wirkt nach einem Neustart von Anki.",
    "Later": "Später",
    "Close Anki now": "Anki jetzt schließen",
    "What's new in Smart Study {version}": "Neu in Smart Study {version}",
    "Keep what you like – everything with a switch can be turned off right here.": "Behalte, was dir gefällt – alles mit Schalter kannst du hier direkt ausschalten.",
    "Also new": "Außerdem neu",
    "Done": "Fertig",
    "Your settings are taken over. “Take over” switches your separate add-ons off, “Take over & delete old ones” moves them to the trash. Change it any time under Tools → Smart Study → Built-in add-ons.": "Deine Einstellungen werden übernommen. „Übernehmen“ deaktiviert deine separaten Add-ons, „Übernehmen & alte löschen“ verschiebt sie in den Papierkorb. Jederzeit änderbar unter Extras → Smart Study → Eingebaute Add-ons.",
    "Take over": "Übernehmen",
    "Take over & delete old ones": "Übernehmen & alte löschen",
}


def tr(text: str) -> str:
    if _current_lang() == "de" and text in DE:
        return DE[text]
    return _smartstudy(text)
