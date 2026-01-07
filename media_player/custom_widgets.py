from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSlider
from superqt import QRangeSlider

class NoWheelSlider(QSlider):
    def wheelEvent(self, e):
        e.ignore()


class CustomRangeSlider(QRangeSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bar_moves_all = False

    def wheelEvent(self, e):
        e.ignore()