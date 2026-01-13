import os
import glob
import tempfile
import cv2
from PySide6.QtCore import Qt, QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QRadioButton,
    QSpinBox,
    QFileDialog,
    QMessageBox,
)

from constants import USER_DOWNLOAD_FOLDER


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

        self.exp_label = QLabel("対応形式\n filename_0000.jpg, .png, .bmp")
        self.exp_label.setAlignment(Qt.AlignCenter)
        self.image_path = QLineEdit()
        self.image_path.setReadOnly(True)
        self.image_folder_button = QPushButton("選択")
        self.image_folder_button.clicked.connect(self.select_image_folder)


        self.path_layout.addWidget(self.exp_label)
        self.path_layout.addSpacing(20)
        self.image_path_layout.addWidget(QLabel("画像フォルダ"))
        self.image_path_layout.addSpacing(20)
        self.image_path_layout.addWidget(self.image_path)
        self.image_path_layout.addStretch()
        self.image_path_layout.addWidget(self.image_folder_button)
        self.path_layout.addLayout(self.image_path_layout)

        # 生成形式
        self.radio_layout = QVBoxLayout()

        self.radio_play_only = QRadioButton("再生のみ")
        self.radio_save_only = QRadioButton("保存のみ")
        self.radio_save_and_play = QRadioButton("保存＆再生")
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
        self.select_button = QPushButton("選択")
        self.select_button.clicked.connect(self.select_save_folder)
        self.save_filename_input = QLineEdit()

        self.folder_layout.addWidget(QLabel("保存先"))
        self.folder_layout.addSpacing(20)
        self.folder_layout.addWidget(self.input_folder_path)
        self.folder_layout.addStretch()
        self.folder_layout.addWidget(self.select_button)

        self.filename_layout.addWidget(QLabel("保存ファイル名"))
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

        self.status_label = QLabel("変換状況")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.process_label = QLabel("0 / 0")
        self.process_label.setAlignment(Qt.AlignCenter)
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.process_label)

        # スタートボタン
        self.start_button = QPushButton("開始")
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
            QMessageBox.information(self, "Finish", "完了")
            self.make_video_thread.deleteLater()
            if self.radio_save_and_play.isChecked():
                self.saved_video.emit(save_path)
            elif self.radio_play_only.isChecked():
                self.temp_video.emit(self.tmp.name)
            self.close()

        if self.image_path.text() == "":
            QMessageBox.warning(self, "Path error", "画像が入っているフォルダを選択してください")
            return
        if self.radio_save_and_play.isChecked() and self.save_filename_input.text() == "":
            QMessageBox.warning(self, "Filename error", "保存先ファイル名を入力してください")
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
