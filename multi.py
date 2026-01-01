# media_player.pyをpyside6に移植
# ダウンロード後の再生機能は動画単体のみサポート（プレイリストは今後気が向いたら開発）

import os
import sys
import vlc
import yt_dlp
import numpy as np
import cv2
from superqt import QRangeSlider
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
    QLineEdit,
    QDialog,
    QProgressBar,
    QCheckBox,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
    QThread,
)


class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 VLC Player")
        self.resize(1000, 700)
        self.send_filename = None

        self.dl_window = DownloadWindow()
        self.dl_window.hide()
        self.dl_window.video.connect(self.open_file)
        self.make_seq = MakeSequential(video_path=None)
        self.make_seq.hide()
        self.make_video = MakeVideo()
        self.make_video.hide()

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
        self.video_to_seq = file.addAction("Sequential output")
        self.video_to_seq.setDisabled(True)
        self.video_to_seq.triggered.connect(self.open_make_seq_window)
        self.seq_to_video = file.addAction("Convert sequential images to video")
        self.seq_to_video.setDisabled(True)
        self.seq_to_video.triggered.connect(lambda: self.make_video.show())

        dl = menu_bar.addMenu("yt_dlp")
        download = dl.addAction("download")
        download.triggered.connect(lambda: self.dl_window.show())
        self.setMenuBar(menu_bar)
        
        # 再生ボタン
        self.play_button = QPushButton(self.style().standardIcon(QStyle.SP_MediaPlay), "")
        self.play_button.clicked.connect(self.toggle_play)

        # 時間表示
        self.time_label = QLabel("00:00:00 / 00:00:00")

        # シークバー
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.sliderPressed.connect(lambda: self.timer.stop())
        self.slider.sliderMoved.connect(self.slider_move)
        self.slider.sliderReleased.connect(self.slider_release)

        # ループ再生
        # 音量
        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setValue(50)
        self.volume.valueChanged.connect(self.set_volum)


        # 画面サイズ

        # レイアウト合体
        # 動画描画画面とその下で垂直分割
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.video_frame)
        
        # ボタン類を水平分割
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.time_label)
        control_layout.addWidget(self.slider)
        control_layout.addWidget(QLabel("vol"))
        control_layout.addWidget(self.volume)
        
        # レイアウトをまとめて追加
        layout.addLayout(control_layout)

        # UI更新の時間設定
        self.timer = QTimer()
        self.timer.setInterval(500) # 0.5秒ごとにスライダー更新
        self.timer.timeout.connect(self.update_slider)

        self.end_check_timer = QTimer()
        self.end_check_timer.setInterval(100)
        self.end_check_timer.timeout.connect(self.end_check)
        
    # 動画表示
    def open_file(self, fn):
        print(f"filename at open_file: {fn}")
        if not fn:
            filename, _ = QFileDialog.getOpenFileName(self, "Choose Video")
        else:
            filename = str(os.path.abspath(fn))
            print(f"filename (abspath): {filename}")

        if filename:
            self.send_filename = filename
            self.media = self.instance.media_new(filename)
            self.player.set_media(self.media)
            self.player.set_hwnd(self.video_frame.winId())
            self.volume.setValue(50)
            self.player.play()
            self.timer.start()
            self.end_check_timer.start()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.slider.setValue(0)
            self.video_to_seq.setEnabled(True)
            self.seq_to_video.setEnabled(True)

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

    def open_make_seq_window(self):
        self.make_seq = MakeSequential(self.send_filename)
        self.make_seq.show()

    def closeEvent(self, event):
        self.dl_window.close()
        self.make_seq.close()
        self.make_video.close()


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

        clear_button = QPushButton("clear")
        clear_button.setMaximumWidth(80)
        clear_button.clicked.connect(self.clear_url)

        # 保存先設定
        save_path_layout = QHBoxLayout()

        path_label = QLabel("PATH")
        save_path_layout.addWidget(path_label)

        # 内部でパス保持する方の変数
        self.folder_path = self.get_user_download_folder()
        # パスを表示する方の変数
        self.dl_path = QLineEdit(self.folder_path)
        self.dl_path.setReadOnly(True)
        save_path_layout.addSpacing(10)
        save_path_layout.addWidget(self.dl_path)
        save_path_layout.addSpacing(10)

        select_button = QPushButton("select")
        select_button.clicked.connect(self.select_folder)
        save_path_layout.addWidget(select_button)
        save_path_layout.addSpacing(10)

        # ダウンロードボタン
        dl_button = QPushButton("download")
        dl_button.clicked.connect(self.download)

        # 確認チェックボックス
        self.open_after_download = QCheckBox("Open The Video File After Downloading")

        # 進捗表示
        progress_layout = QVBoxLayout()

        self.progress_status = QLabel("Waiting")
        self.progress_status.setAlignment(Qt.AlignCenter)
        self.progress_text = QLabel("Download Status")
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

    def clear_url(self):
        self.video_url.clear()

    @staticmethod
    def get_user_download_folder():
        user_folder = os.path.expanduser("~")
        return os.path.join(user_folder, "Downloads")
    
    def select_folder(self):
        foldername = QFileDialog.getExistingDirectory(self, "select folder")
        if foldername:
            self.folder_path = foldername
            self.dl_path.setText(foldername)

    def download(self):
        if not self.video_url.text():
            QMessageBox.warning(self, "error", "Please Input URL")
        if not self.folder_path:
            QMessageBox.warning(self, "error", "Please Input Folder Path")
        
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
            QMessageBox.warning(self, "error", f"Failed to Download\n{mes}")
        else:
            QMessageBox.information(self, "success", "Finish Download")

    def update_status_message(self, status):
        if status == "started":
            self.progress_status.setText("Preparing for Download")
        elif status == "downloading":
            self.progress_status.setText("Download in Progress")
        elif status == "finished":
            self.progress_status.setText("Download Finished")

    def reset_status_message(self, fn):
        print(f"filename at dialog: {fn}")
        self.progress_status.setText("Waiting")
        self.progress_bar.setValue(0)
        if self.open_after_download.isChecked():
            self.video.emit(fn)
            self.close()

    def update_progress_bar(self, value):
        self.progress_bar.setValue(value)



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
                percent = int(d['downloaded_bytes'] / d['total_bytes'] * 100)
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
            # expected string or bytes-like object, got 'PySide6.QtWidgets.QLineEdit'

class MakeSequential(QDialog):
    def __init__(self, video_path):
        super().__init__()
        self.resize(600, 400)
        self.setWindowTitle("Make Sequential Images From Video")

        layout = QVBoxLayout(self)

        # 開始と終了
        range_layout = QHBoxLayout()
        start_label = QLabel("0")
        end_label = QLabel("100")
        slider = QRangeSlider(Qt.Orientation.Horizontal)
        slider.setValue((0, 100))
        slider.show()

        range_layout.addWidget(start_label)
        range_layout.addWidget(slider)
        range_layout.addWidget(end_label)


        # 処理開始ボタン

        layout.addLayout(range_layout)
        
        if not video_path:
            return 
        video = cv2.VideoCapture(video_path)
        video.release()


class MakeVideo(QDialog):
    def __init__(self):
        super().__init__()
        self.resize(600, 400)
        self.setWindowTitle("Make Video From Sequential Images")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
