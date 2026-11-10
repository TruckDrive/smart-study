# -*- coding: utf-8 -*-
"""English changelog data, shown in the "What's new" window after an update.

An item with "integration" gets a switch for that built-in add-on in the
window, so the user can keep or undo the change right away.
"""

CHANGELOG = [
    {
        "version": "2.8.3",
        "date": "November 10, 2026",
        "items": [
            {"tag": "New", "text": "Study plan: if a PDF is no longer where it was, Smart Study looks for it by name and otherwise asks where you saved it."},
            {"tag": "New", "text": "Every device remembers where its PDFs are, so a synced plan opens the right files on each computer."},
        ],
    },
    {
        "version": "2.8.2",
        "date": "November 5, 2026",
        "items": [
            {"tag": "New", "text": "Smooth scrolling: pages in the browser keep gliding after a quick touchpad swipe."},
            {"tag": "New", "text": "Sidebars slide in from the side, browser tabs cross-fade."},
            {"tag": "New", "text": "AI assistant, notebook and mind map: sidebar, split view or their own window, like the browser."},
            {"tag": "Fix", "text": "YouTube's “Allow YouTube ads?” message no longer blocks videos while the ad blocker is on."},
            {"tag": "New", "text": "With the browser beside Anki, the deck list switches to a compact form that fits without scrolling."},
            {"tag": "New", "text": "Browser layout: sidebar, split view, main window or its own window (snap it beside Anki, use a second screen)."},
            {"tag": "New", "text": "The browser saves passwords in your system keyring and fills in login pages – you only click “Log in”."},
            {"tag": "New", "text": "Full screen in the browser: a video's full-screen button now fills the whole screen. Esc brings it back into its tab."},
            {"tag": "New", "text": "Logins in the browser (e.g. Moodle) are kept when Anki restarts."},
            {"tag": "New", "text": "Opening a video or PDF from the study plan brings the browser to the front."},
            {"tag": "Fix", "text": "Touchpad pinch to zoom works in browser tabs and PDFs."},
            {"tag": "Fix", "text": "No more error when a study-plan video tab is closed right after it changed page."},
        ],
    },
    {
        "version": "2.8.1",
        "date": "November 5, 2026",
        "items": [
            {"tag": "Changed", "text": "Settings → Browser: “Open study-plan videos and PDFs in your default browser” (on by default). Off: they open in a Smart Study browser tab."},
        ],
    },
    {
        "version": "2.8.0",
        "date": "November 5, 2026",
        "items": [
            {"tag": "New", "text": "Share study plans with friends: “Share” copies a code for WhatsApp & co., saves the plan as a file or copies a readable overview. Your progress and file paths stay private."},
            {"tag": "New", "text": "“Import” on the study plan start page takes over a plan from a code or file."},
            {"tag": "New", "text": "PDFs open right in the browser instead of being downloaded – also PDFs that a site (e.g. Moodle) sends as a download. ⚙ → “Open PDF file…” shows a PDF from your computer."},
            {"tag": "New", "text": "Study-plan pages (“open”) open the PDF in a browser tab at the right page."},
            {"tag": "New", "text": "Address bar in the browser: type an address or a search, see where you are. Ctrl+L jumps into it."},
        ],
    },
    {
        "version": "2.7.0",
        "date": "November 3, 2026",
        "items": [
            {"tag": "New", "text": "Browser tabs: open several pages at once (+, Ctrl+T, middle click). ▤ saves the open tabs as a group, and open tabs come back after a restart."},
            {"tag": "New", "text": "Study-plan videos open in the browser, continue where you stopped and are checked off once watched (90 %, adjustable)."},
            {"tag": "New", "text": "Video control from anywhere in Anki, also while reviewing: play/pause, ±10 s, speed, picture in picture and a card at the current second – with your own shortcuts or the controller."},
            {"tag": "New", "text": "Cards from the browser: right-click selected text, an image (image occlusion) or a video."},
            {"tag": "New", "text": "Focus mode: hide YouTube Shorts and recommendations, block sites like Instagram – always or only during a Pomodoro. SponsorBlock skips sponsors in YouTube videos."},
            {"tag": "New", "text": "Settings → Browser: all browser options and shortcuts in one place."},
            {"tag": "Changed", "text": "Much less memory: hidden pages are frozen and later unloaded; anything playing sound keeps running."},
            {"tag": "Changed", "text": "YouTube starts about 3 seconds faster, and Gemini and NotebookLM use your Google sign-in from the Smart Study browser."},
        ],
    },
    {
        "version": "2.6.1",
        "date": "November 3, 2026",
        "items": [
            {"tag": "New", "text": "Controller on multiple choice cards: D-pad up/right/down/left picks options 1–4, R2 picks option 5, R buries the card. Included as the default profile “Xbox Series”."},
        ],
    },
    {
        "version": "2.6.0",
        "date": "November 2, 2026",
        "items": [
            {"tag": "New", "text": "NotebookLM in the AI assistant: a fourth tab next to ChatGPT, Claude and Gemini, with your own Google account."},
            {"tag": "New", "text": "Browser: choose your search engine (DuckDuckGo, Google, Brave Search, Startpage, Ecosia, Bing) with the new ⚙ button."},
            {"tag": "New", "text": "Browser: built-in ad blocker with uBlock Origin's filter lists (uBlock filters, EasyList, EasyPrivacy), on by default; skips YouTube video ads."},
            {"tag": "New", "text": "Sound from the browser (YouTube, podcasts) keeps playing when you close the browser or open another sidebar such as the AI chat."},
            {"tag": "Changed", "text": "The music button also closes the streaming sidebar, no need to click “Streaming” again."},
            {"tag": "Changed", "text": "Lighter on your computer: a paused SoundCloud player and the dashboard timers use almost no CPU anymore."},
        ],
    },
    {
        "version": "2.5.0",
        "date": "October 30, 2026",
        "items": [
            {"tag": "New", "text": "Coming from Synapse: your level and XP are taken over automatically on the first start, if they are higher than in Smart Study."},
            {"tag": "Changed", "text": "Third-party notices now also list KaTeX (math in AI answers)."},
        ],
    },
    {
        "version": "2.4.1",
        "date": "October 30, 2026",
        "items": [
            {"tag": "Fix", "text": "Copying a selection with pictures: the text is in the image again when Anki is in night mode (it was white on white)."},
        ],
    },
    {
        "version": "2.4.0",
        "date": "October 30, 2026",
        "items": [
            {"tag": "New", "text": "Persian (فارسی): all of Smart Study in Persian, with a right-to-left layout."},
            {"tag": "New", "text": "Anki itself in Persian: Smart Study repairs Anki's Persian translation, which otherwise shows English."},
            {"tag": "New", "text": "The AI assistant can answer in Persian."},
        ],
    },
    {
        "version": "2.3.0",
        "date": "October 29, 2026",
        "items": [
            {"tag": "New", "text": "Same add-ons on all your devices: your AnkiWeb add-ons sync with AnkiWeb, and other devices offer to install what is missing."},
            {"tag": "New", "text": "Settings → Add-ons: install an add-on by entering its AnkiWeb code."},
            {"tag": "New", "text": "New color Orange and the Orange Pixel Wallpaper with a little pixel buddy."},
            {"tag": "Changed", "text": "The old “Study Plan” decks are now called “Smart Study system data”."},
        ],
    },
    {
        "version": "2.2.0",
        "date": "October 29, 2026",
        "items": [
            {"tag": "New", "text": "Your Smart Study settings and the switches for the built-in add-ons now sync to your other devices with AnkiWeb."},
            {"tag": "New", "text": "Settings → Add-ons: switch each built-in add-on on or off at any time."},
            {"tag": "Changed", "text": "The built-in progress bar was removed. Install Progress bar from AnkiWeb if you want it back."},
            {"tag": "Changed", "text": "Faster dashboard, deck overview and review heatmap."},
            {"tag": "Fix", "text": "Fixes for the review heatmap, controller support, Life Drain and copying selections with pictures."},
        ],
    },
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
