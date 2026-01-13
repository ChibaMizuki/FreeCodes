import os
import csv
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QFileDialog,
)

from constants import USER_DOWNLOAD_FOLDER

class MakePlaylist(QDialog):
    new_playlist = Signal(list)

    def __init__(self):
        super().__init__()
        self.resize(400, 600)
        self.setWindowTitle("Playlist")
        self.setAcceptDrops(True)
        self.setWindowModality(Qt.ApplicationModal)
        self.playlist = []

        layout = QVBoxLayout(self)

        # ファイル表示
        self.video_list = VideoList()
        self.video_list.add.connect(self.update_playlist)

        # ボタン
        button_layout = QHBoxLayout()
        self.make_button = QPushButton("新規作成")
        self.make_button.clicked.connect(self.clear_playlist)
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.export_playlist)
        self.play_button = QPushButton("再生")
        self.play_button.clicked.connect(self.send_playlist)

        button_layout.addWidget(self.make_button)
        button_layout.addWidget(self.save_button)

        layout.addWidget(self.video_list)
        layout.addLayout(button_layout)
        layout.addWidget(self.play_button)
    
    def get_playlist(self, playlist:list):
        self.playlist = playlist
        self.video_list.clear()
        self.add_playlist()

    def add_playlist(self):
        for v in self.playlist:
            title = os.path.basename(v).split('.')[0]
            self.video_list.addItem(title)

    def clear_playlist(self):
        self.playlist = []
        self.video_list.clear()

    def export_playlist(self):
        if not self.playlist:
            QMessageBox.warning(self, "No Playlist", "プレイリストがありません")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Save", filter="csv (*.csv)")
        if filename:
            with open(filename, mode="w", newline="", encoding="UTF-8") as f:
                writer = csv.writer(f, delimiter="\n")
                writer.writerow(self.playlist)
    
    def send_playlist(self):
        if not self.playlist:
            QMessageBox.warning(self, "No Playlist", "プレイリストがありません")
            return
        self.new_playlist.emit(self.playlist)
        self.close()
    
    def update_playlist(self, video):
        if video in self.playlist:
            QMessageBox.warning(self, "Duplication", "すでに追加済みです")
            return
        self.playlist.append(video)
        title = os.path.basename(video).split('.')[0]
        self.video_list.addItem(title)

class VideoList(QListWidget):
    add = Signal(str)

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: black;")
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()

    def dropEvent(self, event):
        url = event.mimeData().urls()
        local_url = url[0].toLocalFile()
        self.add.emit(local_url)