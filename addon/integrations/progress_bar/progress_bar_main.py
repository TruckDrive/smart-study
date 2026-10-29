# Copyright:
# (c) Unknown author (nest0r/Ja-Dark?) 2017
# (c) SebastienGllmt 2017 <https://github.com/SebastienGllmt/>
# (c) Glutanimate 2017-2018 <https://glutanimate.com/>
# (c) liuzikai 2018-2020 <https://github.com/liuzikai>
# (c) BluMist 2022 <https://github.com/BluMist>
# (c) Unknown author 2023
# (c) Shigeyuki 2024-2026 <https://www.patreon.com/Shigeyuki>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from aqt import mw, gui_hooks

from .path_manager import ADDON_NAME, TYPE_B, TYPE_V3, TYPE_V3_ALL
from .progress_bar_backend import ProgressBarBackend
from .progress_bar_ui import ProgressBarUI



#MARK:ProgressBar
class ProgressBarForAnki:

    def __init__(self):
        self.pb_backend = ProgressBarBackend()
        self.pb_ui = ProgressBarUI()
        self.reload_config()


    #MARK:relad config
    def reload_config(self):
        self.pb_backend._reload_config()
        self.pb_ui._reload_config()

    #MARK:state did change
    def on_state_did_change(self, new_state, old_state):

        if new_state == "resetRequired":
            self.pb_ui.show_waiting()
            return

        if new_state == "deckBrowser":
            if not self.pb_ui.progress_bar:
                self.reload_config()
                self.pb_ui.init_bar()
                self.pb_backend.update_all_decks(True)

            self.pb_backend.del_deck_id()

        elif new_state == "profileManager":
            return

        else:
            self.pb_ui.init_bar()
            self.pb_backend.set_deck_id(mw.col.decks.current()["id"])

        self.pb_backend.update_all_decks(True)
        self.on_update()


    #MARK:change config
    def on_change_config(self, new_state):
        self.reload_config()

        if self.pb_ui.progress_bar:
            self.pb_ui.set_bar_style()

        if new_state == "resetRequired":
            self.pb_ui.show_waiting()
            return

        if new_state == "deckBrowser":
            if not self.pb_ui.progress_bar:
                self.pb_ui.init_bar()
                self.pb_backend.update_all_decks(True)
            self.pb_backend.del_deck_id()

        elif new_state == "profileManager":
            return

        else:
            self.pb_ui.init_bar()
            now_deck_id = mw.col.decks.current()["id"]
            self.pb_backend.set_deck_id(now_deck_id)

        self.pb_backend.update_all_decks(True)

        self.on_update()
        self.pb_ui.check_hide_progressbar()
        self.pb_ui.check_dock_widget_area()


    #MARK:check_hide
    def check_hide_progressbar(self, *args, **kwargs):
        self.pb_ui.check_hide_progressbar()


    #MARK:show_question
    def on_reviewer_did_show_question(self, *args, **kwargs):
        try:
            self.pb_backend.update_all_decks(False)
            self.on_update()

        except Exception as e:
            print(f"[{ADDON_NAME}] Error: {e}")

    #📍
    #MARK:update
    def on_update(self):
        try:

            # V2 (TYPE_B)
            if self.pb_backend.bar_type == TYPE_B:
                bar_status = self.pb_backend.make_type_B_text()

            # V3 (TYPE_V3)
            elif self.pb_backend.bar_type == TYPE_V3:
                bar_status = self.pb_backend.make_type_V3_text()

            # V3-All (TYPE_V3_ALL)
            elif self.pb_backend.bar_type == TYPE_V3_ALL:
                bar_status = self.pb_backend.make_type_V3_text(forced_all_deck=True)

            else: # V1 (TYPE_A)
                bar_status = self.pb_backend.make_type_A_text()

            # ui
            self.pb_ui.update_progress_display(*bar_status)

        except Exception as e:
            print(f"[{ADDON_NAME}] Error: {e}")



#MARK: make PB
progress_bar_for_Anki = ProgressBarForAnki()


#📍use from config
def on_change_config(state):
    progress_bar_for_Anki.on_change_config(state)


#MARK: Hooks
def set_PB_hooks():
    gui_hooks.state_did_change.append(progress_bar_for_Anki.on_state_did_change)
    gui_hooks.reviewer_did_show_question.append(progress_bar_for_Anki.on_reviewer_did_show_question)
    gui_hooks.main_window_did_init.append(progress_bar_for_Anki.check_hide_progressbar)

    # undo
    try:
        from anki.collection import OpChangesAfterUndo
        from aqt import tr

        def on_state_did_undo(changes: OpChangesAfterUndo):
            try:

                if changes.operation == tr.actions_answer_card():
                    progress_bar_for_Anki.pb_backend.on_undo_done()
                    # print(f"[{ADDON_NAME}] > on_undo_done")
                else:
                    print(f"[{ADDON_NAME}] Undo Error: {tr.actions_answer_card()}")

            except Exception as e:
                print(f"[{ADDON_NAME}] Error: {e}")

        gui_hooks.state_did_undo.append(on_state_did_undo)

    except Exception as e:
        print(f"[{ADDON_NAME}] Error: {e}")