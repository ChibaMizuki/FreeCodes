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
)
from PySide6.QtCore import Qt, QTimer


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 VLC Player")
        self.setGeometry(200, 200, 1000, 700)
    
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
        dl = menu_bar.addMenu("yt_dlp")
        download = dl.addAction("download")
        self.setMenuBar(menu_bar)
        
        # 再生ボタン
        self.play_button = QPushButton(self.style().standardIcon(QStyle.SP_MediaPlay), "")
        # 時間表示
        self.time_label = QLabel("00:00:00 / 00:00:00")
        # シークバー
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        # ループ再生
        # 音量
        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(50)
        # yt_dlp
        # 画面サイズ
        # レイアウト合体
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.video_frame)
        
        control = QHBoxLayout()
        control.addWidget(self.play_button)
        control.addWidget(self.time_label)
        control.addWidget(self.slider)
        control.addWidget(QLabel("vol"))
        control.addWidget(self.volume)
        
        layout.addLayout(control)
        
    # 動画表示
    def vlc(self, url):
        instance = vlc.Instance()
        self.player = instance.media_player_new()
        media = instance.media_new(url)
        self.player.set_media(media)
        self.player.set_hwnd(self.canvas.winfo_id())
        self.player.play()
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
