# Lernplan (Anki-Add-on)

Lernpläne bis zur Prüfung aus Handbuch/Skript (Seiten), Videos, Aufgaben und Anki-Decks.

- **Quellen + Themen:** Ein Thema bündelt Seiten, Unterdeck/Tag und Videos. Themen entstehen aus dem
  Inhaltsverzeichnis oder aus Unterdecks; „Zuordnung automatisch vorschlagen“ verknüpft per Namensähnlichkeit.
- **Planer:** verteilt alles Offene nach Lernzeit pro Tag bis zur Prüfung (lesen → Video → Karten pro Thema),
  hält das Tageslimit für neue Karten ein und reserviert die letzten Tage für Schwachstellen, Probeprüfung, Wiederholung.
  „Neu planen“ verteilt Rückstand neu; Erledigtes und eigene Punkte bleiben.
- **Auto-Häkchen:** Anki-Punkte werden beim Lernen abgehakt (Ziel = Anzahl gesehener Karten im Thema).
- **Werkzeuge:** Schwachstellen-Runde, Deck „vorziehen“ (nach der Prüfung fällige Karten), Probeprüfung auf Zeit.
- **Danach:** Rückblick (geplant vs. geschafft, pünktlich, echtes Tempo → Standard für den nächsten Plan),
  Erhaltungsmodus (eigene Optionsgruppe, rückgängig machbar), Archiv, nächster Plan per Knopfdruck, Serie + Heatmap.

Pläne: `addon/user_files/plans/<id>.json`, Tempo-Profil: `addon/user_files/profile.json`.

Tests (ohne echte Sammlung):
```
python -I tests/test_planner.py
python -I tests/test_ankidata.py <leerer-ordner>
```
Lokal installiert per Symlink `~/.local/share/Anki2/addons21/lernplan -> addon/`. Paket für AnkiWeb: `./build.sh`.
