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


from aqt import mw
from .._shim import manager as _pb_manager_factory
_pb_manager = _pb_manager_factory('progress_bar')  # Smart Study: own config store
from anki.decks import DeckTreeNode

from .path_manager import ADDON_NAME, TYPE_A



#MARK:backend
class ProgressBarBackend:

    def __init__(self):

        # config
        self.include_review = True
        self.include_learn = True
        self.include_new_after_revs = True

        # weight
        self.weight_new = 2
        self.weight_review = 1
        self.weight_learn = 1

        # data cache
        self.data_remain = {}
        self.data_done = {}
        self.data_total = {}
        self.now_deck_id = None

        self.done_history = []
        self.updated_deck_ids = []


    #MARK:reload_config
    def _reload_config(self):
        config = _pb_manager.getConfig(__name__)

        self.include_new = config.get("includeNew", True)
        self.include_review = config.get("include_review", True)
        self.include_learn = config.get("include_learn", True)


        self.bar_type = config.get("progressbarType", TYPE_A)
        self.show_percent = config.get("showPercent", False)
        self.show_number = config.get("showNumber", False)
        self.show_left_time = config.get("show_left_time", True)
        self.show_left_cards = config.get("show_left_cards", True)

        self.weight_new = config.get("weight_new", 2)
        self.weight_review = config.get("weight_review", 1)
        self.weight_learn = config.get("weight_learn", 1)

        self.include_new_after_revs = config.get("include_new_after_revs", True)
        self.auto_weights = config.get("auto_weights", True)


        try:
            from .time_left import reset_cache
            reset_cache()
        except Exception as e:
            print(f"[{ADDON_NAME}] Error: {e}")


    #MARK:set deck id
    def set_deck_id(self, deck_id):
        self.now_deck_id = deck_id

    #MARK:del deck id
    def del_deck_id(self):
        self.now_deck_id = None


    #MARK:make bar text
    def make_bar_text(self, bar_done, bar_max, bar_remain, counts=None):

        bar_text = ""

        str_cards = ""
        if self.show_number:
            str_cards = f"{bar_done:,} / {bar_max:,}"

        str_percent = ""
        if self.show_percent:
            if bar_max == 0:
                percent = 100
            else:
                percent = int(100 * bar_done / bar_max)
            str_percent = f"{percent:,}%"

        str_left_cards = ""
        if self.show_left_cards:
            # echte Kartenanzahl, nicht die gewichtete Zahl
            left_cards = sum(counts) if counts is not None else bar_remain
            str_left_cards = f"left {left_cards:,} cards"

        str_left_time = ""
        if self.show_left_time:
            try:
                from .time_left import estimate_time_left
                str_left_time = estimate_time_left(bar_remain, counts)
            except Exception as e:
                print(f"[{ADDON_NAME}] Error: {e} ")

        if str_cards:
            if bar_text:
                bar_text += f" | {str_cards}"
            else:
                bar_text += f" {str_cards}"

        if str_percent:
            if bar_text:
                bar_text += f" ({str_percent})"
            else:
                bar_text += f" {str_percent}"

        if str_left_cards:
            if bar_text:
                bar_text += f" | {str_left_cards}"
            else:
                bar_text += f" {str_left_cards}"

        if str_left_time:
            if bar_text:
                bar_text += f" | {str_left_time}"
            else:
                bar_text += f" {str_left_time}"

        return bar_text


    #MARK:cal bar
    def get_now_values(self):

        if self.now_deck_id:
            int_deck_id = self.now_deck_id
            bar_max = self.data_total.get(int_deck_id, 0)
            bar_done = self.data_done.get(int_deck_id, 0)
            return bar_max, bar_done

        bar_max = 0
        bar_done = 0

        for node in mw.col.sched.deck_due_tree().children:
            bar_max += self.data_total.get(node.deck_id, 0)
            bar_done += self.data_done.get(node.deck_id, 0)

        return bar_max, bar_done


    #MARK:typeA
    def make_type_A_text(self):
        bar_max, bar_done = self.get_now_values()

        if bar_max == 0:
            bar_min = 0
            bar_max = 1
            bar_done = 1
        else:
            bar_min = 0
            bar_max = bar_max
            bar_done = bar_done

        bar_remain = max(0, bar_max - bar_done)

        bar_text = self.make_bar_text(bar_done, bar_max, bar_remain)

        return bar_min, bar_max, bar_done, bar_text


    #MARK:typeB
    def make_type_B_text(self):
        day_cutoff = (mw.col.sched.day_cutoff - 86400) * 1000

        query = """
            SELECT
                SUM(CASE
                    WHEN ease >= 1 THEN 1
                    ELSE 0
                END)
            FROM
                revlog
            WHERE
                id > ?
            """

        list_reviewed_cards = mw.col.db.first(query, day_cutoff)
        if list_reviewed_cards and list_reviewed_cards[0] is not None:
            reviewed_cards = list_reviewed_cards[0]
        else:
            reviewed_cards = 0

        bar_total = 0
        bar_done = 0

        for node in mw.col.sched.deck_due_tree().children:
            bar_total += self.data_total.get(node.deck_id, 0)
            bar_done += self.data_done.get(node.deck_id, 0)

        bar_remain = max(0, bar_total - bar_done)
        bar_max = int(bar_remain + reviewed_cards)

        if bar_total == 0 or bar_max <= 0:
            bar_min = 0
            bar_max = 1
            bar_done = 1

        else:
            bar_min = 0
            bar_max = bar_max
            bar_done = reviewed_cards

        bar_text = self.make_bar_text(bar_done, bar_max, bar_remain)

        return bar_min, bar_max, bar_done, bar_text

         
    #MARK:V3
    def make_type_V3_text(self, forced_all_deck=False):

        try:
            current_deck_id = mw.col.decks.current()['id']
        except Exception as e:
            print(f"[{ADDON_NAME}] Error: {e}")
            current_deck_id = None

        if not mw.state in ["overview", "review"]:
            current_deck_id = None

        is_filtered = False
        if current_deck_id and mw.col.decks.is_filtered(current_deck_id):
            is_filtered = True

        if forced_all_deck:
            current_deck_id = None
            is_filtered = False


        def get_child_deck_ids(deck_node:DeckTreeNode):
            child_ids = []
            for child in deck_node.children:
                child_ids.append(child.deck_id)
                child_ids.extend(get_child_deck_ids(child))
            return child_ids

        # get nodes
        node_deck_due_tree = mw.col.sched.deck_due_tree(current_deck_id)

        if current_deck_id:
            list_child_deck_ids = get_child_deck_ids(node_deck_due_tree)
            list_deck_ids = list_child_deck_ids + [current_deck_id]
            deck_ids_tuple = tuple(list_deck_ids)
        else:
            deck_ids_tuple = ()


        if deck_ids_tuple:
            placeholders = ', '.join(['?'] * len(deck_ids_tuple))
            if is_filtered:
                # ﾌｨﾙﾀｰされたﾃﾞｯｷは合算
                deck_ids_placeholder = f"AND (cards.did IN ({placeholders}) OR revlog.type = 3)"
            else:
                deck_ids_placeholder = f"AND cards.did IN ({placeholders})"
        else:
            deck_ids_placeholder = ""

        query = f"""
        SELECT
            COUNT(*)
        FROM
            revlog
        JOIN cards ON revlog.cid = cards.id
        WHERE
            revlog.id > ?
            AND ease > 0
            AND time >= 1
            {deck_ids_placeholder}
        """

        day_cutoff = (mw.col.sched.day_cutoff - 86400) * 1000

        if current_deck_id:
            list_reviewed = mw.col.db.first(
                                query,
                                day_cutoff,
                                *deck_ids_tuple)
        else:
            list_reviewed = mw.col.db.first(
                                query,
                                day_cutoff)

        if list_reviewed and list_reviewed[0] is not None:
            reviewed = list_reviewed[0]
        else:
            reviewed = 0

        # review
        if self.include_review:
            review_remain = int(node_deck_due_tree.review_count or 0)
        else:
            review_remain = 0

        # new
        if self.include_new or (self.include_new_after_revs and review_remain == 0):
            new_remain = int(node_deck_due_tree.new_count or 0)
        else:
            new_remain = 0

        # learn
        if self.include_learn:
            learn_remain = int(node_deck_due_tree.learn_count or 0)
        else:
            learn_remain = 0

        print(f"[{ADDON_NAME}] reviewed: {reviewed} review:{review_remain} lean:{learn_remain} new:{new_remain} ")


        counts = (review_remain, learn_remain, new_remain)

        # Fortschritt in "erwarteten Antworten" (gleiche Einheit wie reviewed),
        # Werte aus der eigenen Historie statt fester Gewichte
        expected = None
        if self.auto_weights:
            try:
                from .time_left import estimate_answers
                expected = estimate_answers(*counts)
            except Exception as e:
                print(f"[{ADDON_NAME}] Error: {e}")

        if expected is not None:
            review_remain, learn_remain, new_remain = int(round(expected)), 0, 0
        else:
            # add weight (fallback) -----------
            review_remain = review_remain * self.weight_review
            new_remain = new_remain * self.weight_new
            learn_remain = learn_remain * self.weight_learn
            # -------------------


        bar_min = 0
        bar_done = reviewed
        bar_remain = review_remain + learn_remain + new_remain
        bar_max = bar_done + bar_remain

        if bar_max <= 0:
            bar_min = 0
            bar_max = 1
            bar_done = 1

        bar_text = self.make_bar_text(bar_done, bar_max, bar_remain, counts)

        return bar_min, bar_max, bar_done, bar_text


    #MARK:get remain
    def get_remain(self, review, learn, new):
        remain = 0

        if self.include_review:
            remain += review * self.weight_review

        if self.include_learn:
            remain += learn * self.weight_learn

        if self.include_new or (self.include_new_after_revs and review == 0):
            remain += new * self.weight_new

        return remain


    #MARK:update decks
    def update_all_decks(self, is_update_total):
        self.updated_deck_ids = [] # undo

        for node in mw.col.sched.deck_due_tree().children:
            self.update_tree(node, is_update_total)

        # undo
        if self.updated_deck_ids:
            self.done_history.append(self.updated_deck_ids.copy())
            # print(f"[{ADDON_NAME}] save batch: {self.updated_deck_ids}")
            if len(self.done_history) > 100:
                self.done_history.pop(0)



    #MARK:update tree
    def update_tree(self, node:"DeckTreeNode", is_update_total):
        remain = self.get_remain(
                                review=node.review_count,
                                learn=node.learn_count,
                                new=node.new_count
                                )

        self.update_deck(
                        deck_id=node.deck_id,
                        remain=remain,
                        is_update_total=is_update_total
                        )

        for node_child in node.children:
            self.update_tree(node_child, is_update_total)

    #MARK:update deck
    def update_deck(self, deck_id, remain, is_update_total):

        if deck_id not in self.data_total:
            self.data_total[deck_id] = remain
            self.data_remain[deck_id] = remain
            self.data_done[deck_id] = 0
            return

        done = self.data_done[deck_id]
        total = self.data_total[deck_id]

        previous_done = done

        self.data_remain[deck_id] = remain

        if is_update_total:
            total = done + remain

        elif remain + done > total:
            total = done + remain

        else:
            done = total - remain

        # undo ---
        if not is_update_total and done > previous_done:
            if deck_id not in self.updated_deck_ids:
                self.updated_deck_ids.append(deck_id)
        #---------

        self.data_total[deck_id] = total
        self.data_done[deck_id] = done


    def on_undo_done(self):
        if not self.done_history:
            return

        deck_ids = self.done_history.pop()
        for deck_id in deck_ids:
            if deck_id in self.data_done:
                self.data_done[deck_id] = max(0, self.data_done[deck_id] - 1)

        # print(f"[{ADDON_NAME}] remove batch: {deck_ids}")
