# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

from aqt import QAction, QDialog, QHBoxLayout, QIcon, QResizeEvent, QTabWidget, QTextBrowser, QWidget, Qt, qconnect
from ..._shim import manager as _pb_manager_factory
_pb_manager = _pb_manager_factory('progress_bar')  # Smart Study: own config store
from aqt import QVBoxLayout, QLabel, QPushButton
from aqt import mw
from os.path import join, dirname
from aqt import QPixmap,gui_hooks
from aqt.utils import openLink

from ..shige_config.change_log import OLD_CHANGE_LOG
from ..shige_config.patrons_list import PATRONS_LIST
from ..path_manager import ADDON_NAME


CHANGE_LOG = "is_change_log"
# CHANGE_LOG_DAY = "2024-11-11j"
CHANGE_LOG_DAY = "2026-04-17"

POKEBALL_PATH = r"popup_icon.png"

THE_ADDON_NAME = "⌛️Progress bar (Fixed by Shige)"
SHORT_ADDON_NAME = "⌛️Progress bar (Fixed by Shige)"
IS_CHANGE_LOG = None
GITHUB_URL = "https://github.com/shigeyukey/my_addons/issues"


# popup-size
# mini-pupup
SIZE_MINI_WIDTH = 645
SIZE_MINI_HEIGHT = 523
# Width: 645, Height: 523


# Large-popup
SIZE_BIG_WIDTH = 700
SIZE_BIG_HEIGHT = 500

ANKI_WEB_URL = ""
RATE_THIS_URL = ""

ADDON_PACKAGE = mw.addonManager.addonFromModule(__name__)
# ｱﾄﾞｵﾝのURLが数値であるか確認
if (isinstance(ADDON_PACKAGE, (int, float))
    or (isinstance(ADDON_PACKAGE, str)
    and ADDON_PACKAGE.isdigit())):
    ANKI_WEB_URL = f"https://ankiweb.net/shared/info/{ADDON_PACKAGE}"
    RATE_THIS_URL = f"https://ankiweb.net/shared/review/{ADDON_PACKAGE}"



IS_CHANGE_LOG = True
PATREON_URL = "http://patreon.com/Shigeyuki"
REDDIT_URL = "https://www.reddit.com/r/Anki/comments/1b0eybn/simple_fix_of_broken_addons_for_the_latest_anki/"

POPUP_PNG = r"popup_shige.png"


NEW_FEATURE = """
2026-04-17:
[ Enhancements and Bug Fixes ]
    - Added text showing remaining cards.
        If not needed please disable it in the options.
    - Added Undo support.
    - Added V3 progress bar.
    - Restart is no longer required.

The explanation of the other changes is a bit long so I’ve written it below,
if you find any issues please contact me.
"""


SPECIAL_THANKS = """
[ Patreon ] Special thanks
Without the support of my Patrons, I would never have been
able to develop this. Thank you very much!🙏

{patreon}
""".format(patreon=PATRONS_LIST)



# CHANGE_LOG_TEXT = """\
# [ Change log : {addon} ]

# Shigeyuki : Hello, thank you for using this add-on!😆 I updated this Add-on.
# {new_feature}
# When Anki gets a major update add-ons will be broken, so if you like this add-on please support my volunteer development (so far I fixed 50 add-ons and created 37 new ones) by donating on Patreon to get exclusive add-ons. Thanks!


# [Change log]
# {old_change_log}

# {special_thanks}

# """.format( addon=SHORT_ADDON_NAME,
#             new_feature=NEW_FEATURE,
#             special_thanks=SPECIAL_THANKS,
#             old_change_log=OLD_CHANGE_LOG
#             )


patron_url_href = '<a href="https://www.patreon.com/posts/101345722" target="_blank">'

try:
    _Leaderboar_plus_path = join(dirname(dirname(__file__)), "chunk_progressbar.webp")
    str_Leaderboar_plus_path = (
        f'{patron_url_href}'
        f'<img src="{_Leaderboar_plus_path}"></a>'
    )
except Exception as e:
    print(f"[{ADDON_NAME}] ")
    str_Leaderboar_plus_path = ""

UPDATE_TEXT = "I updated this add-on."

CHANGE_LOG_TEXT = f"""\
[ Change log : {THE_ADDON_NAME} ]

Shigeyuki: Hi thanks for using this add-on! {UPDATE_TEXT}
{NEW_FEATURE}
--------
[ 🎮Shige's Gamification add-ons ] I develop as a hobby and so far I've fixed 80+ broken add-ons for free by request from users and released 30+ original add-ons for free! If you become a patron ($5/month) and support my volunteer development you can download the Patrons only add-on Chunk Progressbar.
{str_Leaderboar_plus_path}
[ {patron_url_href}Chunk Progressbar (Patrons only)</a> ] This add-on is an enhanced version of Progress bar for chunking Anki cards, add two progress bars to the top of Anki. Revenue from this add-on will be used to maintain and enhance the Free Progressbar add-on. (Not related to the official Anki.)
--------

[ Old change log ]
{OLD_CHANGE_LOG}

{SPECIAL_THANKS}
"""






CHANGE_LOG_TEXT_B = """\
{addon}
Shigeyuki :
Hello, thank you for using this add-on!😆

If you like this add-on, please support
my volunteer development on Patreon. Thank you!






Copyright (C) 🟢
(c) 2024 Shigeyuki  <https://github.com/shigeyukey>



{patreon}
""".format(addon=THE_ADDON_NAME, patreon=SPECIAL_THANKS)



# ------- Rate This PopUp ---------------

def set_gui_hook_change_log():
    gui_hooks.main_window_did_init.append(change_log_popup)
    # gui_hooks.main_window_did_init.append(add_config_button)

def change_log_popup(*args,**kwargs):
    try:
        config = _pb_manager.getConfig(__name__)
        # if (config[IS_RATE_THIS] == False and config[CHANGE_LOG] == False):
        if (config.get(CHANGE_LOG,False) != CHANGE_LOG_DAY):

            dialog = CustomDialog(mw, CHANGE_LOG_TEXT, size_mini=True)
            dialog.show()
            toggle_changelog()

    except Exception as e:
        print(f"[{ADDON_NAME}] Error: {e}")
        pass


class CustomDialog(QDialog):
    def __init__(self, parent=None,change_log_text=CHANGE_LOG_TEXT,more_button=False,size_mini=False):
        super().__init__(parent)

        addon_path = dirname(__file__)
        icon = QPixmap(join(addon_path, POPUP_PNG))
        layout = QVBoxLayout()
        if size_mini:
            self.resize(SIZE_MINI_WIDTH, SIZE_MINI_HEIGHT)
        else:
            self.resize(SIZE_BIG_WIDTH, SIZE_BIG_WIDTH)

        pokeball_icon = QIcon(join(addon_path, POKEBALL_PATH))
        self.setWindowIcon(pokeball_icon)

        self.setWindowTitle(THE_ADDON_NAME)


        tab_widget = QTabWidget()
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)


        icon_label = QLabel()
        icon_label.setPixmap(icon)

        hbox = QHBoxLayout()

        change_log_label = QTextBrowser()
        change_log_label.setReadOnly(True)
        change_log_label.setOpenExternalLinks(True)

        # change_log_label.setPlainText(change_log_text)

        escaped_text = change_log_text.replace("\n", "<br>")
        html_content = f"""\
<div style="white-space: pre-wrap;">{escaped_text}</div>
"""
        change_log_label.setHtml(html_content)

        hbox.addWidget(icon_label)
        hbox.addWidget(change_log_label)

        tab_layout.addLayout(hbox)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        from .button_manager import mini_button
        from .shige_addons import add_shige_addons_tab
        from .endroll.endroll import add_credit_tab

        self.yes_button = QPushButton("💖Become a Patron")
        mini_button(self.yes_button )
        self.yes_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.yes_button.clicked.connect(lambda: openLink(PATREON_URL))

        self.report_button = QPushButton("🚨Report")
        self.report_button.clicked.connect(lambda: openLink(
            "https://shigeyukey.github.io/shige-addons-wiki/progress-bar.html#report"))
        self.report_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        mini_button(self.report_button)

        self.no_button = QPushButton("OK (Close)")
        self.no_button.clicked.connect(self.close)
        self.no_button.setFixedWidth(120)

        button_layout.addWidget(self.yes_button)
        button_layout.addWidget(self.report_button)
        button_layout.addWidget(self.no_button)

        tab_widget.addTab(tab, "Change Log")
        add_credit_tab(self, tab_widget)
        add_shige_addons_tab(self, tab_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(tab_widget)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def resizeEvent(self, event:"QResizeEvent"):
        size = event.size()
        print(f"Width: {size.width()}, Height: {size.height()}")
        super().resizeEvent(event)


def toggle_changelog():
    config = _pb_manager.getConfig(__name__)
    config[CHANGE_LOG] = CHANGE_LOG_DAY
    _pb_manager.writeConfig(__name__, config)

# -----------------------------------
