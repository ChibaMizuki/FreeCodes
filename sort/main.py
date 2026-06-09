import sys
import random

from bubble import bubble_sort
from merge import merged_history

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsRectItem,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
)

from PySide6.QtGui import (
    QBrush,
    QColor,
)

from PySide6.QtCore import (
    Qt,
    Signal,
    QTimer,
)

BLOCK_SIZE = 10
ARRAY_SIZE = 100

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(BLOCK_SIZE * ARRAY_SIZE + 50, BLOCK_SIZE * ARRAY_SIZE + 50)
        self.setStyleSheet("background-color: black")
        self.scene = QGraphicsScene()
        view = QGraphicsView()
        view.setScene(self.scene)
        self.setCentralWidget(view)

        self.array_size = ARRAY_SIZE + 1
        self.interval = 50
        self.bars = []

        self.get_bubble_index = False

        self.merge_index = 0
        self.merge_history = []

        self.dialog = DialogWindow()
        self.dialog.shfl.connect(self.shuffle_array)
        self.dialog.bbl.connect(self.start_bubble_timer)
        self.dialog.mrg.connect(self.start_merge_timer)
        self.dialog.bg.connect(self.start_bogo_timer)
        self.dialog.stp.connect(self.stop_timer)
        self.dialog.show()

        self.array = [i for i in range(1, self.array_size)]
        random.shuffle(self.array)

        self.set_bars()

        self.bubble_timer = QTimer(self)
        self.bubble_timer.timeout.connect(self.bbl_sort)
        self.merge_timer = QTimer(self)
        self.merge_timer.timeout.connect(self.merge_sort)
        self.bogo_timer = QTimer(self)
        self.bogo_timer.timeout.connect(self.check_bogo_sort)
    
    def set_bars(self):
        self.bars = []
        for i in range(self.array_size - 1):
            bar = Bar(i, self.array[i])
            self.bars.append(bar)
            self.scene.addItem(bar)
    
    # 再配置
    def shuffle_array(self):
        self.scene.clear()

        # バブルソート初期化
        self.get_bubble_index = False

        #マージソート初期化
        self.merge_index = 0
        self.merge_history = []
    
        random.shuffle(self.array)
        self.set_bars()
        self.scene.update()

    # ここからバブルソート
    def start_bubble_timer(self):
        self.set_disabled()
        self.bubble_timer.start(self.interval)

    def bbl_sort(self):
        if not self.get_bubble_index:
            self.bubble_index = bubble_sort(self.array)
            self.get_bubble_index = True
        try:
            a, b = next(self.bubble_index)
            self.change(a, b)
        
        except StopIteration:
            self.bubble_timer.stop()
            self.set_enabled()
            QMessageBox.information(self, "Finish", "ソート完了")
            self.get_bubble_index = False
    
    def change(self, a, b):
        for bar in self.bars:
            bar.setBrush(QBrush(Qt.GlobalColor.white))
        self.bars[a].setBrush(QBrush(Qt.GlobalColor.red))

        a_x = self.bars[a].x()
        b_x = self.bars[b].x()

        self.bars[a].setX(b_x)
        self.bars[b].setX(a_x)

        self.bars[a], self.bars[b] = self.bars[b], self.bars[a]
        self.scene.update()

    # ここからマージソート
    def start_merge_timer(self):
        self.set_disabled()
        self.merge_timer.start(100)

    def merge_sort(self):
        if self.merge_history == []:
            self.merge_history = merged_history(self.array)

        if self.merge_index < len(self.merge_history):
            self.update_bar(self.merge_history[self.merge_index])
            self.scene.update()
            self.merge_index += 1
        else:
            self.merge_timer.stop()
            QMessageBox(self, "Finish", "ソート完了")
            self.set_enabled()

    def update_bar(self, array):
        self.scene.clear()
        self.bars = []
        for i, a in enumerate(array):
            bar = Bar(i, a)
            self.bars.append(bar)
            self.scene.addItem(bar)

    # ここからボゴソート
    def start_bogo_timer(self):
        self.get_bubble_index = False
        self.set_disabled()
        self.bogo_timer.start(100)

    def check_bogo_sort(self):
        ok = [i for i in range(1, self.array_size)]
        if ok != self.array:
            self.shuffle_array()
        else:
            self.bogo_timer.stop()
            self.set_enabled()
            QMessageBox.information(self, "miracle", "ソート完了")

    # タイマー停止
    def stop_timer(self):
        if self.bubble_timer.isActive():
            self.bubble_timer.stop()
        if self.merge_timer.isActive():
            self.merge_timer.stop()
        if self.bogo_timer.isActive():
            self.bogo_timer.stop()
        self.set_enabled()

    # ボタンを押下可能に
    def set_enabled(self):
        self.dialog.shuffle_button.setEnabled(True)
        self.dialog.bubble_button.setEnabled(True)
        self.dialog.merge_button.setEnabled(True)
        self.dialog.bogo_button.setEnabled(True)

    # 不可能に
    def set_disabled(self):
        self.dialog.shuffle_button.setEnabled(False)
        self.dialog.bubble_button.setEnabled(False)
        self.dialog.merge_button.setEnabled(False)
        self.dialog.bogo_button.setEnabled(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

        elif event.key() == Qt.Key_D and not self.dialog.isVisible():
            self.dialog.show()

    def closeEvent(self, event):
        if self.dialog.isVisible():
            self.dialog.close()


class Bar(QGraphicsRectItem):
    def __init__(self, num, val):
        super().__init__()
        self.num = num
        self.val = val
        self.block = BLOCK_SIZE

        self.setRect(
            0, 0,
            self.block,
            self.block * self.val,
        )
        self.setPos(
            self.block * self.num,
            900 - self.block * self.val,
        )
        self.setBrush(QBrush(Qt.GlobalColor.white))


class DialogWindow(QDialog):
    shfl = Signal()
    bbl = Signal()
    mrg = Signal()
    bg = Signal()
    stp = Signal()

    def __init__(self):
        super().__init__()
        self.resize(600, 400)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        self.shuffle_button = QPushButton("再配置")
        self.shuffle_button.clicked.connect(self.shuffle)
        layout.addWidget(self.shuffle_button)

        self.bubble_button = QPushButton("バブルソート")
        self.bubble_button.clicked.connect(self.bubble)
        layout.addWidget(self.bubble_button)

        self.merge_button = QPushButton("マージソート")
        self.merge_button.clicked.connect(self.mrg)
        layout.addWidget(self.merge_button)

        self.bogo_button = QPushButton("ボゴソート")
        self.bogo_button.clicked.connect(self.bogo)
        layout.addWidget(self.bogo_button)

        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self.stop)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def shuffle(self):
        self.shfl.emit()

    def bubble(self):
        self.bbl.emit()

    def bogo(self):
        self.bg.emit()

    def stop(self):
        self.stp.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())