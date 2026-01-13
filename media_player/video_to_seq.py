import os
import cv2
from PySide6.QtCore import Qt ,QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QSpinBox,
    QLineEdit, QFileDialog, QMessageBox,
    QComboBox
)

from constants import USER_DOWNLOAD_FOLDER
from custom_widgets import CustomRangeSlider


class MakeSeqWindow(QDialog):
    def __init__(self, video_path):
        super().__init__()
        if not video_path:
            return

        self.resize(600, 400)
        self.setWindowTitle("Make Sequential Images From Video")

        self.video_path = video_path
        self.video = cv2.VideoCapture(self.video_path)
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.total_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.video.release()
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
        self.radio_seconds = QRadioButton("秒数指定")
        self.radio_seconds.clicked.connect(self.radio_clicked)
        self.radio_frames = QRadioButton("フレーム指定")
        self.radio_frames.clicked.connect(self.radio_clicked)
        self.radio_all = QRadioButton("全体")
        self.radio_all.clicked.connect(self.radio_clicked)
        self.radio_custam = QRadioButton("入力指定")
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

        radio_layout.addWidget(QLabel("\n出力方法を指定"))
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
        self.slider = CustomRangeSlider(Qt.Orientation.Horizontal)
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
        select_button = QPushButton("選択")
        select_button.clicked.connect(self.select_folder)
        self.seq_name = QLineEdit("output")

        self.ext_box = QComboBox()
        self.ext_box.addItem("jpg")
        self.ext_box.addItem("png")
        self.ext_box.addItem("bmp")

        folder_layout.addWidget(QLabel("保存先"))
        folder_layout.addSpacing(20)
        folder_layout.addWidget(self.dl_path)
        folder_layout.addSpacing(20)
        folder_layout.addWidget(select_button)

        save_layout.addWidget(QLabel("ファイル名"))
        save_layout.addSpacing(20)
        save_layout.addWidget(self.seq_name)
        save_layout.addSpacing(20)
        save_layout.addWidget(QLabel("_ {file number} ."))
        save_layout.addSpacing(20)
        save_layout.addWidget(self.ext_box)
        save_layout.addStretch()

        # 処理状況
        self.status_label = QLabel("進捗状況")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.proc_status = QLabel("0 / 0")
        self.proc_status.setAlignment(Qt.AlignCenter)

        # 処理開始ボタン
        button_layout = QHBoxLayout()
        start_button = QPushButton("開始")
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
            QMessageBox.information(self, "Finish", "出力終了")
            self.make_seq_thread.deleteLater()
            self.close()

        def error():
            print("An Error Has Occured")

        self.worker = MakeSeqWorker(self.video_path, start, end, output_dir, output_file_name, ext)
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

    def __init__(self, video_path, start, end, dir, filename, ext):
        super().__init__()
        self.video = cv2.VideoCapture(video_path)
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
