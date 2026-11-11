# Changelog

## 2.9.3 – 2026-11-11

- **Archive and Delete in sight**: every plan in the overview has an archive and a delete button on its card (an archived plan has *Make active again* instead), and an open plan has *Archive* and *Delete* in its bar. Before, deleting was a button at the very bottom of the editor and archiving sat in the retrospective. Deleting asks first and offers to archive instead; afterwards the message offers *Undo*, which brings the plan back with its ticks – also on your other devices. Archiving offers *Undo* too
- **Drafts can be deleted**: the delete button used to appear only once a plan had been created; a draft without days could not be removed at all
- **Fix – keys in a browser page triggered Anki's shortcuts**: Anki has shortcuts made of a single key (Space and Enter show the answer, 1–4 rate a card, D opens the decks, A adds a card …), and they fired wherever the focus was inside Anki's window – also in a browser tab. Pressing Space to pause a video showed the answer of the card behind the browser instead, most visibly with the browser in the main window. Now a browser tab (and the picture-in-picture window) keeps every key without Ctrl, Alt or Meta for its page. Shortcuts with a modifier work as before, and so do the browser's own shortcuts from *Settings → Browser*, whatever keys you gave them; Esc and the function keys stay with Anki. With the focus on a card, nothing changes

## 2.9.2 – 2026-11-11

- **Address suggestions**: while you type in the browser's address field, it offers pages you visited, your favourites and the other open tabs – best match first (start of the address before a match inside it before a match in the title; among equals the page visited more often and more recently). Pick one with the arrow keys and Enter or a click. The history is kept only on this computer, in the Anki profile (`SmartStudy_Data/browser_history.json`, at most 800 pages). *Options → Suggest visited pages in the address field* switches it off (favourites and open tabs are still offered), *Clear browsing history* removes it together with the kept site icons
- **Site icons are kept**: a site's icon is stored as a small picture (`SmartStudy_Data/favicons/`), so tabs restored after a restart – which load only when you open them – show their icon at once instead of a globe
- **Drag custom items**: in the study plan, drag a custom item onto another day (today or later) to move it there; the day lights up while you hover. The message afterwards offers *Undo*
- **Ticks from two devices are merged**: if you tick items on two computers before they sync, the newer copy of the plan used to replace the older one completely, and the other computer's ticks were gone. Now the newer plan takes over the ticks it does not know. An untick is remembered with its time, so a tick you removed does not come back from an older copy, and an untick made on the other device arrives too. Ticks of items that no longer exist (after replanning) are dropped
- **Fix – AI assistant kept a processor core busy**: the two glows behind the empty chat drifted forever; moving a 72 px blur of half the page repaints it on every frame. They stand still now. Measured in the test profile with only that sidebar open and nothing happening: about 40 % of one core before, 2 % now
- **Fix – gamification sidebar**: the glow behind the badge pulsed three times (24 s) every time the sidebar opened, at a similar cost while it ran; it pulses once
- **Fix – daily limit on the last day**: the last study day before a date takes whatever did not fit before. If that put more new cards on it than the deck's daily limit while earlier days still had room under the limit, the plan complained that the limit was too low. The surplus now moves back to those days (nearest first). Plans whose last day was within the limit are scheduled exactly as before

## 2.9.1 – 2026-11-11

- **Browser, new look**: the bars were rebuilt. Tabs are on top and share the width of their row – few tabs are wide enough for their title, many get narrower together down to their icon, and the row never pushes the sidebar wider (the scroll arrows only come back when even icon-sized tabs do not fit). Below them: back, forward, reload, a wide rounded address field, and options, *open in browser* and layout as sharp line icons without the little menu arrows. Saved sites sit in a slim favourites row (Home, your sites, +). A thin line under the bars fills while the page loads
- **Address field**: while you read it shows the short address (`youtube.com/watch?v=…`, a PDF by its file name; `http://` stays visible because it is not encrypted); a click shows the whole address, selected, to edit or copy
- **Stop**: while a page loads, Reload is a Stop button
- **Middle click**: on a tab closes it; on a favourite opens it in a background tab (Ctrl+click: in a new tab). Right-click a favourite for *Open in new tab* and *Remove* – the separate “-” buttons are gone
- **Tabs**: a tab without an icon of its own shows a globe (a sheet for PDFs), so a narrow tab is never blank. While tabs are narrow only the current one shows its ×
- **Fix – touchpad glide in pages and PDFs**: after a swipe the page keeps gliding at the speed your fingers had. The glide was measured in one unit and sent in another (QtWebEngine scrolls by `angleDelta`, not by `pixelDelta`, on Linux and Windows), which made it several times too slow: a hard swipe over a PDF stopped after about one page. Measured in a test with the same swipe: 850 px of glide before, 2,550 px now, as the speed at release predicts. The glide also takes one step per screen frame instead of two
- **Fix – study plan animations and CPU**: 2.9.0 animated things that make the browser lay out or repaint large areas for every frame (every card of a view on its own, row heights, bar widths, a full-window confetti canvas, a blurred dialog backdrop, counting numbers, view transitions). Now only opacity and transform are animated, a view fades in as one layer, bars scale instead of changing width, rows fade instead of changing height, confetti gets a small canvas. Measured in the test profile with a 38-day plan: switching views eight times 81 % → 24 % of one core (14 % with motion off), ticking eight items 70 % → about 40 % (21 % with motion off)
- **Fix**: a favourite added while the browser was open landed at the far right of its row
- **Fix**: Anki's deprecated night-mode call is now really replaced in all of the add-on's own files (2.9.0 claimed so but had missed 15 files, among them the browser, which printed the warning on every repaint of its bars)

## 2.9.0 – 2026-11-11

The study plan page was rebuilt around one idea: nothing is redrawn that did not change.

- **Updates in place**: a refresh (after a card in Anki, a sync, a tick) changes only the parts of the page that differ. Nothing flickers, the scroll position stays, and the field you are typing in keeps its focus and text. Before, the whole page was rebuilt each time, which also threw away a half-typed custom item
- **Animations**: views slide over each other (forwards from the right, back from the left), blocks of a new view rise one after the other, progress bars and rings glide to their value, numbers count up, the tick draws itself and the line through a finished item runs from its start to its end, added and removed rows slide in and out, dialogs and messages fade in and out. A day you complete yourself gets a small burst of confetti. All of it is off when the system or Anki (*Preferences → Reduce motion*) asks for calm
- **Instant ticks**: a click on a box shows at once; Anki confirms in the background. If saving fails, the tick is taken back and a message says why
- **Undo**: removing a custom item or a weak-spot item shows a message with *Undo* that puts it back where it was, including its tick
- **Custom items**: *→ tomorrow* moves one to the next day; a duration at the end of the text (“… 45 min”, “… (1,5 h)”) is taken as its time. A year or a chapter number is not mistaken for a duration
- **Today**: a *Today* button appears when today's card is out of sight (also key **t**); each day shows a progress ring and, today, the time still open; the overview shows today's items across all plans and per plan
- **Mock exam**: Space or Enter shows the answer, **1**/→ marks it right, **2**/← wrong; a bar shows the time running out and the exam is evaluated by itself when it is up. A double click no longer skips a card, and a mock exam no longer shows up in another plan
- **Unsaved changes**: leaving the editor with changes asks *Save / Discard / Keep editing*, and so does closing the window. Esc closes dialogs and leaves fields, but no longer the whole window
- **Editor**: changing a date, the daily minutes or a page range no longer swallows the click into the next field; deck numbers are fetched once instead of on every redraw; removing a source asks in the add-on's own dialog
- **Dialogs**: Enter takes the main button, Esc cancels, Tab stays inside, focus returns to where it was. Selecting text and letting go outside no longer closes a dialog. Messages stack instead of covering each other
- **No stutter while reviewing**: with the study plan open, every answered card made Anki count the plan's cards on its main thread (about 0.2 s with 20,000 cards). The numbers are now collected in the background and handed to the page; while the window is minimised nothing is counted until it is shown again
- **Faster overview**: the heatmap's year of reviews is counted by the database instead of row by row in Python (0.64 s → 0.01 s on 20,000 cards with a year of history); the same for the ratings per day of a plan
- **Robust storage**: plan files are written completely before they replace the old one; a file that is no JSON anymore is renamed to `….broken-<time>` instead of being overwritten, and the copy in the collection restores the plan; plans with missing fields (older versions, scripts, another device) are completed when read, so neither the planner nor the page stumbles; a plan id that would point outside the plans folder is ignored; the list of deleted plans is trimmed after 400 days
- **Planner**: when reviews (or other plans) leave no free minute before a date, the material is spread evenly over those days instead of all landing on the last one
- **Fixes**: one broken plan no longer empties the overview or stops *Replan* for the others; an item that vanished meanwhile gives a clear message instead of an empty error; a deck that no longer exists no longer breaks the plan's numbers; opening the window while it is minimised brings it back; Anki's deprecated night-mode call (a warning on every use) is replaced everywhere in the add-on

## 2.8.3 – 2026-11-10

- **Study plan finds moved PDFs**: if a PDF of the plan is no longer where it was (moved into another folder, renamed folder …), *open* looks for it by its file name – first next to the plan's other PDFs, then in your home folder – and opens it at the right page. If it can't be found, a window asks where you saved it
- **PDFs on every device**: each computer remembers its own paths to the plan's PDFs (in the add-on's `user_files`, not synced). The synced plan only carries the file's name and size, so on a second computer the same plan finds its copy of the PDF by itself, or asks once

## 2.8.2 – 2026-11-05

- **Smooth scrolling**: after a quick swipe on the touchpad, pages of the Smart Study browser keep gliding and slow down (like in Firefox or on a phone); Anki's own pages keep Anki's normal scrolling. Switch: *Settings → Browser → Smooth scrolling*
- **Smoother switching**: sidebars (browser, AI assistant, notebook, mind map, music …) slide in from the side when they open and out when they close – a picture of the sidebar moves, so the pages are laid out only once and the motion stays smooth; browser tabs cross-fade
- **Deck list beside the browser**: when the browser (or another sidebar) leaves Anki's main area narrow, the dashboard switches to its compact form and statistics, heatmap and deadline bar step aside – the deck list fits without scrolling. The deck table uses the full width (Anki normally caps the name column at the window width minus 300 px and themes fix the table at 860 px – both cut it off), long deck names wrap, and Anki's top bar no longer loses its first links. Close the sidebar and the full dashboard comes back
- **YouTube “Allow YouTube ads?” / “Ad blockers are not allowed”**: the message is removed from YouTube's data before it shows (as uBlock Origin does); should it still appear, it is closed and the video plays on
- **Layouts for every sidebar**: the AI assistant (⧉ in its tab bar), notebook and mind map (their enlarge button) offer the same choices as the browser – sidebar, split view, main window (notebook, mind map) and own window. Own windows stay open when you open another sidebar from the launcher. Switching from one sidebar to another keeps the width and cross-fades, so Anki doesn't jump
- **Browser layout**: the window button in the browser's bar now offers *Sidebar*, *Split view* (cards and browser half and half, divider still draggable), *Main window* and *Own window*. The own window is a normal window: any size, maximise it, snap it beside Anki (e.g. Meta+←/→ on KDE/Windows) or move it to a second screen. Its size and place are remembered; videos from the study plan open there
- **Saved passwords**: after you log in on a site, the browser offers to save the user name and password. Next time the login page is filled in – you only click *Log in*. Passwords are kept in your system keyring (Linux: KWallet, GNOME Keyring, KeePassXC … via `secret-tool`; macOS Keychain; Windows Credential Manager), never in the add-on's files. *⚙ → Save and fill in passwords* turns it off, *Delete saved passwords…* removes them
- **Full screen in the browser**: the full-screen button of a video (YouTube, Moodle/Opencast …, also double-click or *f*) now fills the whole screen instead of doing nothing. Esc or the button again brings it back into its tab
- **Stay logged in**: logins in the browser (e.g. Moodle with university single sign-on) are kept when Anki restarts, until the site itself ends the session
- **Study plan → browser**: opening a video or PDF from the study plan in the Smart Study browser now puts the study-plan window aside and brings Anki with the browser to the front
- **Pinch to zoom**: touchpad pinch gestures reach the browser tab under the pointer (pages and PDFs) even when the system hands them to the window around it
- **Fix**: closing a study-plan video tab right after it changed page no longer shows an error (“wrapped C/C++ object of type QWebEngineView has been deleted”)

## 2.8.1 – 2026-11-05

- **Study-plan videos and PDFs in your default browser**: new switch under *Settings → Browser*, on by default. On: videos open in your normal web browser and PDFs in your PDF app (Okular/Evince at the right page, otherwise the default app). Off: both open in a Smart Study browser tab as in 2.8.0. Replaces the switch *Open study-plan links in the browser*

## 2.8.0 – 2026-11-05

- **Share study plans with friends**: the new *Share* button in a plan copies a code that fits into a chat message (WhatsApp, Signal, e-mail …), saves the plan as a `.smartstudy.json` file, or copies a readable day-by-day overview for people without the add-on. Shared are the days, topics, sources, milestones and video links – not your progress (ticks, mock exams, retrospective) and not the paths of PDFs on your computer
- **Import a plan**: *Import* on the study plan start page takes over a plan from the pasted message or from a file. A plan from someone else is checked and cleaned before it is stored (only web links, no file paths, sane sizes); missing Anki decks and the PDF to choose are pointed out
- **PDFs in the browser**: PDFs are shown in the browser tab with Chromium's PDF viewer instead of being offered as a download (which did nothing before). PDFs that a site sends as a download (e.g. Moodle's “force download”) are saved to *Downloads/Smart Study PDFs* and opened in the tab right away; the same link reuses its file. *⚙ → Open PDF file…* shows a PDF from your computer, and ↗ opens a PDF tab in your PDF app. Of local files, only PDFs can be opened in the browser
- **Study-plan PDFs in the browser**: *open* in the study plan opens the PDF in a browser tab at the right page (Okular/Evince are still used when *Open study-plan links in the browser* is off)
- **Address bar**: the browser shows the address of the current tab; type an address, a path to a PDF or a search (with your search engine) and press Enter. Esc restores the address, Ctrl+L (adjustable under *Settings → Browser*) jumps into it

## 2.7.0 – 2026-11-03

- **Browser tabs**: open several pages at once (+, Ctrl+T, middle click or Ctrl+click on a link); a link that wants a new window opens in a tab. Sound in a background tab keeps playing
- **Tab groups**: ▤ next to + saves the open tabs as a named group and opens it again later, in addition to or instead of the open tabs. Open tabs come back after a restart and load only when you open them
- **Study-plan videos in the browser**: links from the study plan open in a browser tab. A video starts where you stopped and is checked off in the plan once you have watched 90 % of it (80–100 % adjustable)
- **Video control from anywhere in Anki**: play/pause, 10 s back/forward, slower/faster, picture in picture and “card at this point of the video” with keyboard shortcuts that also work while reviewing, and as controller actions
- **Picture in picture**: the video plays in a small window over Anki that you can move and resize, also over the reviewer
- **Cards from the browser**: right-click selected text (“Create card from selection”), an image (“Image occlusion from this image”, opens Anki's mask editor) or a video (“Card at this point of the video”, with a link to the second). They open in Anki's Add window with the source
- **Focus mode**: hide YouTube Shorts, start-page recommendations, suggestions or comments and block sites such as Instagram or TikTok – always or only during a Pomodoro study phase. YouTube itself stays usable, e.g. for music
- **SponsorBlock**: skips sponsors, self-promotion, like/subscribe reminders and non-music parts of music videos on YouTube; categories selectable
- **New settings page “Browser”**: all of the above, with freely assignable shortcuts
- **YouTube starts faster**: with YouTube set to “device theme” every page loaded twice (about 3 s per video). Smart Study now sets light or dark as in Anki
- **Much less memory**: hidden web pages no longer keep running. After a minute out of sight a page is frozen (no CPU). Browser tabs, AI websites and YouTube Music not looked at for 10 minutes, and the music controls and the gamification sidebar after 30 minutes, are unloaded and reload when you open them again. Anything playing sound is never touched. The API chat is only frozen, so its conversation stays on screen. The SoundCloud page is unloaded when you switch back to local music, and the browser no longer starts an empty page. Measured in a test profile with music, AI assistant, YouTube Music and three tabs open and then closed: 2.85 GB → 2.19 GB after 11 minutes and 1.63 GB after 31 minutes (sum of RSS; measured with AI websites and YouTube Music still unloading after 30 minutes)
- **Gemini and NotebookLM signed in**: they use the Google sign-in of the Smart Study browser, as Google refuses most sign-ins inside the AI sidebar

## 2.6.1 – 2026-11-03

- **Controller: multiple choice cards**: on the question side, the D-pad picks options 1 (up), 2 (right), 3 (down) and 4 (left), R2 picks option 5, and R buries the card. Works with checkboxes and radio buttons of the AllInOne cards. Included as the default profile *Xbox Series*; existing profiles of yours are not changed

## 2.6.0 – 2026-11-02

- **NotebookLM in the AI assistant**: a fourth tab next to ChatGPT, Claude and Gemini. Sign in with the e-mail address of your Google account (Google does not allow "Sign in with Google" inside Anki)
- **Browser: search engine of your choice**: the new ⚙ button in the browser picks DuckDuckGo, Google, Brave Search, Startpage, Ecosia or Bing for Home and for *Search in Sidebar* (which used Google before)
- **Browser: ad blocker with uBlock Origin's filter lists**: the default lists of uBlock Origin (uBlock filters, Privacy, Badware, Quick fixes, Unbreak, EasyList, EasyPrivacy, about 129,000 filters, refreshed weekly) are evaluated by a small engine of our own (`adblock_engine.py`): blocked requests never leave the computer, and ad slots on a site are hidden. On YouTube (also YouTube Music in the streaming sidebar), a script removes the ad data from YouTube's player responses before the player reads them, like uBlock Origin's `json-prune` filter, so ads are not even requested; a second script skips any ad that still shows (e.g. ads built into the video stream). Under ⚙: switch it off, switch it off for the current site, and see how much was blocked on the page. Not supported are uBlock Origin's scriptlets, procedural filters, redirects and generic element hiding
- **Music button closes the streaming sidebar**: with *Streaming* open, the music button closes it (playback goes on), so you no longer have to click *Streaming* again
- **Background playback in the browser**: sound from YouTube, podcasts and the like keeps playing when you close the browser or another sidebar (e.g. the AI chat) replaces it. Only a page that is playing sound stays awake, and only until it has been silent for 30 seconds
- **Lighter on CPU**: a paused SoundCloud player is no longer kept awake in the background and is polled every 4 s instead of every 0.8 s (mpv every 1 s instead of 0.1 s). The dashboard's study timers only touch the page when the shown time changes, so the layout is no longer recalculated every second

## 2.5.0 – 2026-10-30

- **Coming from Synapse**: Smart Study takes over your Synapse level and XP once on start, if Synapse's is higher. Removing Synapse keeps its data in the collection and the profile folder, so nothing needs to be reinstalled. Study time since then is still credited
- **Third-party notices**: KaTeX (math in AI answers) is now listed; its license file was already included

## 2.4.1 – 2026-10-30

- **Fix – copy selections with pictures**: in night mode the text of the selection was drawn white on the white image, so only the pictures were visible after pasting. The image now always has dark text; white text colors from the card (also in single-quoted `style` attributes) no longer carry over

## 2.4.0 – 2026-10-30

- **Persian (فارسی)**: all of Smart Study is available in Persian, with a right-to-left layout in its windows, pages and dashboard widgets. Choose it under *Settings → General → Language*, in the first-start window, or leave it on *Auto* with Anki set to Persian
- **Anki itself in Persian**: five broken lines in Anki's Persian file make Anki reject all of it, so it shows English with a right-to-left layout. Smart Study applies a repaired copy and adds the messages that file lacks. Text produced inside Anki's backend stays English, and the repair turns itself off once Anki's own file works. Choosing Persian in Smart Study offers to switch Anki too
- **AI assistant**: Persian as a response language
- **Study plan**: Persian on top of German and English. Plans made earlier keep their language until you replan

## 2.3.0 – 2026-10-29

- **Same add-ons on all your devices**: Smart Study asks once per device (on the first start and after this update) whether to sync your AnkiWeb add-ons. Your add-on list then travels with the AnkiWeb sync (`smartstudy_addons` in the collection), and on your other devices Smart Study offers to install what is missing. An add-on removed on one device leaves the list; add-ons you switch off in the offer are not offered again on that device, and **Don't ask again** turns add-on sync off on that device
- **Install add-ons by code**: *Settings → Add-ons* has a field for an AnkiWeb add-on code; it is downloaded and installed right away
- **New color: Orange**, and the example wallpaper **Orange Pixel Wallpaper** with a little pixel buddy at the side
- **Your own text color** for the "Studied … today" line on a custom background (*Settings → Appearance → Studied Text → Custom*), so it stays readable on any wallpaper
- **Renamed**: the leftover "Study Plan" / "Lernplan" decks from versions before 0.2 are now called **Smart Study system data** (filtered decks only; a deck of your own with that name stays as it is)

## 2.2.0 – 2026-10-29

- **Settings sync between devices**: the Smart Study settings and the on/off switches of the built-in add-ons are kept in the Anki collection (`smartstudy_settings`), so AnkiWeb sync takes them to your other devices. Of two copies, the newer one wins. Per device stay: which copy of an add-on runs (built-in or separately installed), the launcher being open, and the "What's new" state
- **Add-ons page in the settings**: switch each built-in add-on on or off at any time under *Settings → Add-ons* (the window under *Tools → Smart Study → Built-in add-ons…* stays for options and credits)
- **Removed**: the built-in progress bar. Install [Progress bar](https://ankiweb.net/shared/info/1708250053) from AnkiWeb if you want it back
- **Faster**: the dashboard statistics are reused until a review, sync or new day changes them (before: recomputed on every return to the deck list); the deck overview only reads the last 30 days of reviews; the review heatmap keeps one cached view per screen
- **Fix – review heatmap**: settings, a new day or a profile switch now update it right away; clicking a day in the deck-overview heatmap finds the cards; the old stats window had deck and collection swapped; no more Qt5 crashes in the shortcut field
- **Fix – controller support**: unplugging a controller is noticed; pads without sticks no longer cause an error 20 times a second
- **Fix – Life Drain**: no crash when another panel sits where the bar goes
- **Fix – copy selections with pictures**: Ctrl+C keeps the image, the same selection can be copied again, and pictures with "&" in the file name are found

## 2.1.1 – 2026-10-29

- The windows for built-in add-ons, already installed add-ons, updates and the restart question now use the Smart Study look (title, grouped rows, switches, pill buttons) with shorter texts
- “Already installed” offers **Take over & delete old ones** next to **Take over**: the separate copies go to the trash instead of only being switched off (Contanki profiles are copied first)

## 2.1.0 – 2026-10-29

- **Built-in add-ons** – no separate installs needed, each can be switched off under *Tools → Smart Study → Built-in add-ons…*:
  - **Copy selections with pictures as an image** (new, on by default): select part of a card with pictures and paste it into ChatGPT or Claude with the pictures
  - **Review heatmap**, based on [Review Heatmap](https://github.com/glutanimate/review-heatmap/) by Glutanimate
  - **Progress bar**, based on [Progress bar (Fork for 23)](https://ankiweb.net/shared/info/1708250053) by Shigeyuki and earlier authors
  - **Controller support**, based on [Contanki](https://github.com/roxgib/anki-contanki) by Sam Bradshaw, with reworked detection: controllers that were connected before Anki started are found, 8BitDo Zero pads use the right button layout, and if a controller cannot be told apart (e.g. the 8BitDo Zero 2 in X-Input mode on Windows) you are asked once which one it is
  - **Life Drain**, based on [Life Drain](https://github.com/Yutsuten/anki-lifedrain) by Yutsuten (off by default)
- If one of these add-ons is also installed separately, Smart Study asks once which copy to keep; your settings are taken over
- **"What's new" window** after an update, with switches to keep or turn off what was switched on
- **AI assistant**: ChatGPT, Claude and Gemini tabs – use your own account instead of an API key
- **Music**: a Streaming sidebar with YouTube Music; the Spotify tab opens the Spotify app (Spotify's web player needs Widevine, which Anki's browser does not have)
- **Fix**: the website sidebar crashed Anki when searching (back/forward buttons were wired to Qt actions that crash on update)
- **Fix**: `build.sh` left out `theme/user_files`, the bundled theme styles

## 2.0.1

- Only one workspace tool is open at a time: opening one closes the others
- Workspace screenshots in the README

## 2.0.0 – 2026-10-29

- **Smart Study is now one complete extension**: the study planner plus a workspace with notebook, PDF viewer, mind maps, Pomodoro, music, AI assistant, website sidebar, gamification, statistics and deadlines
- The planner lives in `addon/plan/` and opens via *Tools → Smart Study → Study Plan…* or the **Study Plan** link in the top bar
- Private by design: no analytics, no remotely loaded content, no update pings; the website sidebar starts on DuckDuckGo
- First-run setup without a Terms step
- New logo, icons, rank badges, achievements, music covers, wallpapers, focus sounds and timer chimes, generated by `tools/make_assets.py`
- Daily facts are shown as text only
- The left launcher starts below Anki's top toolbar instead of covering it
- The maintenance filtered deck is named `Smart Study · Maintenance (…)`
- The `.ankiaddon` file installs into a `smart_study` folder

## 0.3.1

- The "Study Plan" link sits left of "sync", so sync stays the rightmost link in the top bar

## 0.3.0 – 2026-10-27

- **Plans sync between your devices.** They are kept in the Anki collection as well, so the normal AnkiWeb sync takes them to your laptop. Of two copies of a plan, the newer one wins; deleted plans are deleted everywhere. Your pace and settings (`profile.json`) sync too
- Plans written as files by other tools (e.g. a script) are taken into the collection on the next start or sync
- The plan window refreshes after a sync

## 0.2.0 – 2026-10-26

- No filtered decks any more. **▶ study** opens the item's own deck, the cards stay where they are
- Mock exam runs in the plan window: random studied cards, show the answer, mark right or wrong, per-topic result. Nothing is moved
- "Study weak cards" opens Anki's browser with a search for the weak cards
- Removed "Study ahead"

## 0.1.1 – 2026-10-26

- Renamed from "Lernplan" to its English name. Existing filtered decks under `Lernplan` keep working and can be deleted when you no longer need them

## 0.1.0 – 2026-10-26

First public release.

- Study plans from books (page ranges), videos, lists and Anki decks, grouped into topics
- Scheduler with study time per day, days off, single-day exceptions, new-card limits and Anki's review forecast
- Milestones and soft lab-session milestones, reserve days before the exam
- Several plans with an optional shared daily budget
- Auto checkmarks from Anki, ▶ study and 📖 open-at-page links
- Weak spots round, study ahead, mock exam
- Retrospective with measured pace, maintenance mode, archive, next plan
- Study streak and heatmap
- English and German interface, follows Anki's language
