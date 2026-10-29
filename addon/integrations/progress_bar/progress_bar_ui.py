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

try:
    from PyQt6.QtWidgets import QDockWidget, QStyleFactory, QWidget
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QColor, QPalette

except:
    from aqt.qt import QDockWidget, QStyleFactory, QWidget
    from aqt.qt import Qt
    from aqt.qt import QColor, QPalette

from .progress_bar_clickable import ClickableProgressBar



#MARK:ui
class ProgressBarUI:
    def __init__(self):
        self.orientation = Qt.Orientation.Horizontal
        self.progress_bar = None
        self.dock_widget = None

        self.is_mw_setStyleSheet_run = False


    #MARK:reload_config
    def _reload_config(self):
        config = _pb_manager.getConfig(__name__)

        self.show_percent = config.get("showPercent", False)
        self.show_number = config.get("showNumber", False)
        self.text_color = config.get("textColor", "aliceblue")
        self.background_color = config.get("backgroundColor", "rgba(0, 0, 0, 0)")
        self.foreground_color = config.get("foregroundColor", "#3399cc")
        self.border_radius = config.get("borderRadius", 0)
        self.max_width = config.get("maxWidth", "5px")
        self.invertTF = config.get("invertTF", False)
        self.use_gradation = config.get("use_gradation", True)
        self.chunk_color_left = config.get("chunk_color_left", "#3399cc")
        self.chunk_color_center = config.get("chunk_color_center", "#4cedff")
        self.chunk_color_right = config.get("chunk_color_right", "#3399cc")
        self.hide_progressbar_flag = config.get("hide_Progressbar", False)

        self.text_color_inside = config.get("text_color_light", "black")
        self.text_color_outside = config.get("text_color_dark", "white")


        self.show_progress_bar_on_bottom = config.get("show_progress_bar_on_bottom", False)
        if self.show_progress_bar_on_bottom:
            self.dock_area = Qt.DockWidgetArea.BottomDockWidgetArea
        else:
            self.dock_area = Qt.DockWidgetArea.TopDockWidgetArea

        self.style_name = config.get("style_name", "")

        self.on_bar_style_change()


    #MARK: Apply Changes
    def on_bar_style_change(self):
        self.qt_style_factory = QStyleFactory.create(self.style_name)

        self.qt_palette = self.make_qt_palette()
        self.restrict_size = self.make_bar_size()


    def make_qt_palette(self):
        qt_palette = QPalette()
        qt_palette.setColor(QPalette.ColorRole.Base, QColor(self.background_color))
        qt_palette.setColor(QPalette.ColorRole.Highlight, QColor(self.foreground_color))
        qt_palette.setColor(QPalette.ColorRole.Button, QColor(self.background_color))
        qt_palette.setColor(QPalette.ColorRole.WindowText, QColor(self.text_color))
        qt_palette.setColor(QPalette.ColorRole.Window, QColor(self.background_color))
        return qt_palette


    def make_bar_size(self):
        str_restrict_size = ""
        if not self.max_width:
            return str_restrict_size

        if self.orientation == Qt.Orientation.Horizontal:
            str_restrict_size = f"height: {self.max_width}; max-height: {self.max_width};"
            return str_restrict_size

        str_restrict_size = f"width: {self.max_width}; max-width: {self.max_width};"

        return str_restrict_size


    #MARK: init Bar
    def init_bar(self):
        if not self.progress_bar:
            self.progress_bar = ClickableProgressBar()
            self.make_qt_dock_widget(self.progress_bar)

        is_text_visible = self.show_percent or self.show_number

        self.progress_bar.setTextVisible(is_text_visible)
        self.progress_bar.setInvertedAppearance(self.invertTF)
        self.progress_bar.setOrientation(self.orientation)

        self.set_bar_style()

        self.on_main_window_style()


    def make_qt_dock_widget(self, progress_bar):
        self.dock_widget = QDockWidget()
        self.dock_widget.setWidget(progress_bar)
        self.dock_widget.setTitleBarWidget(QWidget())

        self.on_rearrange_dock_widget(self.dock_area)

        if self.border_radius > 0 or self.qt_style_factory is not None:
            mw.setPalette(self.qt_palette)

        mw.web.setFocus()

        return self.dock_widget



    #MARK:style
    def set_bar_style(self):
        if not self.progress_bar:
            return

        if self.qt_style_factory is None:

            if self.use_gradation:
                str_chunk_background = (
                    f"background: QLinearGradient("
                    f"x1: 0, y1: 0, x2: 1, y2: 0, "
                    f"stop: 0 {self.chunk_color_left}, "
                    f"stop: 0.5 {self.chunk_color_center}, "
                    f"stop: 1 {self.chunk_color_right}"
                    f");"

                    f"border-top: 1px solid {self.chunk_color_left};"
                    f"border-left: 1px solid {self.chunk_color_left};"
                    f"border-right: 1px solid {self.chunk_color_right};"
                    f"border-bottom: 1px solid {self.chunk_color_right};"
                )
                bar_color_main = self.chunk_color_center

            else:
                str_chunk_background = (
                    f"background-color: {self.foreground_color};"
                    )
                bar_color_main = self.foreground_color



            str_background_border = (
                f"border-top: 1px solid rgba(0, 0, 0, 0.1);"
                f"border-left: 1px solid rgba(0, 0, 0, 0.1);"
                f"border-right: 1px solid rgba(255, 255, 255, 0.1);"
                f"border-bottom: 1px solid rgba(255, 255, 255, 0.1);"
            )

            str_stylesheet = f"""
                QProgressBar
                {{
                    color:{self.text_color};
                    background-color: {self.background_color};
                    border-radius: {self.border_radius}px;
                    {str_background_border}
                    {self.restrict_size}
                }}
                QProgressBar::chunk
                {{
                    {str_chunk_background}
                    margin: 0px;
                    border-radius: {self.border_radius}px;
                }}
                """

            self.progress_bar.setStyleSheet(str_stylesheet)

            self.progress_bar.set_text_colors(
                                            self.text_color_inside,
                                            self.text_color_outside,
                                            bar_color_main,
                                            self.background_color,)
            self.progress_bar.set_border_radius(self.border_radius,
                                                self.invertTF)


            self.progress_bar.setUseCustomPaint(True)

        else:
            self.progress_bar.setStyleSheet("")
            self.progress_bar.setStyle(self.qt_style_factory)

            self.progress_bar.setPalette(self.qt_palette)
            self.progress_bar.set_border_radius(self.border_radius,
                                                self.invertTF)

            self.progress_bar.setUseCustomPaint(False)

            # self.progress_bar.style().unpolish(self.progress_bar)
            # self.progress_bar.style().polish(self.progress_bar)
            # self.progress_bar.update()




    #MARK: Dock Widget
    def on_rearrange_dock_widget(self, dock_area):

        list_existing_widgets = []
        for widget in mw.findChildren(QDockWidget, options=Qt.FindChildOption.FindDirectChildrenOnly):
            if mw.dockWidgetArea(widget) == dock_area:
                list_existing_widgets.append(widget)

        mw.addDockWidget(dock_area, self.dock_widget)

        if list_existing_widgets:
            mw.setDockNestingEnabled(True)

            list_dock_area = [
                Qt.DockWidgetArea.TopDockWidgetArea,
                Qt.DockWidgetArea.BottomDockWidgetArea
                ]

            if dock_area in list_dock_area:
                orientation = Qt.Orientation.Vertical
            else:
                orientation = Qt.Orientation.Horizontal

            mw.splitDockWidget(
                    list_existing_widgets[0],
                    self.dock_widget,
                    orientation)



    #MARK:check area
    def check_dock_widget_area(self):
        if not isinstance(self.dock_widget, QDockWidget):
            return

        dock_area_now = mw.dockWidgetArea(self.dock_widget)
        dock_area_new = self.dock_area

        if dock_area_now == dock_area_new:
            return

        mw.removeDockWidget(self.dock_widget)
        self.on_rearrange_dock_widget(dock_area_new)
        self.dock_widget.show()


    def update_progress_display(self, progress_min, progress_max, progress_value, text):
        self.init_bar()
        self.progress_bar.setRange(progress_min, progress_max)
        self.progress_bar.setValue(progress_value)
        self.progress_bar.setFormat(text)


    def show_waiting(self):
        if not self.progress_bar:
            return

        self.progress_bar.setRange(0, 0)
        if self.show_number:
            self.progress_bar.setFormat("Waiting...")


    #MARK:mw style
    def on_main_window_style(self):
        if not self.is_mw_setStyleSheet_run:
            mw.setStyleSheet(
                """
            QMainWindow::separator
            {
                width: 2px;
                height: 2px;
            }
            """)
            self.is_mw_setStyleSheet_run = True


    def check_hide_progressbar(self):
        if not self.progress_bar:
            return

        self.progress_bar.setVisible(not self.hide_progressbar_flag)

