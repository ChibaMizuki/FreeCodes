import sys
import os
import cv2
import numpy as np
from PySide6.QtWidgets import(
    QApplication,
    QMainWindow,
    QDialog,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QWidget,
    QComboBox,
    QFileDialog,
    QScrollArea,
)
from PySide6.QtCore import(
    Signal,
    Qt,
    QObject,
    QThread,
)
from PySide6.QtGui import(
    QImage,
    QPixmap,
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from color_palette import color_palette

class ShowImageWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 800)
        self.image_pixmap = None
        self.palette_pixmap = None

        self.select = ImageSelect()
        self.select.show()
        self.select.finished.connect(self.show_images)

        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)

        self.image_label = QLabel()
        self.image_label.setStyleSheet("background: black;")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.palette_label = QLabel()
        self.palette_label.setStyleSheet("background: black;")
        self.palette_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.palette_label.setAlignment(Qt.AlignCenter)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.palette_label)
        layout.addWidget(self.image_label, 4) # addWidgetの第2引数で比率指定できるっぽい
        layout.addWidget(self.scroll_area, 1)

    def ndarray_to_qpixmap(self, img:np.ndarray):
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)
    
    def show_images(self, img, palette):
        self.image_pixmap = self.ndarray_to_qpixmap(img)
        self.palette_pixmap = self.ndarray_to_qpixmap(palette)
        self.update_pixmaps()
        
    def update_pixmaps(self):
        if self.image_pixmap:
            self.image_label.setPixmap(
                self.image_pixmap.scaled(
                    self.image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

        if self.palette_pixmap:
            self.palette_label.setPixmap(
                self.palette_pixmap.scaled(
                    self.palette_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_pixmaps()

    def closeEvent(self, event):
        self.select.close()


class ImageSelect(QDialog):
    finished = Signal(np.ndarray, np.ndarray)
    def __init__(self):
        super().__init__()
        self.resize(300, 50)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)

        layout = QHBoxLayout(self)
        button = QPushButton("select")
        colors = [str(x) for x in range(2, 33)]
        self.need_color = QComboBox()
        self.need_color.addItems(colors)
        button.clicked.connect(self.open)
        layout.addWidget(self.need_color)
        layout.addWidget(button)

    def open(self):
        file, _ = QFileDialog.getOpenFileName(self, "select image file")
        if file:
            self.process(file)
    
    def process(self, file):
        def error():
            print("画像の読み込みに失敗しました")

        color_size = self.need_color.currentText()
        self.worker = MedianCutWorker(file, int(color_size))
        self.median_cut_thread = QThread()
        self.worker.moveToThread(self.median_cut_thread)

        self.median_cut_thread.started.connect(self.worker.run)
        self.worker.error.connect(error)
        self.worker.finished.connect(self.finished)
        self.worker.finished.connect(self.median_cut_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.median_cut_thread.finished.connect(self.median_cut_thread.deleteLater)

        self.median_cut_thread.start()


class MedianCutWorker(QObject):
    finished = Signal(np.ndarray, np.ndarray)
    error = Signal()

    def __init__(self, file, num):
        super().__init__()

        self.img = cv2.imread(file)
        if self.img is None:
            self.error.emit()

        self.img = cv2.cvtColor(self.img, cv2.COLOR_BGR2RGB)
        self.need_color = num
        self.color = []
        self.bucket = [np.reshape(self.img, [-1, 3])]

    def rgb_diff(self, color_array:np.ndarray):
        r_max, g_max, b_max = color_array.max(axis=0)
        r_min, g_min, b_min = color_array.min(axis=0)
        r_diff = r_max - r_min
        g_diff = g_max - g_min
        b_diff = b_max - b_min

        max_value = max(r_diff, g_diff, b_diff)
        if r_diff == max_value:
            sort_value = "r"
        elif g_diff == max_value:
            sort_value = "g"
        elif b_diff == max_value:
            sort_value = "b"

        return sort_value

    def three_to_two(self, color_array:np.ndarray):
        return np.reshape(color_array, [-1, 3])

    def two_to_three(self, color_array:np.ndarray, h:int, w:int):
        return np.reshape(color_array, [h, w, 3])

    def sort_colors(self, color_array:np.ndarray, value:str):
        if value == "r":
            color_array = color_array[color_array[:, 0].argsort()]
        elif value == "g":
            color_array = color_array[color_array[:, 1].argsort()]
        elif value == "b":
            color_array = color_array[color_array[:, 2].argsort()]

        return color_array

    def divide_colors(self, color_array:np.ndarray):
        size = color_array.shape[0]
        num = size // 2
        forward = color_array[:num, :]
        backward = color_array[num:, :]
        return forward, backward

    def make_color(self, color_array:np.ndarray):
        color_array = self.three_to_two(color_array)
        num = color_array.shape[0]
        total_rgb = np.sum(color_array, axis=0)
        rgb = np.round((total_rgb / num)).astype(np.uint8)
        rgb = rgb.tolist()
        return rgb

    def median_cut(self, color_bucket:np.ndarray):
        sort_value = self.rgb_diff(color_bucket)
        sorted_color = self.sort_colors(color_bucket, sort_value)
        forward, backward = self.divide_colors(sorted_color)
        return forward, backward

    def get_max_range_index(self, bucket:np.ndarray):
        max_value = []
        for b in bucket:
            r_max, g_max, b_max = b.max(axis=0)
            r_min, g_min, b_min = b.min(axis=0)
            r_diff = r_max - r_min
            g_diff = g_max - g_min
            b_diff = b_max - b_min

            max_value.append(max(r_diff, g_diff, b_diff).item())
        max_range = max(max_value)
        max_index = max_value.index(max_range)
        return max_index

    def color_mapping(self, image:np.ndarray, color_palette:np.ndarray):
        h, w, _ = image.shape
        img = image.reshape(-1, 3).astype(np.int32) # (h*w, 3)
        pal = color_palette.astype(np.int32) # (need_color, 3)

        diff = img[:, None, :] - pal[None, :, :] # numpyのブロードキャストという考え方
        dist = np.sum(diff ** 2, axis=2)
        nearest = np.argmin(dist, axis=1) # axis1方向に色との距離が並んでいる

        quantized = pal[nearest].astype(np.uint8)
        return quantized.reshape(h, w, 3)
    
    def run(self):
        while len(self.bucket) < self.need_color:
            index = self.get_max_range_index(self.bucket)
            max_range_bucket = self.bucket.pop(index)

            forward, backward = self.median_cut(max_range_bucket)
            self.bucket.append(forward)
            self.bucket.append(backward)

        for i in range(len(self.bucket)):
            self.color.append(self.make_color(self.bucket[i]))
        self.color = np.array(self.color, dtype=np.uint8)
        self.color = self.color[self.color[:, 0].argsort()]

        quantized_img = self.color_mapping(self.img, self.color)
        # quantized_img = cv2.cvtColor(quantized_img, cv2.COLOR_RGB2BGR)

        self.color = self.color.tolist()
        palette = color_palette(self.color, mode="h")


        self.finished.emit(quantized_img, palette)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    image = ShowImageWindow()
    image.show()
    sys.exit(app.exec())

