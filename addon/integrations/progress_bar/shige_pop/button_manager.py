from aqt import QPushButton, QSizePolicy

def mini_button(button:QPushButton):
    button.setStyleSheet("QPushButton { padding: 2px; }")
    button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)