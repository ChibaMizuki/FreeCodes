import os
import csv
import random
import vlc
from vlc import EventType
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSizePolicy,
    QStyle,
    QFileDialog,
    QMenuBar,
)

from custom_widgets import NoWheelSlider
from download import DownloadWindow
from video_to_seq import MakeSeqWindow
from seq_to_video import MakeVideoWindow
from playlist import MakePlaylist


class VideoPlayer(QMainWindow):
    media_ended = Signal()
    shuffle = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 VLC Player")
        self.resize(1000, 700)
        self.media = None
        self.hwnd = None
        self.send_filename = None
        self.tmp = None
        self.loop = True
        self.is_playlist = False
        self.playlist = []
        self.original_playlist = []
        self.current_index = 0

        self.media_ended.connect(self.end_check)
        self.shuffle.connect(self.set_shuffled_playlist)

        self.dl_window = DownloadWindow()
        self.dl_window.hide()
        self.dl_window.video.connect(self.open_file)
        self.make_seq = MakeSeqWindow()
        self.make_seq.hide()
        self.make_video = MakeVideoWindow()
        self.make_video.hide()
        self.make_video.temp_video.connect(self.temp_video_process)
        self.make_video.saved_video.connect(self.open_file)
        self.make_playlist = MakePlaylist()
        self.make_playlist.hide()
        self.make_playlist.new_playlist.connect(self.play_playlist)

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

        file = menu_bar.addMenu("ファイル")
        file_open = file.addAction("開く")
        file_open.triggered.connect(self.open_file)
        seq = file.addMenu("連番画像")
        self.video_to_seq = seq.addAction("エクスポート")
        self.video_to_seq.setDisabled(True)
        self.video_to_seq.triggered.connect(self.open_make_seq_window)
        seq_to_video = seq.addAction("インポート")
        seq_to_video.triggered.connect(lambda: self.make_video.show())
        playlist = file.addMenu("プレイリスト")
        make = playlist.addAction("編集")
        make.triggered.connect(self.edit_playlist)
        play = playlist.addAction("再生")
        play.triggered.connect(self.open_playlist)

        dl = menu_bar.addMenu("yt_dlp")
        download = dl.addAction("ダウンロード")
        download.triggered.connect(lambda: self.dl_window.show())
        self.setMenuBar(menu_bar)

        settings = menu_bar.addMenu("設定")
        self.play_shuffle = settings.addAction("シャッフル再生")
        self.play_shuffle.toggled.connect(self.toggle_shuffle)
        self.play_shuffle.setCheckable(True)
        self.play_shuffle.setChecked(False)
        
        # 再生ボタン
        self.play_button = QPushButton(self.style().standardIcon(QStyle.SP_MediaPlay), "")
        self.play_button.clicked.connect(self.toggle_play)
        self.next_button = QPushButton(self.style().standardIcon(QStyle.SP_MediaSkipForward), "")
        self.next_button.clicked.connect(self.next)
        self.previous_button = QPushButton(self.style().standardIcon(QStyle.SP_MediaSkipBackward), "")
        self.previous_button.clicked.connect(self.previous)

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
        self.volume.valueChanged.connect(self.set_volume)

        # レイアウト合体
        # 動画描画画面とその下で垂直分割
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.video_frame)
        
        # ボタン類を水平分割
        control_layout = QHBoxLayout()
        control_layout.addWidget(self.previous_button)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.next_button)
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

        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(EventType.MediaPlayerEndReached, self.media_end_event)
        
    # 動画表示
    def open_file(self, fn=None, *args, **kwargs):
        print(f"filename at open_file: {fn}")
        if not fn:
            filename, _ = QFileDialog.getOpenFileName(self, "Choose Video")
        else:
            filename = str(os.path.abspath(fn))
            print(f"filename (abspath): {filename}")

        if filename:
            self.set_video(filename)
            self.send_filename = filename
            self.is_playlist = False

    def set_video(self, filename):
        if not self.hwnd:
            self.hwnd = int(self.video_frame.winId())
            self.player.set_hwnd(self.hwnd)
        self.media = self.instance.media_new(filename)
        self.player.set_media(self.media)
        self.mute = False
        self.player.audio_set_mute(False)
        self.player.audio_set_volume(50)
        self.player.play()
        self.timer.start()
        self.mute_button.setIcon(self.style().standardIcon(QStyle.SP_MediaVolume))
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.volume.setValue(50)
        self.slider.setValue(0)
        self.video_to_seq.setEnabled(True)

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

    def set_volume(self, value):
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
    
    def toggle_shuffle(self, checked):
        if not self.playlist or not self.is_playlist:
            return
        
        self.shuffle.emit(checked)

    def set_shuffled_playlist(self, checked):
        print(f"shuffle: {checked}")
        if checked:
            self.current_index = 0
            self.is_playlist = True
            self.playlist = random.sample(self.original_playlist, len(self.original_playlist))
            self.send_filename = self.playlist[0]
            self.set_video(self.playlist[0])
        else:
            self.current_index = 0
            self.is_playlist = True
            self.playlist = self.original_playlist
            self.send_filename = self.playlist[0]
            self.set_video(self.playlist[0])

    # イベントハンドラ内でvlc関連の処理をするとlibvlcエラーが起きてフリーズする
    def media_end_event(self, event):
        self.media_ended.emit()

    def end_check(self):
        if self.is_playlist:
            self.next()
        else:
            self.player.set_media(self.media)
            self.player.set_position(0)
            self.player.play()
            self.slider.setValue(0)
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def open_make_seq_window(self):
        self.make_seq.get_video_path(self.send_filename)
        self.make_seq.show()

    def temp_video_process(self, path):
        self.clean_temp_file()
        self.tmp = path
        self.open_file(fn=self.tmp)

    def edit_playlist(self):
        if self.player.is_playing():
            self.player.pause()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.make_playlist.get_playlist(self.playlist)
        self.make_playlist.show()

    def play_playlist(self, playlist):
        self.playlist = playlist
        self.original_playlist = playlist
        self.current_index = 0
        self.send_filename = self.playlist[0]
        self.set_video(self.playlist[0])
        self.play_shuffle.setChecked(False)
        self.is_playlist = True

    def open_playlist(self):
        playlist, _ = QFileDialog.getOpenFileName(self, "Choose Playlist", filter="csv (*.csv)")
        if playlist:
            self.playlist = []
            with open(playlist, encoding="UTF-8", newline="") as f:
                reader = csv.reader(f)
                for video in reader:
                    if video and os.path.exists(video[0]):
                        self.playlist.append(video[0])
            
            self.play_playlist(self.playlist)
    
    def next(self):
        if not self.is_playlist:
            return
        self.current_index += 1
        if self.current_index >= len(self.playlist):
            self.current_index = 0
        self.send_filename = self.playlist[self.current_index]
        self.set_video(self.playlist[self.current_index])

    def previous(self):
        if not self.is_playlist:
            return
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = len(self.playlist) - 1
        self.send_filename = self.playlist[self.current_index]
        self.set_video(self.playlist[self.current_index])

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
        self.make_playlist.close()
