# Smart Study privacy and data behavior

This document describes Smart Study 2.1. Smart Study is a local Anki Desktop
add-on with several optional online tools.

## Automatic behavior

- Smart Study sends no data to the developer or to any other server on its own:
  no analytics, no remote news banner, no update checks.
- The notebook's PDF.js runtime is bundled and is never downloaded or executed
  from a CDN.
- Study plans are stored in the add-on folder (`plan/user_files/`) and in the
  Anki collection, so they travel with your normal AnkiWeb sync.

## Optional online features

- **AI Assistant:** sends the prompt and conversation needed for the request to
  the provider selected by the user. If card context is enabled, visible card
  text is included. Providers have their own privacy policies. Ollama and
  llama.cpp can be used locally.
- **Website sidebar:** loads websites selected by the user. “Search in Sidebar”
  sends the selected search phrase to Google after the user chooses the action.
- **AI websites (ChatGPT, Claude, Gemini):** the tabs in the AI assistant load
  these websites like a normal browser. What you type there goes to that
  website under its own privacy policy. Sign-ins and cookies are kept in
  `SmartStudy_Data/web_profiles/accounts` of the Anki profile.
- **YouTube Music:** the Streaming sidebar loads music.youtube.com (same
  browser storage as above). The Spotify tab only opens the Spotify app or
  open.spotify.com in your normal browser.
- **SoundCloud:** loads SoundCloud's player, media, cookies, and artwork when
  SoundCloud mode is used.
- **External links:** support, community, API-key, and download links open only
  after a user action.

## Built-in add-ons

The bundled add-ons (copy selection as image, review heatmap,
controller support, Life Drain) work offline. Their settings are stored in
`user_files/integrations/` inside the Smart Study add-on folder (kept on
updates); the heatmap and Life Drain also keep their settings in the Anki
collection, as the original add-ons do. "Copy selections with pictures as an
image" only writes to the local clipboard.

## Local and synced storage

- General settings, study plans, browser history/custom shortcuts, browser
  cookies, AI keys, notebook data, mind maps, and imported music files are
  profile-local under the Anki profile directory.
- AI keys are stored in `SmartStudy_Data/ai_secrets.json` with user-only file
  permissions where the operating system supports them.
- Gamification, deadlines, music preferences, and non-secret AI preferences use
  Anki collection configuration and may be included in Anki sync and backups.
- Smart Study's general settings and the on/off switches of the built-in
  add-ons are also mirrored into the collection configuration
  (`smartstudy_settings`), so AnkiWeb sync takes them to your other devices.
  They contain no API keys, history or personal content.
- A migration removes API keys and website history from the older
  collection-synced locations when the corresponding feature is first opened.

Uninstalling or updating an add-on may replace its installation directory.
Smart Study therefore keeps user data in the profile directory rather than the
add-on directory. Removing Smart Study does not automatically delete that data.

## Sensitive content

Do not paste secrets into AI prompts or website search. Card context is off
until explicitly enabled. API-provider requests are made directly from the
desktop client; Smart Study does not proxy them through any server.


## Optional local diagnostics

The developer console can record an explicitly started diagnostic session in
`SmartStudy_Data/diagnostics` within the active Anki profile. It records basic
runtime versions, timestamps, numeric performance measurements and fixed browser
event names/status codes. It does not record URLs, page content, search phrases,
card content, credentials or process command lines. No diagnostic data is
uploaded automatically. Users can explicitly export a ZIP for support.

Up to five recordings are retained, each with approximately 6 MiB of event logs
plus a small summary. Recording stops after eight hours at most and does not
restart automatically. Interrupted recordings remain available on the next
launch.
