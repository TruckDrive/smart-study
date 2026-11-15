# Smart Study

**One Anki extension for your whole study workflow: study plans up to your exam, plus a full workspace with notebook, PDF viewer, mind maps, focus timer, music, AI assistant and motivation, all inside Anki.**

![Smart Study: your decks, and on the right today's plan and your numbers](screenshots/home-3.0.png)

*Anki stays Anki: the deck list is where it always was. A slim rail on the left opens the tools; on the right, **Today** shows the countdown to your exam, today's plan items to tick off, and what is due.*

## Install

Smart Study needs Anki Desktop 25.09.4 or newer (developed and tested on 26.09).

**From AnkiWeb** (recommended): in Anki open *Tools → Add-ons → Get Add-ons…*, enter the code **`1726163334`** and restart Anki. Add-on page: https://ankiweb.net/shared/info/1726163334

**From a release**: download `smart_study.ankiaddon` from the [latest release](https://github.com/TruckDrive/smart-study/releases/latest) and open it with Anki (or *Tools → Add-ons → Install from file…*), then restart Anki.

**From source**:
```sh
git clone https://github.com/TruckDrive/smart-study.git
ln -s "$PWD/smart-study/addon" ~/.local/share/Anki2/addons21/smart_study   # Linux; on macOS/Windows copy the folder
```

**Updating from an older version** (0.x): uninstall it first, otherwise Anki shows two **Study Plan** links. Your plans come back by themselves through the Anki collection.

Changelog and release notes: [CHANGELOG.md](CHANGELOG.md) · [Releases](https://github.com/TruckDrive/smart-study/releases)

## About

You tell Smart Study what you have to learn (book pages, videos, lists of tasks, Anki decks), when the exam is and how much time you have each day. It spreads everything over the days until the exam, topic by topic: first read, then watch the lecture, then do the cards. Anki items tick themselves off while you study. If you fall behind, one click replans the rest. Around that, Smart Study turns Anki into a workspace so you don't have to leave it.

![Plan view](screenshots/plan-3.0.png)

*An Anki add-on for Anki Desktop. No account. Nothing is sent anywhere unless you use an online feature yourself (see [Privacy](#privacy)).*

## Features

### Study plan

**Planning**
- **Sources**: books, scripts or slides (page ranges), videos and lectures (with duration and link), any list (online modules, past questions, exercises) and **Anki decks**
- **Topics** bundle what belongs together: pages + subdeck or tag + videos. Create them from a **pasted table of contents** or from **subdecks**, then let **"Suggest links automatically"** match subdecks, tags and videos to topics by name
- **Smart scheduler**: works through the topics in order, respects your study time per day, days off and single-day exceptions, the daily new-card limit and the reviews Anki will throw at you (from its real forecast, plus the new cards coming back)
- **Milestones** (partial tests, quizzes) get their material done first. **Lab sessions** are soft milestones: read and watch before, cards continue afterwards
- **Reserve days** before the exam: weak spots round → mock exam → light review
- **Several plans at once**, optionally sharing one daily time budget (`"budget": {"minutesPerDay": 360}` in `plan/user_files/profile.json`): the nearest exam gets scheduled first, later ones get what's left
- **Replan** moves everything still open (and your own custom items) onto the remaining days. Finished items stay where they were. **Not today anymore** does the same for the rest of one day

**While studying**
- **Auto checkmarks**: card and review items are checked off from your Anki activity, everything else with a click
- **▶ study** opens the item's own deck. No filtered decks are created, so your cards always stay in their normal decks. **📖 open** opens the PDF at the right page in a Smart Study browser tab (or Okular/Evince)
- **Weak spots round**: finds the topics with the most mistakes and schedules the pages, video and weak cards for them again
- **Weak cards** open in Anki's browser with a search, nothing gets moved
- **Mock exam** runs in the plan window: random studied cards against the clock, show the answer, mark it right or wrong (or Space, 1, 2), with a per-topic result
- **Custom items**: add them to any day (“… 45 min” sets the duration), drag them to another day, remove them with Undo

**Afterwards**
- **Retrospective**: planned vs. done, on time vs. late, per source, time spent in Anki and your measured pace, which becomes the default for your next plan
- **Maintenance mode**: keeps the decks running without new cards and with capped reviews (restores your old deck options when switched off)
- **Archive**, **Delete** (with Undo) and **next plan** in one click, plus a **study streak** and a **6-month heatmap** on the overview
- Plans **sync between devices** through your Anki collection (AnkiWeb sync); ticks made on two devices are merged, and each device finds its own copy of the PDFs (by name, or it asks once)
- **Share with friends**: Share copies a code for WhatsApp & co. or saves the plan as a file; Import takes it over. Your progress and file paths stay private

### Workspace

- **Rail on the left, panel on the right**: a slim rail with the logo (opens the settings), a tab for every tool (each with an optional keyboard shortcut), Pomodoro and music. The tools open in a panel on the right and can also be shown as a split view, in the main window or in their own window
- **Today**, the first tab: countdown to the next exam, today's plan items to tick off without opening the plan, the daily challenge, and three charts with their own period each – cards due on the next days, reviews per day (hover for a day's number) and how much you remembered. It shows on the home screen only and stays away while you review
- **Notebook** with nested pages, task lists and a built-in **PDF viewer** (PDF.js bundled, nothing loaded from a CDN), plus a PDF card creator for basic, reversed and cloze cards
- **Mind maps** and FreeMap diagrams with images, icons and links to Anki cards
- **Pomodoro and session timers** with study-time analytics by deck
- **Music player** for local audio, optional SoundCloud, plus a Streaming sidebar with YouTube Music (Spotify opens in its app)
- **AI assistant** (optional): ChatGPT, Claude, Gemini or NotebookLM with your own account, one at a time (a small menu switches). The page talks to the site directly, as in a normal browser
- **Browser** with tabs, an address field that suggests visited pages, favourites with icons, PDF viewer (PDFs open right in the tab), ad blocker, saved passwords, and layouts: sidebar, split view, main window or its own window
- **Motivation**: XP, ranks, streaks, daily challenges, celebrations
- A **custom deck overview** with retention and hard cards, optional daily facts
- **Its own look**: a calm neutral dark and light theme in Anki's own font, accent colours, the older colour themes and custom backgrounds, eleven interface languages.

### Built-in add-ons

| Add-on | What it does | Default |
|---|---|---|
| **Copy selections with pictures as an image** | Select part of a card with pictures (mouse, Ctrl+A, Shift+arrows): it is copied as one image, so ChatGPT, Claude or a chat get the pictures when you paste. Text-only selections are not touched | on |
| **Review heatmap** | Calendar of your reviews and your streak on the deck list, deck overview and statistics | on |
| **Controller support** | Study with a gamepad such as the 8BitDo Zero 2; buttons for every screen. If a controller cannot be recognised reliably (e.g. any X-Input pad on Windows), you are asked once which one it is. Your button layouts sync to your other computers through AnkiWeb | on |
| **Life Drain** | A life bar that drains while you think and refills when you answer | off |

Switch them on or off under *Tools → Smart Study → Settings → Add-ons* or *Tools → Smart Study → Built-in add-ons…*. Changes take effect after restarting Anki, and the switches sync to your other devices with AnkiWeb. Settings are kept in `user_files/integrations/` (the heatmap and Life Drain also in the collection, like the originals), so updates do not reset them.

![Review heatmap on the deck list](screenshots/heatmap.png)

A controller that cannot be recognised reliably (many pads call themselves "Xbox 360 Controller") makes Smart Study ask once which one it is:

![Which controller?](screenshots/controller-ask.png)

**Good to know**
- Google does not allow signing in inside apps such as Anki (“This browser or app may not be secure”). Sign in to ChatGPT and Claude with your e-mail address; Gemini and YouTube Music also work without signing in.
- Spotify's web player needs the Widevine copy protection, which Anki's built-in browser does not include, so Spotify plays in its own app or your normal browser.

## Screenshots

| Light mode | While reviewing: the assistant next to the card |
|---|---|
| ![Home in light mode](screenshots/home-light-3.0.png) | ![AI assistant](screenshots/workspace-ai-assistant-3.0.png) |

| Browser: tabs, address field, favourites | Mind maps |
|---|---|
| ![Browser](screenshots/workspace-website-3.0.png) | ![Mind map](screenshots/workspace-mindmap-3.0.png) |

| Trophies: level, streak, challenge, badges | Settings: tabs on top, search, one switch per part |
|---|---|
| ![Trophies](screenshots/trophies-3.0.png) | ![Settings](screenshots/settings-3.0.png) |

**Study plan**

| Overview: streak, heatmap, plans | A plan in dark mode |
|---|---|
| ![Overview](screenshots/plan-home-3.0.png) | ![Plan in dark mode](screenshots/plan-dark-3.0.png) |

| Basics, milestones and single days | Sources |
|---|---|
| ![Basics](screenshots/plan-edit-3.0.png) | ![Sources](screenshots/edit-sources-2.9.png) |

| Topics with linked pages, lectures and subdecks | Tools: weak spots, mock exam |
|---|---|
| ![Topics](screenshots/edit-topics-2.9.png) | ![Tools](screenshots/tools-2.9.png) |

**Retrospective**: what worked, and your real pace for the next plan

![Retrospective](screenshots/plan-review-3.0.png)

## Usage

1. Open the planner via **Tools → Smart Study → Study Plan…** or the **Study Plan** link in Anki's top bar.
2. **+ New plan**: name and exam date (you can leave the date empty for a draft).
3. **Basics**: study time per day, days off, milestones, single days (e.g. 0 minutes on a busy day).
4. **Sources**: add your book (pace in minutes per page, optional PDF), your lectures (one per line: `Name | 25 | https://…`), lists and Anki decks (search, or pick from the suggestions matching your plan name).
5. **Topics**: paste the table of contents (`Peritoneum ...... 78`) or create topics from subdecks, then **Suggest links automatically** and check the ★ suggestions.
6. **Create plan**. From then on, study in Anki as usual; the plan keeps up.
7. The workspace tools are on the rail at the left edge of the window; settings are under **Tools → Smart Study → Settings…**.

Plans are stored as JSON under `plan/user_files/plans/` in the add-on folder and also in your Anki collection, so **AnkiWeb sync brings them to your other devices**. If you change a plan on two devices without syncing in between, the newer copy wins.

## Privacy

Smart Study sends nothing on its own: no analytics, no remote banner, no update pings. Online connections happen only when you use a feature that needs them: the AI assistant (to the provider or website you picked), the website sidebar, SoundCloud, YouTube Music, or a link you click. Details: [PRIVACY.md](PRIVACY.md).

## Development

```sh
python -I tests/test_planner.py               # scheduler, no Anki needed
python -I tests/test_ankidata.py <empty dir>  # Anki queries on a throwaway collection
python -I tests/test_store.py <empty dir>     # plan sync between two devices
./build.sh                                     # → dist/smart_study.ankiaddon
```

- `addon/__init__.py`: entry point, menu and hooks
- `addon/panel.py`, `addon/web_panel/`: the rail and the Today page; `addon/design.py`: the colour tokens shared by Qt and the web pages
- `addon/plan/`: the study planner (`planner.py` scheduler in plain Python, `ankidata.py` collection queries, `store.py` storage and sync, `web/` interface)
- `addon/*.py`, `addon/web_*`, `addon/settings_web/`: the workspace tools

## License

[GNU AGPL v3](LICENSE).

### Credits for the built-in add-ons

All bundled add-ons are licensed under the GNU AGPL v3 and were modified for Smart Study (config storage, loading as part of Smart Study, and for Contanki the controller detection). Their license files are kept in `addon/integrations/<name>/`.

- Based on the Anki add-on [Review Heatmap](https://github.com/glutanimate/review-heatmap/) by Glutanimate. [Click here to support Glutanimate's work.](https://glutanimate.com/support-my-work/)
- Controller support: based on [Contanki](https://github.com/roxgib/anki-contanki) by Sam Bradshaw
- Life Drain: based on [Life Drain](https://github.com/Yutsuten/anki-lifedrain) by Yutsuten

The workspace is based on [Synapse](https://github.com/mobesamedia/Synapse) by MobesaMedia (MIT License). Synapse's branding, images and sounds are not used; Smart Study's own are generated by `tools/make_assets.py`. The MIT notice is kept in [`addon/LICENSE-MIT.txt`](addon/LICENSE-MIT.txt). Bundled third-party libraries are listed in [`addon/THIRD_PARTY_NOTICES.md`](addon/THIRD_PARTY_NOTICES.md). The Lucide icons are under the ISC License (`addon/web_roadmap/icons/LICENSE.txt`).
