# Changelog

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

- Renamed from "Lernplan" to **Smart Study Plan**. New filtered decks go under `Smart Study Plan`; existing ones under `Lernplan` keep working and can be deleted when you no longer need them
- The `.ankiaddon` file now installs into a `smart_study_plan` folder

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
