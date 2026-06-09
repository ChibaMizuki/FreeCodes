import sys
import random

from bubble import bubble_sort

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 1000)
        self.setStyleSheet("background-color: black")
        self.scene = QGraphicsScene()
        view = QGraphicsView()
        view.setScene(self.scene)
        self.setCentralWidget(view)

        self.array_size = 31
        self.interval = 50
        self.get_bubble_index = False

        self.dialog = DialogWindow()
        self.dialog.shfl.connect(self.shuffle_array)
        self.dialog.bbl.connect(self.start_bubble_timer)
        self.dialog.bg.connect(self.start_bogo_timer)
        self.dialog.stp.connect(self.stop_timer)
        self.dialog.show()

        self.array = [i for i in range(1, self.array_size)]
        random.shuffle(self.array)

        self.bars = []
        for i in range(self.array_size - 1):
            bar = Bar(i, self.array[i])
            self.bars.append(bar)
            self.scene.addItem(bar)

        self.bubble_timer = QTimer(self)
        self.bubble_timer.timeout.connect(self.bbl_sort)
        self.bogo_timer = QTimer(self)
        self.bogo_timer.timeout.connect(self.check_bogo_sort)
    
    def shuffle_array(self):
        self.scene.clear()
        self.get_bubble_index = False
        random.shuffle(self.array)
        self.bars = []
        for i in range(self.array_size - 1):
            bar = Bar(i, self.array[i])
            self.bars.append(bar)
            self.scene.addItem(bar)
        self.scene.update()

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

    def stop_timer(self):
        if self.bubble_timer.isActive():
            self.bubble_timer.stop()
        if self.bogo_timer.isActive():
            self.bogo_timer.stop()
        self.set_enabled()

    def set_enabled(self):
        self.dialog.shuffle_button.setEnabled(True)
        self.dialog.bubble_button.setEnabled(True)
        self.dialog.bogo_button.setEnabled(True)

    def set_disabled(self):
        self.dialog.shuffle_button.setEnabled(False)
        self.dialog.bubble_button.setEnabled(False)
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
        self.block = 30

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