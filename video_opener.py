# VLCを使って動画を開く
# tkinterのcanvasに描画する

# 実装したい機能
# シークバー（済）
# 動画を閉じる（済）
# 動画編集機能
# ループ再生
# 音量
# yt-dlp機能
# 別窓
# ダークモード(済)
# 動画サイズ、画面サイズ変更
# 保存、出力機能
# 

import vlc
import tkinter as tk
from tkinter import filedialog
import cv2
import time

class videoPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.x = 600
        self.y = 500
        size = str(self.x) + "x" + str(self.y)
        self.config(background="#202020")

        self.title("動画ダウンローダー")
        self.geometry(size)

        self.open_video = False
        self.is_dragging = False
        self.slider_id = None

        self.set_widget()

    def set_widget(self):
        # pack, grid, placeは同じコンテナで混在不可
        # メニューバー(ファイル)
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        file = tk.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="file", menu=file)
        # 動画ファイルを開く項目
        file.add_command(label="open file", command=self.open_file)


        # canvas
        self.canvas = tk.Canvas(self, background="#202020")
        self.canvas.pack(side="top", fill="both", expand=True)
        
        # frame
        self.frame = tk.Frame(self, background="#202020")
        self.frame.pack(side="top", fill="x")
        
        # スライダー
        self.value_var = tk.StringVar(value="0")
        self.time_scale = tk.Scale(
            self.frame,
            length=self.x,
            orient=tk.HORIZONTAL,
            showvalue=False,
            command=self.on_scale_move, # 動かしたときに実行する
            background="#202020",
            foreground="#e0e0e0"
            )
        self.time_scale.pack(side="top", fill="x", padx=10)
        tk.Label(self.frame, textvariable=self.value_var, background="#202020", foreground="#e0e0e0").pack()
        
        # 一時停止ボタン
        self.pause_button = tk.Button(
            self.frame,
            text="play / pause", 
            command=self.pause, 
            state="disabled",
            background="#202020",
            foreground="#e0e0e0"
        )
        self.pause_button.pack(side="top")

        # 終了ボタン
        self.end_button = tk.Button(
            self,
            text="END",
            command=self.end,
            background="#202020",
            foreground="#e0e0e0"
            )
        self.end_button.pack(side="right")
        
        # 動画を閉じる
        self.release_button = tk.Button(
            self,
            text="CLOSE",
            command=self.release_video,
            background="#202020",
            foreground="#e0e0e0",
            state="disabled",
            )
        self.release_button.pack(side="right")
    
    # VLCメディアプレイヤーの設定
    def VLC(self, url):
        if self.open_video:
            self.release_video()
        instance = vlc.Instance("--no-video-title-show")
        self.player = instance.media_player_new()
        media = instance.media_new(url)
        self.player.set_media(media)
        self.player.set_hwnd(self.canvas.winfo_id())
        self.player.play()
        self.open_video = True
        self.pause_button.config(state="normal")
        self.release_button.config(state="normal")
        self.after(500, self.set_scale_range) # ms後に関数を1度実行する
    
    # 動画の長さを取得してスライダー範囲設定
    def set_scale_range(self):
        if not self.open_video:
            return
        length = self.player.get_length()
        if length > 0:
            self.time_scale.config(to=length)
            self.total_length = length
            self.value_var.set(f"0 / {length // 1000}s")
            self.after(1000, self.update_slider)
        else:
            self.after(500, self.set_scale_range)

    # スライダー操作時再生位置を変更
    def on_scale_move(self, val):
        if self.open_video:
            self.is_dragging = True
            pos = int(float(val)) # なぜかstrで戻ってくるらしい（ソースコードより）
            self.player.set_time(pos)
            self.value_var.set(f"{pos // 1000} / {self.total_length // 1000}s")
            self.after(200, lambda: setattr(self, "is_dragging", False))

    # スライダーを見かけ上動かす
    def update_slider(self):
        if self.open_video and not self.is_dragging:
            state = self.player.get_state()
            if state == vlc.State.Playing:
                val = self.time_scale.get() + 1000
                if val <= self.total_length:
                    self.time_scale.set(val)
                    self.value_var.set(f"{val // 1000} / {self.total_length // 1000}s")
            elif state == vlc.State.Ended:
                self.time_scale.set(self.total_length)
                self.value_var.set(f"{self.total_length // 1000} / {self.total_length // 1000}s")

        if self.open_video:
            self.slider_id = self.after(1000, self.update_slider)

    # ファイル選択をもとにVLC起動
    def open_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.VLC(file)

    # 一時停止
    def pause(self):
        if not self.open_video:
            return
        
        state = self.player.get_state()
        if state == vlc.State.Playing:
            self.player.pause()
        elif state == vlc.State.Paused:
            self.player.play()
        elif state in (vlc.State.Stopped, vlc.State.Ended, vlc.State.NothingSpecial):
            self.player.stop()
            self.player.set_time(0)
            self.time_scale.set(0)
            self.player.play()

    def release_video(self):
        if self.open_video:
            self.open_video = False
            if self.slider_id:
                self.after_cancel(self.slider_id)
                self.slider_id = None
            self.player.stop()
            self.player.release()
            self.player = None
            self.canvas.delete("all")
            self.time_scale.set(0)
            self.value_var.set(value="0")

    # 終了
    def end(self):
        # 第1引数に第2引数が存在するか判定
        if hasattr(self, 'player') and self.player != None:
            self.player.stop()
        self.destroy()
        

if __name__ == "__main__":
    vlc_player = videoPlayer()
    vlc_player.mainloop()
