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
        self.y = 500
        size = str(self.x) + "x" + str(self.y)

        self.title("動画ダウンローダー")
        self.geometry(size)
        self.set_widget()

    def set_widget(self):
        # pack, grid, placeは同じコンテナで混在不可
        # メニューバー(ファイル)
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        
        file = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="file", menu=file)

        # 動画ファイルを開く
        file.add_command(label="open file", command=self.open_file)

        # canvas
        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="top")
        
        # frame
        self.frame = tk.Frame(self)
        self.frame.pack(side="top")
        
        # スライダー
        self.value = 0
        self.value_var = tk.StringVar(value="0")
        time_scale = tk.Scale(
            self.frame,
            length=self.x,
            orient=tk.HORIZONTAL,
            showvalue=False,
            command=self.get_scale_value
            )
        time_scale.pack(side="top")
        tk.Label(self.frame, textvariable=self.value_var).pack()
        
        # 一時停止ボタン
        pause_button = tk.Button(self.frame, text="pause", command=self.pause)
        pause_button.pack(side="top")
        

        # ループ再生オンオフ

        # 終了ボタン
        end_button = tk.Button(self, text="END", command=self.end)
        end_button.pack(side="right")
    
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
            
    # スライダーの値を取得
    def get_scale_value(self, value):
        self.value = value
        self.value_var.set(str(value))

    # 一時停止
    def pause(self):
        self.player.pause()

    # 終了
    def end(self):
        try:
            self.player.stop()
        finally:
            self.destroy()


if __name__ == "__main__":
    vlc_player = videoPlayer()
    vlc_player.mainloop()
