# media_player.pyをpyside6に移植
# ダウンロード後の再生機能は動画単体のみサポート（プレイリストは今後気が向いたら開発）

import os
import sys
import time
import glob
import tempfile
import cv2
import vlc
import yt_dlp
import numpy as np
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
    QRadioButton,
    QSpinBox,
    QComboBox,
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
    Slot,
    QThread,
    QObject,
)

USER_DOWNLOAD_FOLDER = os.path.join(
    os.path.expanduser("~"),
    "Downloads"
)


# スクロール無効のスライダーにカスタム
# eventfilterを使用した書き方もあるっぽい？
class NoWheelSlider(QSlider):
    def wheelEvent(self, e):
        e.ignore()


class CustamRangeSlider(QRangeSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bar_moves_all = False

    def wheelEvent(self, e):
        e.ignore()



class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 VLC Player")
        self.resize(1000, 700)
        self.media = None
        self.send_filename = None
        self.tmp = None

        self.dl_window = DownloadWindow()
        self.dl_window.hide()
        self.dl_window.video.connect(self.open_file)
        self.make_seq = MakeSeqWindow(video_path=None)
        self.make_seq.hide()
        self.make_video = MakeVideoWindow()
        self.make_video.hide()
        self.make_video.temp_video.connect(self.temp_video_process)
        self.make_video.saved_video.connect(self.open_file)

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
        self.slider = NoWheelSlider(Qt.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.sliderPressed.connect(lambda: self.timer.stop())
        self.slider.sliderMoved.connect(self.slider_move)
        self.slider.sliderReleased.connect(self.slider_release)

        # ループ再生
        # 音量
        self.mute = False
        self.mute_button = QPushButton(self.style().standardIcon(QStyle.SP_MediaVolume), "")
        self.mute_button.clicked.connect(self.set_mute)
        self.volume = NoWheelSlider(Qt.Horizontal)
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
        control_layout.addWidget(self.mute_button)
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
    def open_file(self, fn=None, *args, **kwargs):
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
            self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
            self.volume.setValue(50)
            self.player.play()
            self.mute = False
            self.player.audio_set_mute(False)
            self.timer.start()
            self.end_check_timer.start()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.slider.setValue(0)
            self.video_to_seq.setEnabled(True)
            self.seq_to_video.setEnabled(True)

    def toggle_play(self):
        state = self.player.get_state()
        if not self.media:
            self.open_file(fn=None)
        elif state == vlc.State.Playing:
            self.player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.player.play()
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def set_volum(self, value):
        self.player.audio_set_volume(value)

    def set_mute(self):
        if not self.mute:
            self.mute = True
            self.player.audio_set_mute(True)
            self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolumeMuted))
        elif self.mute:
            self.mute = False
            self.player.audio_set_mute(False)
            self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))

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
        self.make_seq = MakeSeqWindow(self.send_filename)
        self.make_seq.show()

    def temp_video_process(self, path):
        self.clean_temp_file()
        self.tmp = path
        self.open_file(fn=self.tmp)

    def clean_temp_file(self):
        if self.player:
            self.player.stop()
            self.player.set_media(None)
        if self.tmp and os.path.exists(self.tmp):
            try:
                os.remove(self.tmp)
                print(f"{self.tmp} is exist: {os.path.exists(self.tmp)}")
            except PermissionError as e:
                print(f"Failed to Delete TempFile: {e}")
            self.tmp = None

    def closeEvent(self, event):
        print(self.tmp)
        self.clean_temp_file()
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
        clear_button.clicked.connect(lambda: self.video_url.clear())

        # 保存先設定
        save_path_layout = QHBoxLayout()

        path_label = QLabel("PATH")
        save_path_layout.addWidget(path_label)

        # 内部でパス保持する方の変数
        self.folder_path = USER_DOWNLOAD_FOLDER
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
            # 例: expected string or bytes-like object, got 'PySide6.QtWidgets.QLineEdit'

class MakeSeqWindow(QDialog):
    def __init__(self, video_path):
        super().__init__()
        if not video_path:
            return

        self.resize(600, 400)
        self.setWindowTitle("Make Sequential Images From Video")

        self.video = cv2.VideoCapture(video_path)
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.total_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.length = self.total_frames / self.fps

        layout = QVBoxLayout(self)

        # 動画情報
        video_info_layout = QHBoxLayout()
        fps_label = QLabel(f"fps: {round(self.fps, 2)}")
        frames_label = QLabel(f"frame: {int(self.total_frames)}")
        length_label = QLabel(f"length: {round(self.length, 2)}s")


        video_info_layout.addWidget(fps_label)
        video_info_layout.addWidget(frames_label)
        video_info_layout.addWidget(length_label)

        # ラジオボタン
        radio_layout = QVBoxLayout()
        custam_layout = QHBoxLayout()
        self.radio_seconds = QRadioButton("seconds")
        self.radio_seconds.clicked.connect(self.radio_clicked)
        self.radio_frames = QRadioButton("frames")
        self.radio_frames.clicked.connect(self.radio_clicked)
        self.radio_all = QRadioButton("All")
        self.radio_all.clicked.connect(self.radio_clicked)
        self.radio_custam = QRadioButton("Custam")
        self.radio_custam.clicked.connect(self.radio_clicked)
        self.radio_seconds.setChecked(True)

        self.input_start = QSpinBox()
        self.input_start.valueChanged.connect(self.set_min_value)
        self.input_end = QSpinBox()
        self.input_end.valueChanged.connect(self.set_max_value)

        self.input_start.setMinimum(1)
        self.input_start.setValue(1)
        self.input_end.setMaximum(int(self.total_frames))
        self.input_end.setValue(int(self.total_frames))
        self.input_start.setMaximum(self.input_end.value())
        self.input_end.setMinimum(self.input_start.value())

        self.input_start.setEnabled(False)
        self.input_end.setEnabled(False)

        radio_layout.addWidget(QLabel("\nPlease Select a Creation Method"))
        radio_layout.addWidget(self.radio_seconds)
        radio_layout.addWidget(self.radio_frames)
        radio_layout.addWidget(self.radio_all)
        custam_layout.addWidget(self.radio_custam)
        custam_layout.addStretch()
        custam_layout.addWidget(self.input_start)
        custam_layout.addSpacing(20)
        custam_layout.addWidget(QLabel("to"))
        custam_layout.addSpacing(20)
        custam_layout.addWidget(self.input_end)
        custam_layout.addStretch()
        radio_layout.addLayout(custam_layout)

        # 開始と終了
        range_layout = QHBoxLayout()
        self.start_label = QLabel("0")
        self.end_label = QLabel(f"{int(round(self.length, 0))}")
        self.slider = CustamRangeSlider(Qt.Orientation.Horizontal)
        self.slider.valueChanged.connect(self.set_value)
        self.slider.setRange(0, self.total_frames)
        self.slider.setValue((0, self.total_frames))
        self.slider.show()

        range_layout.addWidget(self.start_label)
        range_layout.addSpacing(20)
        range_layout.addWidget(self.slider)
        range_layout.addSpacing(20)
        range_layout.addWidget(self.end_label)

        # ダウンロードフォルダ、ファイル表示
        save_layout = QHBoxLayout()
        folder_layout = QHBoxLayout()

        self.download_folder = USER_DOWNLOAD_FOLDER
        self.dl_path = QLineEdit(self.download_folder)
        self.dl_path.setReadOnly(True)
        select_button = QPushButton("select")
        select_button.clicked.connect(self.select_folder)
        self.seq_name = QLineEdit("output")

        self.ext_box = QComboBox()
        self.ext_box.addItem("jpg")
        self.ext_box.addItem("png")
        self.ext_box.addItem("bmp")

        folder_layout.addWidget(QLabel("Path"))
        folder_layout.addSpacing(20)
        folder_layout.addWidget(self.dl_path)
        folder_layout.addSpacing(20)
        folder_layout.addWidget(select_button)

        save_layout.addWidget(QLabel("File Name"))
        save_layout.addSpacing(20)
        save_layout.addWidget(self.seq_name)
        save_layout.addSpacing(20)
        save_layout.addWidget(QLabel("_ {file number} ."))
        save_layout.addSpacing(20)
        save_layout.addWidget(self.ext_box)
        save_layout.addStretch()

        # 処理状況
        self.status_label = QLabel("Process Status")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.proc_status = QLabel("0 / 0")
        self.proc_status.setAlignment(Qt.AlignCenter)

        # 処理開始ボタン
        button_layout = QHBoxLayout()
        start_button = QPushButton("start")
        start_button.clicked.connect(self.make_seq_images)
        button_layout.addStretch()
        button_layout.addWidget(start_button)
        button_layout.addStretch()

        layout.addLayout(video_info_layout)
        layout.addLayout(radio_layout)
        layout.addStretch()
        layout.addLayout(range_layout)
        layout.addStretch()
        layout.addLayout(folder_layout)
        layout.addLayout(save_layout)
        layout.addWidget(self.status_label)
        layout.addWidget(self.proc_status)
        layout.addLayout(button_layout)

    def set_value(self, value):
        if self.radio_seconds.isChecked():
            self.start_label.setText(str(int(round((value[0]/ self.fps), 0))))
            self.end_label.setText(str(int(round((value[1]/ self.fps), 0))))
        elif self.radio_frames.isChecked():
            self.start_label.setText(str(int(value[0])))
            self.end_label.setText(str(int(value[1])))
        elif self.radio_frames.isChecked() or self.radio_custam.isChecked():
            pass

    def set_max_value(self):
        self.input_start.setMaximum(self.input_end.value())

    def set_min_value(self):
        self.input_end.setMinimum(self.input_start.value())

    def radio_clicked(self):
        if self.radio_seconds.isChecked():
            self.input_start.setEnabled(False)
            self.input_end.setEnabled(False)
            self.slider.setEnabled(True)
            self.end_label.setText(str(int(round(self.length, 0))))
        elif self.radio_frames.isChecked():
            self.input_start.setEnabled(False)
            self.input_end.setEnabled(False)
            self.slider.setEnabled(True)
            self.end_label.setText(str(int(self.total_frames)))
        elif self.radio_all.isChecked():
            self.input_start.setEnabled(False)
            self.input_end.setEnabled(False)
            self.slider.setEnabled(False)
        elif self.radio_custam.isChecked():
            self.input_start.setEnabled(True)
            self.input_end.setEnabled(True)
            self.slider.setEnabled(False)

    def select_folder(self):
        foldername = QFileDialog.getExistingDirectory(self, "select folder")
        if foldername:
            self.download_folder = foldername
            self.dl_path.setText(foldername)

    def make_seq_images(self):
        if self.radio_all.isChecked():
            start = 1
            end = self.total_frames
        elif self.radio_custam.isChecked():
            start = self.input_start.value()
            end = self.input_end.value()
        else:
            start = self.slider.value()[0]
            end = self.slider.value()[1]
        output_dir = self.download_folder
        output_file_name = self.seq_name.text()
        ext = self.ext_box.currentText()

        def show_progress(value):
            self.proc_status.setText(f"{int(value)} / {int(end - start + 1)}")

        def finished():
            QMessageBox.information(self, "Finish", "Finished Makeing Sequential Images")
            self.make_seq_thread.deleteLater()
            self.close()

        def error():
            print("An Error Has Occured")

        self.worker = MakeSeqWorker(self.video, start, end, output_dir, output_file_name, ext)
        self.make_seq_thread = QThread()
        self.worker.moveToThread(self.make_seq_thread)

        self.make_seq_thread.started.connect(self.worker.run)
        self.worker.progress.connect(show_progress)
        self.worker.error.connect(error)
        self.worker.finished.connect(self.make_seq_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.make_seq_thread.finished.connect(finished)

        self.make_seq_thread.start()

# movetoThread方式（推奨されているらしい？）
class MakeSeqWorker(QObject):
    progress = Signal(int)
    error = Signal()
    finished = Signal()

    def __init__(self, video, start, end, dir, filename, ext):
        super().__init__()
        self.video = video
        self.start = start - 1 # わかりやすいように1始まりにしてあったものを0始まりに直す
        self.end = end - 1
        self.filename = filename
        self.ext = ext
        print(self.video)

        os.makedirs(dir, exist_ok=True)
        self.base = os.path.join(dir, filename)

    @Slot()
    def run(self):
        print("process start")
        self.video.set(cv2.CAP_PROP_POS_FRAMES, self.start)
        if self.start == self.end:
            ret, frame = self.video.read()
            if ret:
                cv2.imwrite(f"{self.base}_0001.{self.ext}", frame)
            else:
                self.error.emit()
        elif self.start < self.end:
            for num in range(int(self.end - self.start) + 1):
                ret, frame = self.video.read()
                if ret:
                    cv2.imwrite(f"{self.base}_{num+1:04}.{self.ext}", frame)
                    self.progress.emit(num+1)
                else:
                    self.error.emit()

        self.video.release()
        self.finished.emit()


class MakeVideoWindow(QDialog):
    temp_video = Signal(str)
    saved_video = Signal(str)

    def __init__(self):
        super().__init__()
        self.resize(600, 400)
        self.setWindowTitle("Make Video From Sequential Images")
        self.folder_path = USER_DOWNLOAD_FOLDER

        layout = QVBoxLayout(self)

        # パス
        self.path_layout = QVBoxLayout()
        self.image_path_layout = QHBoxLayout()

        self.exp_label = QLabel("Supports only the format\n filename_0000.jpg, .png, .bmp")
        self.exp_label.setAlignment(Qt.AlignCenter)
        self.image_path = QLineEdit()
        self.image_path.setReadOnly(True)
        self.image_folder_button = QPushButton("select")
        self.image_folder_button.clicked.connect(self.select_image_folder)


        self.path_layout.addWidget(self.exp_label)
        self.path_layout.addSpacing(20)
        self.image_path_layout.addWidget(QLabel("Image Path"))
        self.image_path_layout.addSpacing(20)
        self.image_path_layout.addWidget(self.image_path)
        self.image_path_layout.addStretch()
        self.image_path_layout.addWidget(self.image_folder_button)
        self.path_layout.addLayout(self.image_path_layout)

        # 生成形式
        self.radio_layout = QVBoxLayout()

        self.radio_play_only = QRadioButton("Only Play")
        self.radio_save_only = QRadioButton("Only Save")
        self.radio_save_and_play = QRadioButton("Save and Play")
        self.radio_save_and_play.setChecked(True)

        self.radio_layout.addWidget(self.radio_play_only)
        self.radio_layout.addWidget(self.radio_save_only)
        self.radio_layout.addWidget(self.radio_save_and_play)

        # 入力
        self.input_layout = QVBoxLayout()
        self.folder_layout = QHBoxLayout()
        self.filename_layout = QHBoxLayout()

        self.input_folder_path = QLineEdit(self.folder_path)
        self.input_folder_path.setReadOnly(True)
        self.select_button = QPushButton("select")
        self.select_button.clicked.connect(self.select_save_folder)
        self.save_filename_input = QLineEdit()

        self.folder_layout.addWidget(QLabel("Save Path"))
        self.folder_layout.addSpacing(20)
        self.folder_layout.addWidget(self.input_folder_path)
        self.folder_layout.addStretch()
        self.folder_layout.addWidget(self.select_button)

        self.filename_layout.addWidget(QLabel("Save Filename"))
        self.filename_layout.addSpacing(20)
        self.filename_layout.addWidget(self.save_filename_input)
        self.filename_layout.addStretch()
    
        self.input_layout.addLayout(self.folder_layout)
        self.input_layout.addLayout(self.filename_layout)

        # fps
        self.fps_layout = QHBoxLayout()
        
        self.fps = QSpinBox()
        self.fps.setMinimum(1)
        self.fps.setValue(30)

        self.fps_layout.addWidget(QLabel("fps"))
        self.fps_layout.addStretch()
        self.fps_layout.addWidget(self.fps)
        self.fps_layout.addStretch()

        # 変換状況
        self.status_layout = QVBoxLayout()

        self.status_label = QLabel("Conversion Processing Status")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.process_label = QLabel("0 / 0")
        self.process_label.setAlignment(Qt.AlignCenter)
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.process_label)

        # スタートボタン
        self.start_button = QPushButton("start")
        self.start_button.clicked.connect(self.make_video)

        layout.addLayout(self.path_layout)
        layout.addStretch()
        layout.addLayout(self.radio_layout)
        layout.addStretch()
        layout.addLayout(self.input_layout)
        layout.addLayout(self.fps_layout)
        layout.addStretch()
        layout.addLayout(self.status_layout)
        layout.addWidget(self.start_button)

    def select_save_folder(self):
        foldername = QFileDialog.getExistingDirectory(self, "select folder")
        if foldername:
            self.folder_path = foldername
            self.input_folder_path.setText(foldername)

    def select_image_folder(self):
        foldername = QFileDialog.getExistingDirectory(self, "select folder")
        if foldername:
            self.image_path.setText(foldername)

    def make_video(self):
        def get_images():
            files = []
            extension = ("jpg", "png", "bmp")
            for ext in extension:
                files.append(glob.glob(f"{self.image_path.text()}/*_[0-9][0-9][0-9][0-9].{ext}"))
            return files

        def sort_file(file):
            sorted_file = sorted(file, key=lambda f: int(os.path.splitext(f)[0][-4:]))
            return sorted_file
        
        def get_size(file):
            img = cv2.imread(file[0])
            h, w, _ = img.shape
            return w, h
        
        def progress_status(value):
            self.process_label.setText(f"{value} / {len(file)}")
        
        def finished():
            QMessageBox.information(self, "Finish", "Finish Making Video")
            self.make_video_thread.deleteLater()
            if self.radio_save_and_play.isChecked():
                self.saved_video.emit(save_path)
            elif self.radio_play_only.isChecked():
                self.temp_video.emit(self.tmp.name)
            self.close()

        if self.image_path.text() == "":
            QMessageBox.warning(self, "Path error", "Please Input Image Path")
            return
        if self.radio_save_and_play.isChecked() and self.save_filename_input.text() == "":
            QMessageBox.warning(self, "Filename error", "Please Input Filename")
            return
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        files = get_images()
        """
        今はいったん１つの形式にのみ対応
        今後プレイリスト形式にしたときに複数形式や同一形式複数ファイルに対応予定
        """
        if not files[0] and not files[1] and not files[2]:
            print("No Images")
            return
        elif files[0]:
            file = files[0]
        elif files[1]:
            file = files[1]
        elif files[2]:
            file = files[2]

        file = sort_file(file)
        width, height = get_size(file)
        if self.radio_play_only.isChecked():
            self.tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
            self.tmp.close()
            save_path = self.tmp.name
        elif self.radio_save_only.isChecked() or self.radio_save_and_play.isChecked():
            save_path = os.path.join(self.folder_path, self.save_filename_input.text() + ".mp4")
            os.makedirs(self.folder_path, exist_ok=True)
        fps = self.fps.value()

        self.make_video_worker = MakeVideoWorker(file, save_path, fourcc, fps, width, height)
        self.make_video_thread = QThread()
        self.make_video_worker.moveToThread(self.make_video_thread)

        self.make_video_thread.started.connect(self.make_video_worker.run)
        self.make_video_worker.progress.connect(progress_status)
        self.make_video_worker.finished.connect(self.make_video_thread.quit)
        self.make_video_worker.finished.connect(self.make_video_worker.deleteLater)
        self.make_video_thread.finished.connect(finished)

        self.make_video_thread.start()


class MakeVideoWorker(QObject):
    finished = Signal()
    progress = Signal(int)

    def __init__(self, file, filename, fourcc, fps, width, height):
        super().__init__()
        self.file = file
        self.filename = filename
        self.fourcc = fourcc
        self.fps = fps
        self.size = (width, height)

    @Slot()
    def run(self):
        self.video = cv2.VideoWriter(self.filename, self.fourcc, self.fps, self.size)
        i = 1
        try:
            for f in self.file:
                img = cv2.imread(f)
                if img is None:
                    continue
                self.video.write(img)
                self.progress.emit(i)
                i += 1
        finally:
            self.video.release()
            self.finished.emit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())
