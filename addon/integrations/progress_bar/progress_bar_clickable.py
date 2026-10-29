# Copyright (C) Shigeyuki <http://patreon.com/Shigeyuki>
# License: GNU AGPL version 3 or later <http://www.gnu.org/licenses/agpl.html>

try:
    from PyQt6.QtWidgets import (
        QProgressBar,
        QStyleOptionProgressBar,
    )
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QColor, QMouseEvent, QPainter, QLinearGradient, QBrush, QPainterPath
    from PyQt6.QtWidgets import QStyleOptionProgressBar

except:
    from aqt.qt import (
        QProgressBar,
        QStyleOptionProgressBar,
    )
    from aqt.qt import Qt
    from aqt.qt import QColor, QMouseEvent, QPainter, QLinearGradient, QBrush, QPainterPath
    from aqt.qt import QStyleOptionProgressBar

from aqt import mw

from .path_manager import ADDON_NAME

class ClickableProgressBar(QProgressBar):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.check_error_occurred = False

        self.text_color_inside = "black"
        self.text_color_outside = "white"
        self.border_radius = 0

        self.is_use_custom_patint = True
        self.invertTF = False


    def set_text_colors(
                    self,
                    light_color="black", dark_color="white",
                    main_color="#3399cc", back_color="rgba(0, 0, 0, 0)"):

        if self.is_light_text(main_color):
            self.text_color_inside = light_color
        else:
            self.text_color_inside = dark_color

        if self.is_light_text(back_color):
            self.text_color_outside = light_color
        else:
            self.text_color_outside = dark_color

    def set_border_radius(self, border_radius, invertTF):
        self.border_radius = border_radius
        self.invertTF = invertTF

    def is_dark_mode(self):
        try:
            from aqt.theme import theme_manager
            return theme_manager.night_mode
        except Exception as e:
            print(f"[{ADDON_NAME}] Error: {e} ")
            return True


    def is_light_text(self, color_input):
        try:
            qt_color = QColor(color_input)

            lightness = qt_color.lightness()

            if qt_color.alpha() <= 75:
                # 背景が半透明であればAnkiの色に合わす
                if self.is_dark_mode():
                    return False # Dark
                else:
                    return True # light

            if lightness > 128:
                return True # light

            else:
                return False # Dark

        except Exception as e:
            print(f"[{ADDON_NAME}] Error: {e} ")
            return False


    #MARK:click actions
    def enterEvent(self, event):
        if self.check_error_occurred:
            return

        try:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            super().enterEvent(event)
        except Exception as e:
            self.check_error_occurred = True
            print(f"[{ADDON_NAME}] Error: {e} ")


    def leaveEvent(self, event):
        if self.check_error_occurred:
            return

        try:
            self.unsetCursor()
            super().leaveEvent(event)
        except Exception as e:
            self.check_error_occurred = True
            print(f"[{ADDON_NAME}] Error: {e} ")


    def mousePressEvent(self, event:"QMouseEvent"):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_left_clicked_action()
        super().mousePressEvent(event)

    def on_left_clicked_action(self):
        from .shige_config.progressbar_config import setProgressbarConfig
        setProgressbarConfig()

    def setUseCustomPaint(self, is_enabled):
        self.is_use_custom_patint = is_enabled


    #MARK:paintEvent
    def paintEvent(self, event):
        try:
            if self.check_error_occurred or (not self.is_use_custom_patint):
                super().paintEvent(event)
                return

            qt_painter = QPainter(self)

            # ﾊﾞｰ背景+ﾁｬﾝｸ描画
            qt_style_option_progress_bar = QStyleOptionProgressBar()
            self.initStyleOption(qt_style_option_progress_bar)

            # 状態保持
            is_text_visible = qt_style_option_progress_bar.textVisible
            str_display_text = qt_style_option_progress_bar.text

            # ﾃｷｽﾄ描画ｽｷｯﾌﾟ(ﾃｷｽﾄは反射しない)
            qt_style_option_progress_bar.textVisible = False

            self.style().drawControl(
                            self.style().ControlElement.CE_ProgressBar,
                            qt_style_option_progress_bar,
                            qt_painter,
                            self
                            )

            # 進捗率
            if self.maximum() > self.minimum():
                float_value_ratio = (self.value() - self.minimum()) / (self.maximum() - self.minimum())
            else:
                float_value_ratio = 0

            # rect
            qt_rect = self.rect()

            # 描画範囲
            int_progress_width = int(qt_rect.width() * float_value_ratio)

            if self.invertTF:
                # 反転
                int_progress_width = qt_rect.width() - int_progress_width

            # ﾃｷｽﾄ描画
            if is_text_visible and str_display_text:
                alignment_to_use = Qt.AlignmentFlag.AlignCenter

                # ﾁｬﾝｸ内
                qt_painter.save()
                if self.invertTF:
                    # 反転
                    qt_painter.setClipRect(
                                            int_progress_width, 0,
                                            qt_rect.width() - int_progress_width,
                                            qt_rect.height())
                else:
                    # 通常
                    qt_painter.setClipRect(
                                            0, 0,
                                            int_progress_width,
                                            qt_rect.height())

                color_inside = QColor(self.text_color_inside)
                qt_painter.setPen(color_inside)
                qt_painter.drawText(qt_rect, alignment_to_use, str_display_text)
                qt_painter.restore()

                # ﾁｬﾝｸ外
                qt_painter.save()

                if self.invertTF:
                    # 反転
                    qt_painter.setClipRect(
                                            0, 0,
                                            int_progress_width,
                                            qt_rect.height())
                else:
                    # 通常
                    qt_painter.setClipRect(
                                            int_progress_width, 0,
                                            qt_rect.width() - int_progress_width,
                                            qt_rect.height())

                color_outside = QColor(self.text_color_outside)

                qt_painter.setPen(color_outside)
                qt_painter.drawText(qt_rect, alignment_to_use, str_display_text)
                qt_painter.restore()

            # end
            qt_painter.end()

        except Exception as e:
            self.check_error_occurred = True
            print(f"[{ADDON_NAME}] Error in paintEvent: {e} ")

