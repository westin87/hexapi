from PyQt5.QtWidgets import QToolBar, QLabel, QComboBox
import functools


class ModeSelectionToolbar(QToolBar):
    def __init__(self, switch_mode_callback):
        super().__init__("Mode selection")

        mode_text = QLabel()
        mode_text.setText("Select mode:")

        self._mode_selection = QComboBox()
        self._mode_selection.setMinimumWidth(100)
        self._mode_selection.setMaximumWidth(140)
        self._mode_selection.addItem("RC")
        self._mode_selection.addItem("GPS")

        self.addWidget(mode_text)
        self.addWidget(self._mode_selection)

        self.addAction(
            "Select", functools.partial(
                switch_mode_callback, self._mode_selection.currentText))
