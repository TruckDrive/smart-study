# Changelog

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
