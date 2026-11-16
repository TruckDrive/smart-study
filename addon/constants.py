# -*- coding: utf-8 -*-

try:
    from .quiet import ignored as _ignored
except ImportError:  # the module is loaded on its own (tests)
    def _ignored(*_args):
        pass


# --- Addon Package Name ---
addon_package_name = "SmartStudy1"
ADDON_DISPLAY_NAME = "Smart Study"
print(f"Constants: Addon package name set to '{addon_package_name}'.")

ADDON_VERSION = "3.1.0"
MIN_ANKI_VERSION = "25.09.4"
MIN_ANKI_POINT_VERSION = 250904

# --- Launcher Constants ---
ADDON_NAME_LAUNCHER = "Launcher_Sidebar" 
ICONS_SUBFOLDER = "media" 

# --- Sizes & Layout (Launcher) ---
INFO_IMAGE_FILENAME = "news-banner.png"

# Sidebar tools that can receive a user-defined keyboard shortcut.  The keys
# deliberately match their existing enable/disable setting so one persisted
# map can drive both the settings UI and the runtime registrations.
SIDEBAR_SHORTCUT_KEYS = (
    "gamification_sidebar_enabled",
    "music_player_enabled",
    "pomodoro_enabled",
    "ai_assistant_enabled",
    "website_viewer_enabled",
)

# --- Filenames & Object Names (Launcher & Submodules) ---

WEBSITE_DOCK_OBJECT_NAME = "IntegratedWebsiteSidebarDock_SmartStudy_v1"
AI_ASSISTANT_DOCK_OBJECT_NAME = "AIAssistantSidebarDock_Integrated_v1"

# --- Pomodoro Constants ---
ADDON_NAME_POMODORO = "Pomodoro_Integrated"
CONFIG_KEY_POMODORO = f"addon_{ADDON_NAME_POMODORO}_config"
CONFIG_KEY_POMODORO_STATS = f"addon_{ADDON_NAME_POMODORO}_stats"
DEFAULT_POMODORO_CONFIG = { "work_minutes": 25, "short_break_minutes": 5, "long_break_minutes": 15, "pomodoros_before_long_break": 4, "sound_work_end": "bells.wav", "sound_break_end": "chime.wav", "auto_start_next": False }
DEFAULT_POMODORO_STATS = { "total_pomodoros": 0, "total_focus_minutes": 0, "best_streak": 0, "daily_data": {} }
STATE_IDLE = 0; STATE_WORK = 1; STATE_SHORT_BREAK = 2; STATE_LONG_BREAK = 3; STATE_PAUSED = 4

# --- Website Sidebar Constants ---
ADDON_NAME_WEBSITE = "Website_Sidebar"
CONFIG_KEY_CUSTOM_SITES = f"addon_{ADDON_NAME_LAUNCHER}_{ADDON_NAME_WEBSITE}_custom_sites_v2"
MAX_CUSTOM_SITES = 20
CONFIG_KEY_LAST_OPENED_URL = f"addon_{ADDON_NAME_LAUNCHER}_{ADDON_NAME_WEBSITE}_last_opened_url"


# --- Set by init at runtime ---
addon_path: str = ""
icons_folder: str = ""
sound_available: bool = False
play_sound_function = lambda x: None


def is_night() -> bool:
    """Anki's dark mode, asked the current way (mw.pm.night_mode() is deprecated
    and prints a warning on every call), with the old call as a fallback."""
    try:
        from aqt.theme import theme_manager
        return bool(theme_manager.night_mode)
    except Exception:
        _ignored()
    try:
        from aqt import mw
        return bool(mw and mw.pm and mw.pm.night_mode())
    except Exception:
        return False
