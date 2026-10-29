# -*- coding: utf-8 -*-
"""English changelog data, shown in the "What's new" window after an update.

An item with "integration" gets a switch for that built-in add-on in the
window, so the user can keep or undo the change right away.
"""

CHANGELOG = [
    {
        "version": "2.1.1",
        "date": "October 29, 2026",
        "items": [
            {"tag": "Changed", "text": "The windows for built-in add-ons, already installed add-ons and updates have the Smart Study look: clear groups, switches and short texts. Separately installed copies can be deleted right there (“Take over & delete old ones”)."},
        ],
    },
    {
        "version": "2.1.0",
        "date": "October 29, 2026",
        "items": [
            {"tag": "New", "text": "Built-in add-ons: you no longer need to install them separately. Switch them on or off under Tools → Smart Study → Built-in add-ons.", },
            {"tag": "New", "text": "Copy selections with pictures as an image – paste card pictures into ChatGPT or Claude.", "integration": "select2clip"},
            {"tag": "New", "text": "Review heatmap on the deck list (based on Review Heatmap by Glutanimate).", "integration": "heatmap"},
            {"tag": "New", "text": "Progress bar in the reviewer (based on Progress bar by Shigeyuki).", "integration": "progress_bar"},
            {"tag": "New", "text": "Controller support (based on Contanki), with better detection: if a controller such as the 8BitDo Zero 2 cannot be recognised reliably, you are asked once which one it is.", "integration": "contanki"},
            {"tag": "New", "text": "Life Drain (based on Life Drain by Yutsuten) – off by default.", "integration": "lifedrain"},
            {"tag": "New", "text": "AI assistant: use ChatGPT, Claude or Gemini with your own account, without an API key."},
            {"tag": "New", "text": "Music: YouTube Music in a sidebar; Spotify opens in its app."},
            {"tag": "Fix", "text": "The website sidebar no longer crashes Anki when you search."},
        ],
    },
    {
        "version": "2.0.1",
        "date": "October 29, 2026",
        "items": [
            {"tag": "Changed", "text": "Only one workspace tool is open at a time: opening the notebook, mind map, AI assistant, website or gamification sidebar closes the others."},
            {"tag": "New", "text": "Workspace screenshots and an updated README on GitHub."},
        ],
    },
    {
        "version": "2.0.0",
        "date": "October 29, 2026",
        "items": [
            {"tag": "Highlight", "text": "Smart Study combines the study planner and the workspace in one extension."},
            {"tag": "New", "text": "The study plan (sources, topics, milestones, auto check-off, mock exam, retrospective) replaces the old built-in study plan. Open it via Tools → Smart Study → Study Plan or the Study Plan link in the top bar."},
            {"tag": "Changed", "text": "No data is sent anywhere: the onboarding analytics upload and the remote news banner were removed."},
            {"tag": "Changed", "text": "The Terms acceptance step was removed from the first-run setup."},
            {"tag": "Fix", "text": "The left launcher starts below Anki's top toolbar instead of covering it."},
        ],
    },

]
