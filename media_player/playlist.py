import os
import csv
from PySide6.QtGui import QDrag, QCursor
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QFileDialog,
    QAbstractItemView,
    QListWidgetItem,
)


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
        self.video_list.add.connect(self.add_playlist)
        self.video_list.remove.connect(self.sync_playlist)

        # ボタン
        button_layout = QHBoxLayout()
        self.make_button = QPushButton("新規作成")
        self.make_button.clicked.connect(self.clear_playlist)
        self.read_playlist_button = QPushButton("読込")
        self.read_playlist_button.clicked.connect(self.read_playlist)
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.export_playlist)
        self.play_button = QPushButton("再生")
        self.play_button.clicked.connect(self.send_playlist)

        button_layout.addWidget(self.make_button)
        button_layout.addWidget(self.read_playlist_button)
        button_layout.addWidget(self.save_button)

        layout.addWidget(self.video_list)
        layout.addLayout(button_layout)
        layout.addWidget(self.play_button)
    
    def get_playlist(self, playlist:list):
        self.playlist = playlist
        self.video_list.clear()
        self.update_playlist()

    def read_playlist(self):
        playlist, _ = QFileDialog.getOpenFileName(self, "Choose Playlist", filter="csv (*.csv)")
        if playlist:
            self.playlist = []
            with open(playlist, encoding="UTF-8", newline="") as f:
                reader = csv.reader(f)
                for video in reader:
                    if video and os.path.exists(video[0]):
                        self.playlist.append(video[0])
            self.update_playlist()

    def update_playlist(self):
        self.video_list.clear()
        for v in self.playlist:
            title = os.path.basename(v).split('.')[0]
            item = QListWidgetItem(title)
            item.setData(Qt.UserRole, v)
            self.video_list.addItem(item)

    def clear_playlist(self):
        self.playlist = []
        self.video_list.clear()

    def export_playlist(self):
        self.sync_playlist()
        if not self.playlist:
            QMessageBox.warning(self, "No Playlist", "プレイリストがありません")
            return
        filename, _ = QFileDialog.getSaveFileName(self, "Save", filter="csv (*.csv)")
        if filename:
            with open(filename, mode="w", newline="", encoding="UTF-8") as f:
                writer = csv.writer(f)
                for p in self.playlist:
                    writer.writerow([p])
    
    def send_playlist(self):
        self.sync_playlist()
        if not self.playlist:
            QMessageBox.warning(self, "No Playlist", "プレイリストがありません")
            return
        self.new_playlist.emit(self.playlist)
        self.close()

    def sync_playlist(self):
        new_list = []
        for i in range(self.video_list.count()):
            item = self.video_list.item(i)
            path = item.data(Qt.UserRole)
            new_list.append(path)
        self.playlist = new_list

    def add_playlist(self, video):
        if video in self.playlist:
            QMessageBox.warning(self, "Duplication", "すでに追加済みです")
            return
        self.playlist.append(video)
        title = os.path.basename(video).split('.')[0]
        item = QListWidgetItem(title)
        item.setData(Qt.UserRole, video)
        self.video_list.addItem(item)

class VideoList(QListWidget):
    add = Signal(str)
    remove = Signal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background: black;")
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove) # これでリストのD&Dができるように
        self.setSelectionMode(QAbstractItemView.SingleSelection) # 単体選択のみに

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragEnterEvent(event)
        
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                local_url = url.toLocalFile()
                self.add.emit(local_url)
            event.accept()
        else:
            super().dropEvent(event)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return

        # 親クラスのドラッグ処理（ドロップされるまでここで止まる）
        super().startDrag(supportedActions)

        # --- 判定処理を座標ベースに変更 ---
        
        # 1. マウスの現在のグローバル座標を取得
        global_pos = QCursor.pos()
        
        # 2. ウィジェット内（このQListWidget）の座標系に変換
        local_pos = self.mapFromGlobal(global_pos)

        # 3. 自分の領域（rect）にその座標が含まれているかチェック
        if not self.rect().contains(local_pos):
            # 枠外なら削除処理
            row = self.row(item)
            if row != -1: # アイテムがまだ存在する場合
                print(row)
                self.takeItem(row)
                self.remove.emit()
