import sys
import vlc
from PySide6.QtGui import (QAction)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSlider, QFileDialog, QMenuBar, QLabel, QPushButton, QStyle
)
from PySide6.QtCore import Qt, QTimer


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PySide6 VLC Player")
        self.setGeometry(200, 200, 1000, 700)

        # VLCセットアップ
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # ----- UI 設定 -----
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.video_frame = QWidget()
        self.video_frame.setStyleSheet("background: black;")
        self.video_frame.setMinimumHeight(500)

        # 再生ボタン
        self.play_button = QPushButton(self.style().standardIcon(QStyle.SP_MediaPlay), "")
        self.play_button.clicked.connect(self.toggle_play)

        # 時間表示（小さめ）
        self.time_label = QLabel("00:00.00 / 00:00.00")
        self.time_label.setFixedWidth(200)

        # シークバー
        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 1000)
        self.position_slider.sliderMoved.connect(self.slider_moved)
        self.position_slider.sliderReleased.connect(self.slider_released)

        # 音量
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(80)
        self.volume_slider.valueChanged.connect(self.set_volume)

        # レイアウト
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.video_frame)

        controls = QHBoxLayout()
        controls.addWidget(self.play_button)
        controls.addWidget(self.time_label)
        controls.addWidget(self.position_slider)
        controls.addWidget(QLabel("Vol"))
        controls.addWidget(self.volume_slider)

        layout.addLayout(controls)

        # メニューバー
        menu_bar = QMenuBar(self)
        file_menu = menu_bar.addMenu("ファイル")
        open_action = file_menu.addAction("動画を開く")
        open_action.triggered.connect(self.open_file)
        self.setMenuBar(menu_bar)

        # タイマーで UI 更新
        self.timer = QTimer()
        self.timer.setInterval(10)  # 0.01秒更新
        self.timer.timeout.connect(self.update_ui)

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "動画を選択")
        if filename:
            media = self.instance.media_new(filename)
            self.player.set_media(media)

            if sys.platform.startswith("linux"):
                self.player.set_xwindow(self.video_frame.winId())
            elif sys.platform == "win32":
                self.player.set_hwnd(self.video_frame.winId())
            else:
                self.player.set_nsobject(int(self.video_frame.winId()))

            self.player.play()
            self.timer.start()

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.player.play()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def slider_moved(self, value):
        """ドラッグ中も時間ラベルを更新"""
        if self.player.get_length() > 0:
            pos = value / 1000
            ms = pos * self.player.get_length()
            self.time_label.setText(f"{self.format_time(ms)} / {self.format_time(self.player.get_length())}")

    def slider_released(self):
        """離したときに動画をシーク"""
        value = self.position_slider.value() / 1000
        self.player.set_position(value)

    def set_volume(self, value):
        self.player.audio_set_volume(value)

    def update_ui(self):
        if not self.player.is_playing():
            return

        length = self.player.get_length()
        if length > 0:
            pos = self.player.get_position()
            self.position_slider.blockSignals(True)
            self.position_slider.setValue(int(pos * 1000))
            self.position_slider.blockSignals(False)

            cur_ms = pos * length
            self.time_label.setText(f"{self.format_time(cur_ms)} / {self.format_time(length)}")

    def format_time(self, ms):
        sec = int(ms / 1000)
        ms_100 = int((ms % 1000) / 10)
        m = sec // 60
        s = sec % 60
        return f"{m:02}:{s:02}.{ms_100:02}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())