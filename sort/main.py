import sys
import random

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
)

from PySide6.QtGui import (
    QBrush,
    QColor,
)

from PySide6.QtCore import (
    Qt,
    Signal,
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

        self.dialog = DialogWindow()
        self.dialog.change.connect(self.change)
        self.dialog.show()

        array = [i for i in range(1, self.array_size)]
        random.shuffle(array)
        self.bars = []
        for i in range(self.array_size - 1):
            bar = Bar(i, array[i])
            self.bars.append(bar)
            self.scene.addItem(bar)
    
    def change(self):
        a = 5
        b = 10
        a_x = self.bars[a].pos().x()
        a_y = self.bars[a].pos().y()
        b_x = self.bars[b].pos().x()
        b_y = self.bars[b].pos().y()
        self.bars[a].setPos(b_x, a_y)
        self.bars[b].setPos(a_x, b_y)

        self.bars[a], self.bars[b] = self.bars[b], self.bars[a]
        self.scene.update()

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
    change = Signal()

    def __init__(self):
        super().__init__()
        self.resize(600, 400)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        self.bubble_button = QPushButton("change")
        self.bubble_button.clicked.connect(self.bubble)
        layout.addWidget(self.bubble_button)


        self.setLayout(layout)

    def bubble(self):
        self.change.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())