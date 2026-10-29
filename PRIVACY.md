# Smart Study privacy and data behavior

This document describes Smart Study 2.0. Smart Study is a local Anki Desktop
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
- **SoundCloud:** loads SoundCloud's player, media, cookies, and artwork when
  SoundCloud mode is used.
- **External links:** support, community, API-key, and download links open only
  after a user action.

## Local and synced storage

- General settings, study plans, browser history/custom shortcuts, browser
  cookies, AI keys, notebook data, mind maps, and imported music files are
  profile-local under the Anki profile directory.
- AI keys are stored in `SmartStudy_Data/ai_secrets.json` with user-only file
  permissions where the operating system supports them.
- Gamification, deadlines, music preferences, and non-secret AI preferences use
  Anki collection configuration and may be included in Anki sync and backups.
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
