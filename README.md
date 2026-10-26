# Lernplan

**Study plans up to your exam, built from your book, your lectures and your Anki decks, and checked off by Anki as you study.**

You tell Lernplan what you have to learn (book pages, videos, lists of tasks, Anki decks), when the exam is and how much time you have each day. It spreads everything over the days until the exam, topic by topic: first read, then watch the lecture, then do the cards. Anki items tick themselves off while you study. If you fall behind, one click replans the rest.

![Plan view](screenshots/plan.png)

*"Lernplan" is German for "study plan". The interface is in English and German and follows Anki's language.*

## Features

**Planning**
- **Sources**: books, scripts or slides (page ranges), videos and lectures (with duration and link), any list (online modules, past questions, exercises) and **Anki decks**
- **Topics** bundle what belongs together: pages + subdeck or tag + videos. Create them from a **pasted table of contents** or from **subdecks**, then let **"Suggest links automatically"** match subdecks, tags and videos to topics by name
- **Smart scheduler**: works through the topics in order, respects your study time per day, days off and single-day exceptions, the daily new-card limit and the reviews Anki will throw at you (from its real forecast, plus the new cards coming back)
- **Milestones** (partial tests, quizzes) get their material done first. **Lab sessions** are soft milestones: read and watch before, cards continue afterwards
- **Reserve days** before the exam: weak spots round → mock exam → light review
- **Several plans at once**, optionally sharing one daily time budget (`"budget": {"minutesPerDay": 360}` in `user_files/profile.json`): the nearest exam gets scheduled first, later ones get what's left
- **Replan** moves everything still open (and your own custom items) onto the remaining days. Finished items stay where they were

**While studying**
- **Auto checkmarks**: card and review items are checked off from your Anki activity, everything else with a click
- **▶ study** opens the right deck (or a filtered deck with exactly that item's cards), **📖 open** opens the PDF at the right page (Okular/Evince)
- **Weak spots round**: finds the topics with the most mistakes and schedules the pages, video and weak cards for them again
- **Study ahead**: a filtered deck with cards that would only be due after the exam
- **Mock exam**: random studied cards against the clock, plus random topics to explain out loud, with a per-topic result

**Afterwards**
- **Retrospective**: planned vs. done, on time vs. late, per source, time spent in Anki and your measured pace, which becomes the default for your next plan
- **Maintenance mode**: keeps the decks running without new cards and with capped reviews (restores your old deck options when switched off)
- **Archive** and **next plan** in one click, plus a **study streak** and a **6-month heatmap** on the overview
- Light and dark mode, following Anki

## Screenshots

| Overview: streak, heatmap, plans | Dark mode |
|---|---|
| ![Overview](screenshots/home.png) | ![Plan in dark mode](screenshots/plan-dark.png) |

| Basics, milestones and single days | Sources |
|---|---|
| ![Basics](screenshots/edit-basics.png) | ![Sources](screenshots/edit-sources.png) |

| Topics with linked pages, lectures and subdecks | Tools: weak spots, study ahead, mock exam |
|---|---|
| ![Topics](screenshots/edit-topics.png) | ![Tools](screenshots/tools.png) |

**Retrospective**: what worked, and your real pace for the next plan

![Retrospective](screenshots/review.png)

## Install

Lernplan needs a recent Anki (developed and tested on 26.09).

**From a release**: download `lernplan.ankiaddon` from the [latest release](https://github.com/TruckDrive/lernplan/releases/latest) and open it with Anki (or *Tools → Add-ons → Install from file…*), then restart Anki.

**From source**:
```sh
git clone https://github.com/TruckDrive/lernplan.git
ln -s "$PWD/lernplan/addon" ~/.local/share/Anki2/addons21/lernplan   # Linux; on macOS/Windows copy the folder
```

## Usage

1. Open it via **Tools → Lernplan…** or the **Lernplan** link in Anki's top bar.
2. **+ New plan**: name and exam date (you can leave the date empty for a draft).
3. **Basics**: study time per day, days off, milestones, single days (e.g. 0 minutes on a busy day).
4. **Sources**: add your book (pace in minutes per page, optional PDF), your lectures (one per line: `Name | 25 | https://…`), lists and Anki decks (search, or pick from the suggestions matching your plan name).
5. **Topics**: paste the table of contents (`Peritoneum ...... 78`) or create topics from subdecks, then **Suggest links automatically** and check the ★ suggestions.
6. **Create plan**. From then on, study in Anki as usual; the plan keeps up.

Your plans are stored as JSON in the add-on folder under `user_files/plans/`, so they survive add-on updates. Filtered decks created by Lernplan live under a `Lernplan` parent deck.

## Development

```sh
python -I tests/test_planner.py               # scheduler, no Anki needed
python -I tests/test_ankidata.py <empty dir>  # Anki queries on a throwaway collection
./build.sh                                     # → dist/lernplan.ankiaddon
```

- `addon/planner.py`: the scheduler, plain Python
- `addon/ankidata.py`: everything that reads the collection or creates decks
- `addon/__init__.py`: window, menu entry, bridge between the web page and Python
- `addon/web/`: the interface (plain JS + CSS, no build step)

## License

[GNU AGPL v3](LICENSE)
