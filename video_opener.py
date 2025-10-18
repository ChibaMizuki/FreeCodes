# VLCを使って動画を開く
# tkinterのcanvasに描画する

# 実装したい機能
# menu
# シークバー
# 動画編集機能
# ループ再生
# 音量
# yt-dlp機能
# 別窓
# ダークモード
# 動画サイズ、画面サイズ変更
# 保存、出力機能
# 

import vlc
import tkinter as tk
from tkinter import filedialog
import cv2

class videoPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.x = 600
        self.y = 400
        size = str(self.x) + "x" + str(self.y)

        self.title("動画ダウンローダー")
        self.geometry(size)
        self.set_widget()

    def set_widget(self):
        # pack, grid, placeは同じコンテナで混在不可
        # 動画ファイルを開くボタン
        open_button = tk.Button(self, text="open", command=self.open_file)
        open_button.grid(row=0, column=0)

        # canvas
        self.canvas = tk.Canvas(self)
        self.canvas.grid(row=1, column=1)

        # 一時停止ボタン
        pause_button = tk.Button(self, text="pause", command=self.pause)
        pause_button.grid(row=2, column=1)

        # ループ再生オンオフ

        # 終了ボタン
        end_button = tk.Button(self, text="END", command=self.end)
        end_button.grid(row=2, column=2)
    
    # VLCメディアプレイヤーの設定
    def VLC(self, url):
        instance = vlc.Instance()
        self.player = instance.media_player_new()
        media = instance.media_new(url)
        self.player.set_media(media)
        self.player.set_hwnd(self.canvas.winfo_id())
        self.player.play()

    # ファイル選択をもとにVLC起動
    def open_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.VLC(file)

    # 一時停止
    def pause(self):
        self.player.pause()

    # 終了
    def end(self):
        self.player.stop()
        self.destroy()


if __name__ == "__main__":
    vlc_player = videoPlayer()
    vlc_player.mainloop()
