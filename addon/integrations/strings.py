# -*- coding: utf-8 -*-
"""Translations for the built-in add-ons, the update notes and the new web modes.

Keys are the English texts.  Missing languages fall back to Smart Study's
catalogue and then to English.  ``FA`` also holds the Persian for the text inside
the bundled add-ons, reached through ``fa_tr`` and ``translate_widgets``.
"""
from __future__ import annotations

import re
from typing import Dict, Iterable

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
    "Add-ons": "Add-ons",
    "Same add-ons on all your devices: your AnkiWeb add-ons sync with AnkiWeb, and other devices offer to install what is missing.": "Gleiche Add-ons auf all deinen Geräten: Deine AnkiWeb-Add-ons synchronisieren sich per AnkiWeb, und andere Geräte bieten an, Fehlendes zu installieren.",
    "Settings → Add-ons: install an add-on by entering its AnkiWeb code.": "Einstellungen → Add-ons: ein Add-on über seinen AnkiWeb-Code installieren.",
    "New color Orange and the Orange Pixel Wallpaper with a little pixel buddy.": "Neue Farbe Orange und das Orange-Pixel-Wallpaper mit kleinem Pixel-Freund.",
    "The old “Study Plan” decks are now called “Smart Study system data”.": "Die alten „Study Plan“-Decks heißen jetzt „Smart Study system data“.",
    "Sync your add-ons?": "Add-ons synchronisieren?",
    "Smart Study can keep the same AnkiWeb add-ons on all your devices. Your add-on list then travels with the normal AnkiWeb sync, and on your other devices Smart Study offers to install what is missing.": "Smart Study kann auf all deinen Geräten dieselben AnkiWeb-Add-ons bereithalten. Deine Add-on-Liste reist dann mit dem normalen AnkiWeb-Sync mit, und auf deinen anderen Geräten bietet Smart Study an, Fehlendes zu installieren.",
    "You can change this any time under Settings → Add-ons.": "Das kannst du jederzeit unter Einstellungen → Add-ons ändern.",
    "No thanks": "Nein danke",
    "Sync add-ons": "Add-ons synchronisieren",
    "Add-ons from your other devices": "Add-ons von deinen anderen Geräten",
    "These add-ons are installed on another device. Install them here too?": "Diese Add-ons sind auf einem anderen Gerät installiert. Auch hier installieren?",
    "Code {code}": "Code {code}",
    "Switched off add-ons are not offered again on this device.": "Ausgeschaltete Add-ons werden auf diesem Gerät nicht mehr angeboten.",
    "Not now": "Jetzt nicht",
    "Don't ask again": "Nicht mehr fragen",
    "Switched off add-ons are not offered again on this device. “Don't ask again” turns add-on sync off here; turn it back on under Settings → Add-ons.": "Ausgeschaltete Add-ons werden auf diesem Gerät nicht mehr angeboten. „Nicht mehr fragen“ schaltet den Add-on-Sync hier aus; wieder einschalten unter Einstellungen → Add-ons.",
    "Install": "Installieren",
    "Same add-ons on all devices": "Gleiche Add-ons auf allen Geräten",
    "Your AnkiWeb add-ons travel with the AnkiWeb sync; other devices offer to install what is missing.": "Deine AnkiWeb-Add-ons reisen mit dem AnkiWeb-Sync mit; andere Geräte bieten an, Fehlendes zu installieren.",
    "Install an add-on": "Add-on installieren",
    "Enter the code from the add-on's AnkiWeb page.": "Gib den Code von der AnkiWeb-Seite des Add-ons ein.",
    "Code": "Code",
    "Installed": "Installiert",
    "Not on this device": "Nicht auf diesem Gerät",
    "New add-ons work after restarting Anki.": "Neue Add-ons funktionieren nach einem Neustart von Anki.",
    "Faster dashboard, deck overview and review heatmap.": "Schnelleres Dashboard, schnellere Deck-Übersicht und Lern-Heatmap.",
    "Fixes for the review heatmap, controller support, Life Drain and copying selections with pictures.": "Fehlerbehebungen für Lern-Heatmap, Controller-Steuerung, Life Drain und das Kopieren von Auswahlen mit Bildern.",
    "Your Smart Study settings and the switches for the built-in add-ons now sync to your other devices with AnkiWeb.": "Deine Smart-Study-Einstellungen und die Schalter der eingebauten Add-ons werden jetzt per AnkiWeb mit deinen anderen Geräten synchronisiert.",
    "Settings → Add-ons: switch each built-in add-on on or off at any time.": "Einstellungen → Add-ons: jedes eingebaute Add-on jederzeit an- oder ausschalten.",
    "The built-in progress bar was removed. Install Progress bar from AnkiWeb if you want it back.": "Die eingebaute Fortschrittsleiste wurde entfernt. Wer sie zurückhaben möchte, installiert Progress bar von AnkiWeb.",
    "Options & credits…": "Optionen & Credits…",
    "Your choice syncs to your other devices with AnkiWeb.": "Deine Auswahl wird per AnkiWeb mit deinen anderen Geräten synchronisiert.",
    "Built-in add-ons were changed on another device. Restart Anki to apply.": "Eingebaute Add-ons wurden auf einem anderen Gerät geändert. Starte Anki neu, damit es wirkt.",
    "Settings updated from your other device.": "Einstellungen von deinem anderen Gerät übernommen.",
    "Persian (فارسی): all of Smart Study in Persian, with a right-to-left layout.": "Persisch (فارسی): ganz Smart Study auf Persisch, mit Layout von rechts nach links.",
    "Anki itself in Persian: Smart Study repairs Anki's Persian translation, which otherwise shows English.": "Anki selbst auf Persisch: Smart Study repariert Ankis persische Übersetzung, die sonst Englisch anzeigt.",
    "The AI assistant can answer in Persian.": "Der KI-Assistent kann auf Persisch antworten.",
    "Copying a selection with pictures: the text is in the image again when Anki is in night mode (it was white on white).": "Auswahl mit Bildern kopieren: Im Nachtmodus ist der Text wieder im Bild (er war weiß auf weiß).",
}


FA: Dict[str, str] = {
    # Life Drain
    "Life Drain Global Settings (v{version})": "تنظیمات سراسری Life Drain (نسخهٔ {version})",
    "Life Drain Deck Settings for {name}": "تنظیمات Life Drain برای {name}",
    "Basic": "پایه",
    "Bar Style": "ظاهر نوار",
    "Deck Defaults": "پیش‌فرض‌های دسته",
    "Damage": "آسیب",
    "Select": "انتخاب",
    "Recover": "بازیابی",
    "Enable Life Drain": "فعال کردن Life Drain",
    "Enable/disable the add-on without restarting Anki.": "افزونه را بدون راه‌اندازی دوبارهٔ Anki روشن یا خاموش می‌کند.",
    "Stop drain on answer shown": "توقف کاهش جان هنگام نمایش پاسخ",
    "Automatically stops the drain after answering a card.": "پس از پاسخ دادن به کارت، کاهش جان را خودکار متوقف می‌کند.",
    "Stop drain while edititing or browsing": "توقف کاهش جان هنگام ویرایش یا مرور فهرست کارت‌ها",
    "Automatically stops the drain when opening the editor or browser.\nMay not resume the drain automatically when closing it.": "با باز شدن ویرایشگر یا مرورگر کارت‌ها، کاهش جان خودکار متوقف می‌شود.\nممکن است پس از بستن آن‌ها خودکار ادامه پیدا نکند.",
    "Default initial life is 0": "جان اولیهٔ پیش‌فرض 0 باشد",
    "Life will begin at 0 instead of full. Also affects Recover.": "جان به جای پر بودن از 0 شروع می‌شود. بر بازیابی هم اثر دارد.",
    "<b>Special action behavior</b>": "<b>رفتار در عملیات خاص</b>",
    "Delete": "حذف",
    "How should the program behave when deleting a card/note?": "هنگام حذف کارت یا یادداشت، برنامه چگونه رفتار کند؟",
    "Bury": "دفن کردن",
    "How should the program behave when burying a card/note?": "هنگام دفن کردن کارت یا یادداشت، برنامه چگونه رفتار کند؟",
    "Suspend": "تعلیق",
    "How should the program behave when suspending a card/note?": "هنگام تعلیق کارت یا یادداشت، برنامه چگونه رفتار کند؟",
    "<b>Shortcuts</b>": "<b>میانبرها</b>",
    "\nThere is no validation for your shortcut string, so edit with care!\nInvalid shortcuts, or already used shortcuts won't work.": "\nمیانبر واردشده بررسی نمی‌شود، پس با دقت ویرایش کنید!\nمیانبرهای نامعتبر یا تکراری کار نمی‌کنند.",
    "Global Settings": "تنظیمات سراسری",
    "Shortcut for the Global Settings.": "میانبر تنظیمات سراسری.",
    "Deck Settings": "تنظیمات دسته",
    "Shortcut for the Deck Settings.": "میانبر تنظیمات دسته.",
    "Pause": "مکث",
    "Shortcut for pausing.": "میانبر مکث.",
    "Shortcut for recovering.": "میانبر بازیابی.",
    "Invert bar movement": "وارونه کردن حرکت نوار",
    "Reduce life from left to right instead of right to left.": "جان را به جای راست به چپ، از چپ به راست کم می‌کند.",
    "Position": "موقعیت",
    "Place to show the life bar.": "محل نمایش نوار جان.",
    "Height": "ارتفاع",
    "Height of the life bar.": "ارتفاع نوار جان.",
    "Border radius": "گردی لبه‌ها",
    "Add a rounded border to the life bar.": "به نوار جان لبهٔ گرد می‌دهد.",
    "Default": "پیش‌فرض",
    "Style": "سبک",
    "Style of the life bar. Custom styles coloring may only work after a restart.": "سبک نوار جان. رنگ‌های سبک‌های سفارشی شاید فقط پس از راه‌اندازی دوباره اعمال شوند.",
    "Bar color (default)": "رنگ نوار (پیش‌فرض)",
    "Color of the life bar's foreground.": "رنگ پیش‌زمینهٔ نوار جان.",
    "Warn threshold (%)": "آستانهٔ هشدار (%)",
    "Threshold % to show the life bar with the warn color.": "درصدی که از آن به بعد نوار جان با رنگ هشدار نمایش داده می‌شود.",
    "Bar color (warn)": "رنگ نوار (هشدار)",
    "Color of the life bar's foreground (warn).": "رنگ پیش‌زمینهٔ نوار جان (هشدار).",
    "Danger threshold (%)": "آستانهٔ خطر (%)",
    "Threshold % to show the life bar with the danger color.": "درصدی که از آن به بعد نوار جان با رنگ خطر نمایش داده می‌شود.",
    "Bar color (danger)": "رنگ نوار (خطر)",
    "Color of the life bar's foreground (danger).": "رنگ پیش‌زمینهٔ نوار جان (خطر).",
    "Text": "متن",
    "Text shown inside the life bar.": "متنی که داخل نوار جان نمایش داده می‌شود.",
    "Text color": "رنگ متن",
    "Color of the life bar's text.": "رنگ متن نوار جان.",
    "Enable custom background color": "فعال کردن رنگ پس‌زمینهٔ سفارشی",
    "If checked, you can choose a background color on the next field.": "اگر فعال باشد، می‌توانید در فیلد بعدی رنگ پس‌زمینه را انتخاب کنید.",
    "Background color": "رنگ پس‌زمینه",
    "Color of the life bar's background.": "رنگ پس‌زمینهٔ نوار جان.",
    "Share drain across all decks": "اشتراک کاهش جان بین همهٔ دسته‌ها",
    "Current life will be shared between all decks.": "جان فعلی بین همهٔ دسته‌ها مشترک خواهد بود.",
    "Maximum life": "حداکثر جان",
    "Time in seconds for the life bar go from full to empty.": "زمان خالی شدن نوار جان از پر تا خالی، به ثانیه.",
    "Answer recover": "بازیابی با پاسخ",
    "Time in seconds that is recovered after answering a card.": "مقدار زمانی که پس از پاسخ دادن به کارت بازیابی می‌شود، به ثانیه.",
    "Full recover speed": "سرعت بازیابی کامل",
    "Amount to recover each second when clicking the \"Recover\" button in the deck overview screen or using the Recover shortcut on the review screen or deck overview screen. Negative values allowed.\nUse 0 for the default behavior: instant recovery.\nThe recover will stop once life reaches 0, maximum, or if going back to deck browser screen.": "مقدار بازیابی در هر ثانیه هنگام کلیک روی دکمهٔ «بازیابی» در صفحهٔ نمای کلی دسته یا استفاده از میانبر بازیابی در صفحهٔ مرور یا نمای کلی دسته. مقادیر منفی مجاز است.\nبرای رفتار پیش‌فرض، یعنی بازیابی فوری، 0 بگذارید.\nبازیابی وقتی جان به 0 یا حداکثر برسد، یا با بازگشت به صفحهٔ فهرست دسته‌ها متوقف می‌شود.",
    "Enable damage": "فعال کردن آسیب",
    "Enable the damage feature. It will be triggered when answering with 'Again'.": "قابلیت آسیب را فعال می‌کند. با پاسخ «دوباره» اعمال می‌شود.",
    "New cards": "کارت‌های جدید",
    "Damage value on new cards.": "مقدار آسیب در کارت‌های جدید.",
    "Learning cards": "کارت‌های یادگیری",
    "Damage value on learning cards.": "مقدار آسیب در کارت‌های یادگیری.",
    "Review cards": "کارت‌های مرور",
    "Damage value on review cards.": "مقدار آسیب در کارت‌های مرور.",
    "Enable for this deck": "فعال برای این دسته",
    "Enable/disable Life Drain for this deck.": "Life Drain را برای این دسته روشن یا خاموش می‌کند.",
    "Current life": "جان فعلی",
    "Current life, in seconds.": "جان فعلی، به ثانیه.",
    "Drain life": "کاهش جان",
    "Do nothing": "هیچ کاری نکن",
    "Recover life": "بازیابی جان",
    "Top": "بالا",
    "Bottom": "پایین",
    "None": "هیچ‌کدام",
    "current/total (XX%)": "فعلی/کل (XX%)",
    "current/total": "فعلی/کل",
    "current": "فعلی",
    # Controller support: dialogs and messages
    "Controller not detected. Connect your controller and press any button to initialise.": "دسته بازی شناسایی نشد. دسته را وصل کنید و برای راه‌اندازی یکی از دکمه‌ها را بزنید.",
    "Contanki Options": "تنظیمات Contanki",
    "Controls": "کنترل‌ها",
    "Controller": "دسته بازی",
    "Save": "ذخیره",
    "Cancel": "لغو",
    "Help": "راهنما",
    "Profile": "پروفایل",
    "Add Profile": "افزودن پروفایل",
    "Rename": "تغییر نام",
    "Import": "وارد کردن",
    "Export": "خروجی گرفتن",
    "Create New Profile": "ساخت پروفایل جدید",
    "Select an existing profile to copy:": "پروفایل موجودی را برای کپی انتخاب کنید:",
    "Enter the new profile name:": "نام پروفایل جدید را وارد کنید:",
    "You can't delete the last profile": "نمی‌توانید آخرین پروفایل را حذف کنید",
    "New Name": "نام جدید",
    "Please enter a new profile name": "لطفاً نام جدید پروفایل را وارد کنید",
    "Import Profile": "وارد کردن پروفایل",
    "Export Profile": "خروجی گرفتن از پروفایل",
    "Contanki Profiles (*.contanki)": "پروفایل‌های Contanki (*.contanki)",
    "Invalid profile": "پروفایل نامعتبر است",
    "Custom Action": "عملکرد سفارشی",
    "Shortcut": "میانبر",
    "Add": "افزودن",
    "New Action": "عملکرد جدید",
    "Flags": "نشانه‌ها",
    "Axis Roles": "نقش محورها",
    "Invert": "وارونه",
    " (inherited)": " (ارث‌بری‌شده)",
    "Use this page if the buttons on your controller are not working as expected. Press each button on your controller, and select the correct button from the dropdown that flashes.": "اگر دکمه‌های دسته بازی شما درست کار نمی‌کنند، از این صفحه استفاده کنید. هر دکمهٔ دسته را فشار دهید و دکمهٔ درست را از فهرست کشویی‌ای که چشمک می‌زند انتخاب کنید.",
    "Reset": "بازنشانی",
    "Would you be willing to share your controller configuration with the developer? This makes it easier to support this controller out of the box.": "آیا مایلید پیکربندی دسته بازی خود را با توسعه‌دهنده به اشتراک بگذارید؟ این کار پشتیبانی آماده از این دسته را آسان‌تر می‌کند.",
    "Not Assigned": "تعیین نشده",
    "Deck Browser": "فهرست دسته‌ها",
    "Overview": "نمای کلی",
    "Review": "مرور",
    "Question": "سؤال",
    "Answer": "پاسخ",
    "Dialogs": "پنجره‌ها",
    "Controller Options": "تنظیمات دسته بازی",
    "Contanki was unable to load config, using defaults.": "Contanki نتوانست تنظیمات را بارگذاری کند؛ از پیش‌فرض‌ها استفاده می‌شود.",
    "Action not available on this screen": "این عملکرد در این صفحه در دسترس نیست",
    "Nothing to undo": "چیزی برای برگرداندن نیست",
    "Nothing to redo": "چیزی برای انجام دوباره نیست",
    "This action is only available in Anki 2.1.50+": "این عملکرد فقط در Anki 2.1.50 به بالا در دسترس است",
    "This action can only be done on filtered decks": "این عملکرد فقط در دسته‌های فیلترشده انجام می‌شود",
    "Error: Unable to load profile {profile}": "خطا: بارگذاری پروفایل {profile} ممکن نیست",
    "{controller} Connected": "{controller} وصل شد",
    "Controller Disconnected": "دسته بازی قطع شد",
    "{count} controllers detected - select from the Tools menu.": "{count} دسته بازی شناسایی شد؛ از منوی ابزارها انتخاب کنید.",
    "See the <a href=\"https://ankiweb.net/shared/info/1898790263\">add-on page</a> for some tips on using Contanki. If you're having trouble or have found a bug you can post on the <a href=\"https://forums.ankiweb.net/t/contanki-official-support-thread/\">official support thread</a> or the <a href=\"https://github.com/roxgib/anki-contanki/issues\">GitHub issue tracker</a>. <br><br>Please copy and paste the following information into your post:<br><br>": "برای دیدن نکته‌هایی دربارهٔ استفاده از Contanki به <a href=\"https://ankiweb.net/shared/info/1898790263\">صفحهٔ افزونه</a> سر بزنید. اگر مشکلی دارید یا خطایی پیدا کرده‌اید، می‌توانید در <a href=\"https://forums.ankiweb.net/t/contanki-official-support-thread/\">رشتهٔ پشتیبانی رسمی</a> یا <a href=\"https://github.com/roxgib/anki-contanki/issues\">فهرست مشکلات GitHub</a> بنویسید. <br><br>لطفاً اطلاعات زیر را در پیام خود کپی کنید:<br><br>",
    # Controller support: option names (stored in English, shown translated)
    "Scroll Speed": "سرعت پیمایش",
    "Cursor Speed": "سرعت نشانگر",
    "Cursor Acceleration": "شتاب نشانگر",
    "Stick Deadzone": "ناحیهٔ مردهٔ استیک",
    "Enable Control Overlays": "فعال کردن راهنمای دکمه‌ها",
    "Large Overlays": "راهنمای بزرگ",
    "Overlays Always On": "راهنما همیشه روشن",
    "Overlays in Quick Select": "راهنما در انتخاب سریع",
    "Detect 8BitDo Controllers": "شناسایی دسته‌های 8BitDo",
    "Enable Quick Select": "فعال کردن انتخاب سریع",
    "Select with Stick": "انتخاب با استیک",
    "Select with D-Pad": "انتخاب با D-Pad",
    "Do Action on Release": "اجرای عملکرد هنگام رها کردن",
    "Do Action on Stick Press": "اجرای عملکرد با فشردن استیک",
    "Do Action on Stick Flick": "اجرای عملکرد با حرکت سریع استیک",
    # Controller support: axis roles (stored in English, shown translated)
    "Unassigned": "بدون نقش",
    "Buttons": "دکمه‌ها",
    "Cursor Horizontal": "نشانگر افقی",
    "Cursor Vertical": "نشانگر عمودی",
    "Scroll Horizontal": "پیمایش افقی",
    "Scroll Vertical": "پیمایش عمودی",
    # Controller support: actions (stored in English, shown translated; each
    # translation must be unique so a dropdown choice maps back to one action)
    "Show Quick Select": "نمایش انتخاب سریع",
    "Toggle Quick Select": "روشن/خاموش کردن انتخاب سریع",
    "Quick Select": "انتخاب سریع",
    "Sync": "همگام‌سازی",
    "Go to Overview": "رفتن به نمای کلی",
    "Go to Main Screen": "رفتن به صفحهٔ اصلی",
    "Go to Review": "رفتن به مرور",
    "Open Browser": "باز کردن فهرست کارت‌ها",
    "Open Statistics": "باز کردن آمار",
    "Undo": "برگرداندن",
    "Redo": "انجام دوباره",
    "Back": "قبلی",
    "Forward": "بعدی",
    "Enter": "تأیید",
    "Fullscreen": "تمام‌صفحه",
    "Volume Up": "افزایش صدا",
    "Volume Down": "کاهش صدا",
    "Add Notes": "افزودن یادداشت",
    "Preferences": "تنظیمات Anki",
    "Quit": "خروج",
    "Hide Cursor": "پنهان کردن نشانگر",
    "Click": "کلیک",
    "Secondary Click": "کلیک راست",
    "Select Next": "انتخاب بعدی",
    "Select Previous": "انتخاب قبلی",
    "Switch Window": "تعویض پنجره",
    "Escape": "خروج از پنجره",
    "Up": "بالا رفتن",
    "Down": "پایین رفتن",
    "Up by 10": "10 مورد بالاتر",
    "Down by 10": "10 مورد پایین‌تر",
    "Scroll Up": "پیمایش به بالا",
    "Scroll Down": "پیمایش به پایین",
    "Scroll Up Smooth": "پیمایش نرم به بالا",
    "Scroll Down Smooth": "پیمایش نرم به پایین",
    "Options": "گزینه‌ها",
    "Next Deck": "دستهٔ بعدی",
    "Previous Deck": "دستهٔ قبلی",
    "Next Due Deck": "دستهٔ موعددار بعدی",
    "Previous Due Deck": "دستهٔ موعددار قبلی",
    "Expand/Collapse": "باز/بسته کردن",
    "Filter Deck": "دستهٔ فیلترشده",
    "Check Database": "بررسی دیتابیس",
    "Check Media": "بررسی رسانه",
    "Empty Cards": "کارت‌های خالی",
    "Manage Note Types": "مدیریت انواع یادداشت",
    "Study Deck": "مطالعهٔ دسته",
    "Custom Study": "مطالعهٔ سفارشی",
    "Rebuild": "بازسازی",
    "Empty": "خالی کردن",
    "Again": "دوباره",
    "Hard": "سخت",
    "Good": "خوب",
    "Easy": "آسان",
    "Suspend Card": "تعلیق کارت",
    "Suspend Note": "تعلیق یادداشت",
    "Bury Card": "دفن کردن کارت",
    "Bury Note": "دفن کردن یادداشت",
    "Flag": "نشانه",
    "Mark Note": "علامت‌گذاری یادداشت",
    "Delete Note": "حذف یادداشت",
    "Record Voice": "ضبط صدا",
    "Replay Voice": "پخش صدای ضبط‌شده",
    "Card Info": "اطلاعات کارت",
    "Previous Card Info": "اطلاعات کارت قبلی",
    "Pause Audio": "توقف صدا",
    "Audio +5s": "صدا 5 ثانیه جلو",
    "Audio -5s": "صدا 5 ثانیه عقب",
    "Replay Audio": "بازپخش صوت",
    "Edit Note": "ویرایش یادداشت",
    "Flip Card": "برگرداندن کارت",
    "Set Due Date": "تعیین تاریخ موعد",
    "Toggle IO Masks": "نمایش/پنهان کردن ماسک‌های تصویر",
    "Focus Main Window": "تمرکز روی پنجرهٔ اصلی",
    # Review heatmap: options dialog (mnemonics are ignored when looking up)
    "Review Heatmap Settings": "تنظیمات نقشهٔ حرارتی مرور",
    "Review &Heatmap Options...": "تنظیمات نقشهٔ حرارتی مرور...",
    "Review Heatmap?": "Review Heatmap؟",
    "<html>Please leave a thumbs-up if you've enjoyed this add-on</html>": "<html>اگر از این افزونه راضی هستید، لطفاً به آن امتیاز مثبت بدهید</html>",
    "Rate": "امتیاز دادن",
    "<html>Follow me on Twitter for <br>updates on add-on releases and news on Anki in general!</html>": "<html>برای دریافت خبر نسخه‌های افزونه و <br>اخبار Anki مرا در Twitter دنبال کنید!</html>",
    "<html>Check out my YouTube channel for<br>helpful tutorials on this add-on and more</html>": "<html>برای آموزش‌های مفید دربارهٔ این افزونه و موارد دیگر<br>به کانال YouTube من سر بزنید</html>",
    "<html>Invoke the wiki page, add-on description, or manual</html>": "<html>باز کردن صفحهٔ ویکی، توضیحات افزونه یا راهنما</html>",
    "Perks include access to Patron-only add-ons, <br>exclusive blog posts, mentions in the credits, and more!": "مزایا شامل دسترسی به افزونه‌های ویژهٔ حامیان، <br>نوشته‌های اختصاصی وبلاگ، ذکر نام در فهرست سازندگان و موارد دیگر است!",
    "Support my work and receive\naccess to many exclusive add-ons!": "از کار من حمایت کنید و\nبه افزونه‌های اختصاصی زیادی دسترسی پیدا کنید!",
    "Heatmap appearance": "ظاهر نقشهٔ حرارتی",
    "Color scheme": "طرح رنگ",
    "Calendar mode": "حالت تقویم",
    "Sets the general color scheme of the add-on": "طرح رنگ کلی افزونه را تعیین می‌کند",
    "Sets the display mode of the calendar": "حالت نمایش تقویم را تعیین می‌کند",
    "Heatmap visibility": "نمایش نقشهٔ حرارتی",
    "Screen you're presented with when starting Anki": "صفحه‌ای که هنگام شروع Anki می‌بینید",
    "Main screen": "صفحهٔ اصلی",
    "Screen you see when clicking on a deck from the main screen": "صفحه‌ای که با کلیک روی یک دسته در صفحهٔ اصلی می‌بینید",
    "Deck screen": "صفحهٔ دسته",
    "Stats window": "پنجرهٔ آمار",
    "Stats screen": "صفحهٔ آمار",
    "Streak visibility": "نمایش زنجیره",
    "<html>Overrides the heatmap visibility setting, always showing you information on your stats (e.g. streaks, average, etc.)</html>": "<html>تنظیم نمایش نقشهٔ حرارتی را نادیده می‌گیرد و همیشه آمار شما (مثل زنجیره‌ها، میانگین و غیره) را نشان می‌دهد.</html>",
    "Show streak stats even when heatmap disabled": "نمایش آمار زنجیره حتی وقتی نقشهٔ حرارتی خاموش است",
    "General": "عمومی",
    "<html>Limits the number of days in the future that the heatmap displays. Only applies to main screen and deck overview.</html>": "<html>تعداد روزهای آینده را که نقشهٔ حرارتی نشان می‌دهد محدود می‌کند. فقط روی صفحهٔ اصلی و نمای کلی دسته اثر دارد.</html>",
    "No limit": "بدون محدودیت",
    " days": " روز",
    "History limit": "محدودیت تاریخچه",
    "Forecast limit": "محدودیت پیش‌بینی",
    "Ignore data before": "نادیده گرفتن داده‌های پیش از",
    "<html>Allows you to exclude a period of time from your stats (e.g. when you were still getting familiar with Anki).<br>Only applies to main screen and deck overview.</html>": "<html>امکان می‌دهد بازه‌ای از زمان را از آمار حذف کنید (مثلاً زمانی که هنوز با Anki آشنا نبودید).<br>فقط روی صفحهٔ اصلی و نمای کلی دسته اثر دارد.</html>",
    "<html>Limits the number of days in the past that the heatmap displays. Only applies to main screen and deck overview.</html>": "<html>تعداد روزهای گذشته را که نقشهٔ حرارتی نشان می‌دهد محدود می‌کند. فقط روی صفحهٔ اصلی و نمای کلی دسته اثر دارد.</html>",
    "<html>Ignores any reviews performed of cards that have been deleted since</html>": "<html>مرورهای کارت‌هایی را که بعداً حذف شده‌اند نادیده می‌گیرد</html>",
    "Exclude deleted cards from history": "حذف کارت‌های پاک‌شده از تاریخچه",
    "Exclude manual reschedules from history": "حذف زمان‌بندی‌های دستی از تاریخچه",
    "Exclude decks from main heatmap:": "حذف دسته‌ها از نقشهٔ حرارتی اصلی:",
    "<html>Any decks listed here will not be included in the calculations for the main heatmap. Each individual deck's heatmap will still work, however.</html>": "<html>دسته‌های این فهرست در محاسبات نقشهٔ حرارتی اصلی به حساب نمی‌آیند؛ با این حال نقشهٔ حرارتی هر دسته همچنان کار می‌کند.</html>",
    "Add new deck exclusion rule": "افزودن قانون جدید برای حذف دسته",
    "Delete deck exclusion rule": "حذف قانون حذف دسته",
    "Fine Tuning": "تنظیم دقیق",
    "About": "درباره",
    "Choose": "انتخاب",
    "Choose Deck": "انتخاب دسته",
    "Lime": "لیمویی",
    "Olive": "زیتونی",
    "Ice": "یخی",
    "Magenta": "سرخابی",
    "Flame": "شعله‌ای",
    "Yearly Overview": "نمای سالانه",
    "Continuous Timeline": "خط زمانی پیوسته",
    # Review heatmap: support dialog
    "Please support my work": "لطفاً از کار من حمایت کنید",
    "Love {ADDON_NAME}?": "{ADDON_NAME} را دوست دارید؟",
    "<html><head/><body><p>Hi! <strong>Glutanimate</strong> here :) Thanks for checking out Review Heatmap and some of my other add-ons. I hope you've been enjoying them! </p><p>If <strong>{ADDON_NAME}</strong> or any of <a href=\"action://installed-addons\"><span style=\" text-decoration: underline; color:#2980b9;\">my other projects</span></a> has been a valuable asset in your studies, please do consider <strong>supporting my work</strong>:</p></body></html>": "<html><head/><body><p>سلام! من <strong>Glutanimate</strong> هستم :) ممنون که Review Heatmap و افزونه‌های دیگر مرا امتحان کردید. امیدوارم از آن‌ها لذت برده باشید! </p><p>اگر <strong>{ADDON_NAME}</strong> یا هر یک از <a href=\"action://installed-addons\"><span style=\" text-decoration: underline; color:#2980b9;\">پروژه‌های دیگر من</span></a> در مطالعهٔ شما مفید بوده است، لطفاً به <strong>حمایت از کار من</strong> فکر کنید:</p></body></html>",
    "Become a Patron and receive \nexclusive add-ons && other goodies!": "حامی شوید و \nافزونه‌های اختصاصی و امتیازهای دیگر دریافت کنید!",
    "<html><head/><body><p>Each contribution is greatly appreciated and will help me <strong>update and improve</strong> my add-ons as time goes by! Thank you.</p></body></html>": "<html><head/><body><p>از هر کمکی بسیار سپاسگزارم؛ این کمک‌ها به من امکان می‌دهند افزونه‌هایم را <strong>به‌روز و بهتر</strong> کنم. سپاس از شما.</p></body></html>",
    # Review heatmap: deck list
    "Go back\n(Shift-click for first year)": "قبلی\n(برای سال اول Shift را نگه دارید و کلیک کنید)",
    "Go forward\n(Shift-click for last year)": "بعدی\n(برای سال آخر Shift را نگه دارید و کلیک کنید)",
    "Today": "امروز",
    "Support this add-on": "حمایت از این افزونه",
    "Daily average:": "میانگین روزانه:",
    "Average reviews on active days": "میانگین مرور در روزهای فعال",
    "Days learned:": "روزهای مطالعه:",
    "Percentage of days with review activity over entire review history": "درصد روزهای دارای مرور در کل تاریخچهٔ مرور",
    "Longest streak:": "طولانی‌ترین زنجیره:",
    "Longest continuous streak of review activity. All types of repetitions included.": "طولانی‌ترین زنجیرهٔ پیوستهٔ مرور. همهٔ انواع تکرار به حساب می‌آیند.",
    "Current streak:": "زنجیرهٔ فعلی:",
    "Current card review activity streak. All types of repetitions included.": "زنجیرهٔ فعلی مرور کارت‌ها. همهٔ انواع تکرار به حساب می‌آیند.",
    "No activity data to show (": "داده‌ای برای نمایش وجود ندارد (",
    ">options<": ">گزینه‌ها<",
    "day": "روز",
    "card": "کارت",
    # Review heatmap: hidden game
    "LIVES: ": "جان: ",
    "SCORE: ": "امتیاز: ",
    "BEST: ": "بهترین: ",
    "\n\nNew high score! 1 life replenished.": "\n\nرکورد جدید! 1 جان اضافه شد.",
    "GAME OVER{}\n\nPress space to play again": "بازی تمام شد{}\n\nبرای بازی دوباره Space را بزنید",
    "GAME OVER\n\nYou're out of lives for today,\nbut tomorrow is another day :)\n\nTip: Get more lives by\nkeeping up with your reviews!\n\nPro-Tip: Pledge your support on Patreon\nand get access to other secret\nfeatures and add-ons :)\n\nClick here to go to\npatreon.com/glutanimate": "بازی تمام شد\n\nجان‌های امروزتان تمام شد،\nاما فردا روز دیگری است :)\n\nنکته: با انجام منظم مرورها\nجان بیشتری بگیرید!\n\nنکتهٔ حرفه‌ای: در Patreon حمایت کنید\nو به قابلیت‌ها و افزونه‌های مخفی دیگر\nدسترسی پیدا کنید :)\n\nبرای رفتن به\npatreon.com/glutanimate اینجا کلیک کنید",
    "Psst! You've stumbled on a secret.<br>Return when you've done at least<br>{} cards for the day :)": "پیس! یک راز پیدا کردید.<br>وقتی امروز دست‌کم {} کارت را<br>مرور کردید برگردید :)",
    "No more Snanki rounds left for today,<br>but feel free to check back tomorrow :) !": "امروز دیگر دور Snanki باقی نمانده،<br>اما فردا دوباره سر بزنید :) !",
}

# Text and date names for the heatmap's calendar. Only sent to the page in Persian.
HEATMAP_FA_WEB: Dict[str, object] = {
    "reviewed": "مرور شده",
    "due": "موعد دارد",
    "card": "کارت",
    "noReviews": "مروری انجام نشده است",
    "noDue": "کارتی موعد ندارد",
    "on": "در",
    "dateFormat": "%A %-e %B %Y",
    "locale": {
        "decimal": ".",
        "thousands": ",",
        "grouping": [3],
        "currency": ["", ""],
        "dateTime": "%a %b %e %X %Y",
        "date": "%Y/%m/%d",
        "time": "%H:%M:%S",
        "periods": ["ق.ظ", "ب.ظ"],
        "days": ["یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه", "جمعه", "شنبه"],
        "shortDays": ["ی", "د", "س", "چ", "پ", "ج", "ش"],
        "months": ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن", "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"],
        "shortMonths": ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن", "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"],
    },
}


def tr(text: str) -> str:
    lang = _current_lang()
    if lang == "fa" and text in FA:
        return FA[text]
    if lang == "de" and text in DE:
        return DE[text]
    return _smartstudy(text)


def fa_active() -> bool:
    return _current_lang() == "fa"


def fa_tr(text: str) -> str:
    """Persian for the bundled add-ons' own texts; every other language is unchanged.

    tr() would also pull German from Smart Study's catalogue for common words
    such as "Delete", which would change those windows for German users.
    """
    if not fa_active():
        return text
    return FA.get(text) or _smartstudy(text)


def fa_html(html: str, phrases: Iterable[str]) -> str:
    """Translate the given English fragments of a fixed HTML template."""
    if not fa_active():
        return html
    for phrase in phrases:
        html = html.replace(phrase, fa_tr(phrase))
    return html


def _fa_widget_text(text: str) -> str:
    """Translation of a widget's text, ignoring its "&" keyboard mnemonic."""
    if not text:
        return text
    translated = fa_tr(text)
    if translated != text:
        return translated
    plain = re.sub(r"&(.)", r"\1", text)
    translated = fa_tr(plain)
    return translated if translated != plain else text


def translate_widgets(root) -> None:
    """Translate a pyuic form after setupUi; does nothing unless Persian is active.

    Text is only set when it changes: QAbstractButton.setText() would otherwise
    clear a shortcut assigned by the form.
    """
    if not fa_active():
        return
    from aqt.qt import QAbstractButton, QComboBox, QDoubleSpinBox, QGroupBox, QLabel, QSpinBox, QTabWidget, QWidget

    def apply(getter, setter) -> None:
        old = getter()
        new = _fa_widget_text(old)
        if new != old:
            setter(new)

    apply(root.windowTitle, root.setWindowTitle)
    for widget in [root, *root.findChildren(QWidget)]:
        apply(widget.toolTip, widget.setToolTip)
        if isinstance(widget, (QLabel, QAbstractButton)):
            apply(widget.text, widget.setText)
        elif isinstance(widget, QGroupBox):
            apply(widget.title, widget.setTitle)
        elif isinstance(widget, QComboBox):
            for index in range(widget.count()):
                apply(lambda i=index: widget.itemText(i), lambda value, i=index: widget.setItemText(i, value))
        elif isinstance(widget, QTabWidget):
            for index in range(widget.count()):
                apply(lambda i=index: widget.tabText(i), lambda value, i=index: widget.setTabText(i, value))
        elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
            apply(widget.suffix, widget.setSuffix)
            apply(widget.specialValueText, widget.setSpecialValueText)
