import os
import yt_dlp
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox,
    QProgressBar, QCheckBox, QFileDialog
)

from constants import USER_DOWNLOAD_FOLDER


class DownloadWindow(QDialog):
    success = Signal()
    error = Signal(str)
    video = Signal(str)

    def __init__(self):
        super().__init__()
        self.resize(600, 400)
        self.setWindowTitle("Download")

        layout = QVBoxLayout(self)

        # URL入力欄
        video_url_layout = QHBoxLayout()

        url_label = QLabel("URL: ")
        video_url_layout.addWidget(url_label)

        self.video_url = QLineEdit()
        video_url_layout.addSpacing(10)
        video_url_layout.addWidget(self.video_url)
        video_url_layout.addSpacing(10)

        clear_button = QPushButton("クリア")
        clear_button.setMaximumWidth(80)
        clear_button.clicked.connect(lambda: self.video_url.clear())

        # 保存先設定
        save_path_layout = QHBoxLayout()

        path_label = QLabel("保存先")
        save_path_layout.addWidget(path_label)

        # 内部でパス保持する方の変数
        self.folder_path = USER_DOWNLOAD_FOLDER
        # パスを表示する方の変数
        self.dl_path = QLineEdit(self.folder_path)
        self.dl_path.setReadOnly(True)
        save_path_layout.addSpacing(10)
        save_path_layout.addWidget(self.dl_path)
        save_path_layout.addSpacing(10)

        select_button = QPushButton("選択")
        select_button.clicked.connect(self.select_folder)
        save_path_layout.addWidget(select_button)
        save_path_layout.addSpacing(10)

        # ダウンロードボタン
        dl_button = QPushButton("ダウンロード")
        dl_button.clicked.connect(self.download)

        # 確認チェックボックス
        self.open_after_download = QCheckBox("ダウンロード後に動画を再生する")

        # 進捗表示
        progress_layout = QVBoxLayout()

        self.progress_status = QLabel("待機中")
        self.progress_status.setAlignment(Qt.AlignCenter)
        self.progress_text = QLabel("ダウンロード状況")
        self.progress_text.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_text)
        progress_layout.addWidget(self.progress_status)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        # レイアウト合体
        layout.addSpacing(20)
        layout.addLayout(video_url_layout)
        layout.addSpacing(20)
        layout.addWidget(clear_button)
        layout.addSpacing(20)
        layout.addLayout(save_path_layout)
        layout.addStretch()
        layout.addWidget(self.open_after_download)
        layout.addStretch()
        layout.addLayout(progress_layout)
        layout.addStretch()
        layout.addWidget(dl_button)
    
    def select_folder(self):
        foldername = QFileDialog.getExistingDirectory(self, "select folder")
        if foldername:
            self.folder_path = foldername
            self.dl_path.setText(foldername)

    def download(self):
        if not self.video_url.text():
            QMessageBox.warning(self, "error", "URLを入力してください")
        if not self.folder_path:
            QMessageBox.warning(self, "error", "保存先を設定してください")
        
        os.makedirs(self.folder_path, exist_ok=True)
        
        self.download_process = downloadThread(self, self.video_url.text(), self.folder_path)
        self.download_process.error.connect(self.show_messege)
        self.download_process.success.connect(self.show_messege)
        self.download_process.progress.connect(self.update_progress_bar)
        self.download_process.status.connect(self.update_status_message)
        self.download_process.finished.connect(self.reset_status_message)
        self.download_process.start()

    def show_messege(self, mes=None):
        if mes != None:
            QMessageBox.warning(self, "error", f"ダウンロード失敗\n{mes}")
        else:
            QMessageBox.information(self, "success", "ダウンロード終了")

    def update_status_message(self, status):
        if status == "started":
            self.progress_status.setText("ダウンロード準備中")
        elif status == "downloading":
            self.progress_status.setText("ダウンロード中")
        elif status == "finished":
            self.progress_status.setText("Dダウンロード完了")

    def reset_status_message(self, fn):
        print(f"filename at dialog: {fn}")
        self.progress_status.setText("待機中")
        self.progress_bar.setValue(0)
        if self.open_after_download.isChecked():
            self.video.emit(fn)
            self.close()

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)


# QThread継承形式（非推奨らしい？）
class downloadThread(QThread):
    error = Signal(str)
    success = Signal()
    progress = Signal(int)
    status = Signal(str)
    finished = Signal(str)

    def __init__(self, dl_window ,url, folder):
        super().__init__()
        self.dl_window = dl_window
        self.url = url
        self.folder = folder
    
    def run(self):
        self.status.emit("started")
        def progress_hook(d):
            if d['status'] == 'downloading':
                # _percent_strはただの文字列じゃなくて装飾文字だから扱える代物じゃなかった
                total = d.get("total_bytes") or d.get("total_bytes_estimate")
                if total:
                    percent = int(d["downloaded_bytes"] / total * 100)
                self.progress.emit(percent)
                self.status.emit("downloading")
            elif d['status'] == 'finished':
                self.status.emit("finished")

        ydl_opts = {
            "format": "bv*+ba/b", # bestvideoとbestaudio or best video&audioをダウンロード
            "remote_components": ["ejs:github"], # Denoインストール必須
            "outtmpl": os.path.join(self.folder, '%(title)s.%(ext)s'),
            "progress_hooks": [progress_hook],
            "merge_output_format": "mp4",
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # ydl.download([self.url])
                info = ydl.extract_info(self.url, download=True)
                filename = ydl.prepare_filename(info)
                print(filename)
            self.success.emit()
            self.finished.emit(filename)
        except Exception as e:
           self.error.emit(e)
            # QThread内でメッセージボックスなどUIをいじるとエラーが生じる
            # 例: expected string or bytes-like object, got 'PySide6.QtWidgets.QLineEdit'
