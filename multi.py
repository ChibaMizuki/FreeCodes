# media_player.pyをpyside6に移植

import vlc
import yt_dlp
import os
import sys
import threading
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox,
    QStyle,
    QLabel,
    QSizePolicy,
    QSlider,
    QMenuBar,
    QFileDialog,
)
from PySide6.QtCore import Qt, QTimer


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 VLC Player")
        self.setGeometry(200, 200, 1000, 700)

        # VLC初期化
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
    
        # UI
        central_widget = QWidget() # 画面全体のUI土台
        self.setCentralWidget(central_widget)
        
        self.video_frame = QWidget() # 動画表示の土台
        self.video_frame.setStyleSheet("background: black;")
        size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # 最大限充填
        self.video_frame.setSizePolicy(size_policy) 
        
        # メニューバー
        menu_bar = QMenuBar(self)
        file = menu_bar.addMenu("file")
        file_open = file.addAction("open file")
        file_open.triggered.connect(self.open_file)
        dl = menu_bar.addMenu("yt_dlp")
        download = dl.addAction("download")
        self.setMenuBar(menu_bar)
        
        # 再生ボタン
        self.play_button = QPushButton(self.style().standardIcon(QStyle.SP_MediaPlay), "")
        self.play_button.clicked.connect(self.toggle_play)

        # 時間表示
        self.time_label = QLabel("00:00:00 / 00:00:00")

        # シークバー
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.sliderPressed.connect(self.slider_press)
        self.slider.sliderMoved.connect(self.slider_move)
        self.slider.sliderReleased.connect(self.slider_release)

        # ループ再生
        # 音量
        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(50)
        self.volume.valueChanged.connect(self.set_volum)

        # yt_dlp
        # 画面サイズ

        # レイアウト合体
        # 動画描画画面とその下で垂直分割
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.video_frame)
        
        # ボタン類を水平分割
        control = QHBoxLayout()
        control.addWidget(self.play_button)
        control.addWidget(self.time_label)
        control.addWidget(self.slider)
        control.addWidget(QLabel("vol"))
        control.addWidget(self.volume)
        
        # レイアウトをまとめて追加
        layout.addLayout(control)

        # UI更新の時間設定
        self.timer = QTimer()
        self.timer.setInterval(500) # 0.5秒ごとにスライダー更新
        self.timer.timeout.connect(self.update_slider)

        self.end_check_timer = QTimer()
        self.end_check_timer.setInterval(100)
        self.end_check_timer.timeout.connect(self.end_check)
        
    # 動画表示
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "動画を選択")
        if filename:
            self.media = self.instance.media_new(filename)
            self.player.set_media(self.media)
            self.player.set_hwnd(self.video_frame.winId())
            self.volume.setValue(50)
            self.player.play()
            self.timer.start()
            self.end_check_timer.start()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.slider.setValue(0)

    def toggle_play(self):
        if self.player.is_playing():
            self.player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.player.play()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def set_volum(self, value):
        self.player.audio_set_volume(value)

    def update_slider(self):
        if not self.player.is_playing():
            return
        length = self.player.get_length()
        if length > 0:
            pos = self.player.get_position() # 0~1の小数値を取得
            self.slider.setValue(int(pos * 1000)) # スライダーが0~1000で設定したため1000倍

            current_time = length * pos # ms
            self.time_label.setText(f"{self.format_time(current_time)} / {self.format_time(length)}")

    def format_time(self, ms):
        sec = int(ms / 1000)
        ms = int((ms % 1000) / 10)
        s = sec % 60
        m = sec // 60
        return f"{m:02}:{s:02}.{ms:02}"
    
    def slider_press(self):
        self.timer.stop()

    def slider_move(self, value):
        if self.player.get_length() > 0:
            pos = value / 1000
            ms = pos * self.player.get_length()
            self.time_label.setText(f"{self.format_time(ms)} / {self.format_time(self.player.get_length())}")
    
    def slider_release(self):
        value = self.slider.value() / 1000
        if value >= 1:
            value = 0.99 # 終了判定を巻き込まないために
        self.player.set_position(value)
        self.timer.start()

    def end_check(self):
        if self.player.get_state() == vlc.State.Ended:
            self.player.set_media(self.media)
            self.player.set_position(0)
            self.slider.setValue(0)
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
