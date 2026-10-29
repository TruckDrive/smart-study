# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
#License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>


def more_info_text():
    from ..shige_pop.popup_config import CHANGE_LOG_TEXT
    change_log = CHANGE_LOG_TEXT.replace("\n", "<br>")
    more_info = (f"""
        {change_log}
        <br>
        Anki Add-on: Progress Bar<br>
        Copyright:<br>
                    (c) Unknown author (nest0r/Ja-Dark?) 2017<br>
                    (c) SebastienGllmt 2017 <https://github.com/SebastienGllmt/><br>
                    (c) Glutanimate 2017-2018 <https://glutanimate.com/><br>
                    (c) liuzikai 2018-2020 <https://github.com/liuzikai><br>
                    (c) BluMist 2022 <https://github.com/BluMist><br>
                    (c) Unknown author 2023<br>
                    (c) Shigeyuki 2024 <https://www.patreon.com/Shigeyuki><br>
        License: GNU AGPLv3 or later <https://www.gnu.org/licenses/agpl.html><br>
        <br>
        """)
    return more_info
