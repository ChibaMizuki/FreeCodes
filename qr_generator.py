import sys
import io
import qrcode
from qrcode.image.styledpil import StyledPilImage
import qrcode.image.svg
from PIL import Image
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
)
from PySide6.QtCore import(
    Signal,
    Qt,
)
from PySide6.QtGui import(
    QImage,
    QPixmap,
)


class QRGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 500, 500)
        self.setWindowTitle("QRGenerator")
        self.editor = QREditor()
        self.editor.show()
        self.editor.gen.connect(self.update_qr)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.show_qr = QLabel()
        self.show_qr.setAlignment(Qt.AlignCenter)
        self.show_qr.setStyleSheet("background: black;")

        # central_widgetの中にshow_qrを入れることにより、デフォルトの空白が適用されて枠ができたように見える？
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.show_qr)

    def update_qr(self, img):
        # QImageとQPixmapの違い
        # https://www.reddit.com/r/QtFramework/comments/d9m17b/the_detailed_differences_between_qimage_and/?tl=ja
        # https://stackoverflow.com/questions/10307860/what-is-the-difference-between-qimage-and-qpixmap
        # 多分QImageはデータをいじるとき、QPixmapは表示するだけの時に使うっぽい？
        # またQImageを挟むことで、生成方法やデータ形式が変わっても対応しやすい点がある？
        pixmap = QPixmap.fromImage(img) # QImageをQPixmapに変換
        self.show_qr.setPixmap(pixmap.scaled(
            self.show_qr.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))

    def closeEvent(self, event):
        self.editor.close()


class QREditor(QDialog):
    gen = Signal(object)

    def __init__(self):
        super().__init__()
        self.resize(600, 400)
        self.setWindowTitle("QREditor")

        layout = QVBoxLayout(self)

        # 文字列入力欄
        input_outside_layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        input_button_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.clear_button = QPushButton("クリア")
        self.clear_button.clicked.connect(self.clear_input)

        input_layout.addWidget(QLabel("QR化したい文字列を入力: "))
        input_layout.addSpacing(10)
        input_layout.addWidget(self.input_field)
        
        input_outside_layout.addLayout(input_layout)
        input_button_layout.addWidget(self.clear_button)
        input_button_layout.addStretch()
        input_outside_layout.addLayout(input_button_layout)

        # ボタン
        button_layout = QHBoxLayout()

        generate_button = QPushButton("作成")
        generate_button.clicked.connect(self.generate_qrcode)
        save_button = QPushButton("保存")

        button_layout.addStretch()
        button_layout.addWidget(generate_button)
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addStretch()

        layout.addLayout(input_outside_layout)
        layout.addLayout(button_layout)

    def generate_qrcode(self):
        data = self.input_field.text()

        if not data:
            return
        # https://github.com/lincolnloop/python-qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=20,
            border=4,
        )

        qr.add_data(data)
        qr.make(fit=True)

        # https://zenn.dev/tamanobi/articles/88dacd450f8405c9a5a9
        # 画像をbytesで保存して渡す例
        img = qr.make_image(fill='black', back_color='white')
        buffer = io.BytesIO() # メモリに仮想ファイルを用意
        img.save(buffer, format="PNG") # 仮想ファイルにPNG形式で保存
        saved_img = QImage.fromData(buffer.getvalue()) # fromdata()で与えられたデータからQImageを構築

        self.gen.emit(saved_img)
        # img.show()
    
    def clear_input(self):
        self.input_field.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qr = QRGenerator()
    qr.show()
    sys.exit(app.exec())
