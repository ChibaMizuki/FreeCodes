# media_player.pyをpyside6に移植

import vlc
import yt_dlp
import os
import sys
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
)
from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
    Slot,
    QThread,
)


class videoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 VLC Player")
        self.setGeometry(200, 200, 1000, 700)
        self.dl_window = downloadWindow(self)
        self.dl_window.hide()

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
        download.triggered.connect(self.show_dl_window)
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
    
    def show_dl_window(self):
        self.dl_window.show()

    def closeEvent(self, event):
        self.dl_window.close()


class downloadWindow(QDialog):
    success = Signal()
    error = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(600, 600, 600, 400)
        self.setWindowTitle("Download")

        layout = QVBoxLayout(self)

        # URL入力欄
        input_video_url = QHBoxLayout()

        url_label = QLabel("URL: ")
        input_video_url.addWidget(url_label)

        self.video_url = QLineEdit()
        input_video_url.addSpacing(10)
        input_video_url.addWidget(self.video_url)
        input_video_url.addSpacing(10)

        clear_button = QPushButton("clear")
        clear_button.setMaximumWidth(80)
        clear_button.clicked.connect(self.clear_url)

        # 保存先設定
        input_save_path = QHBoxLayout()

        path_label = QLabel("PATH")
        input_save_path.addWidget(path_label)

        # 内部でパス保持する方の変数
        self.folder_path = self.get_user_download_folder()
        # パスを表示する方の変数
        self.dl_path = QLineEdit(self.folder_path)
        self.dl_path.setReadOnly(True)
        input_save_path.addSpacing(10)
        input_save_path.addWidget(self.dl_path)
        input_save_path.addSpacing(10)

        select_button = QPushButton("select")
        select_button.clicked.connect(self.select_folder)
        input_save_path.addWidget(select_button)
        input_save_path.addSpacing(10)

        # ダウンロードボタン
        dl_button = QPushButton("download")
        dl_button.clicked.connect(self.download)

        # 確認チェックボックス

        # 進捗表示
        self.progress = QLabel("waiting")
        self.progress.setAlignment(Qt.AlignCenter)

        # レイアウト合体
        layout.addSpacing(20)
        layout.addLayout(input_video_url)
        layout.addSpacing(20)
        layout.addWidget(clear_button)
        layout.addSpacing(20)
        layout.addLayout(input_save_path)
        layout.addStretch()
        layout.addWidget(self.progress)
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
        self.download_process.start()

    def show_messege(self, mes=None):
        if mes != None:
            QMessageBox.warning(self, "error", f"Failed to Download\n{mes}")
        else:
            QMessageBox.information(self, "success", "Finish Download")

class downloadThread(QThread):
    error = Signal(str)
    success = Signal()

    def __init__(self, dl_window ,url, folder):
        super().__init__()
        self.dl_window = dl_window
        self.url = url
        self.folder = folder
    
    def run(self):
        ydl_opts = {
            "format": "bv*+ba/b", # bestvideoとbestaudio or best video&audioをダウンロード
            "remote_components": ["ejs:github"], # Denoインストール必須
            'outtmpl': os.path.join(self.folder, '%(title)s.%(ext)s'),
            # 'progress_hooks': [progress_hook],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.success.emit()
        except Exception as e:
           self.error.emit(e)
            # QThread内でメッセージボックスなどUIをいじるとエラーが生じる
            # expected string or bytes-like object, got 'PySide6.QtWidgets.QLineEdit'


if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = videoPlayer()
    player.show()
    sys.exit(app.exec())
