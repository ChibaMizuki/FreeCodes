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

        self.open_video = False
        self.is_dragging = False
        self.is_updating = False

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
        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="top", fill="both", expand=True)
        
        # frame
        self.frame = tk.Frame(self)
        self.frame.pack(side="top", fill="x")
        
        # スライダー
        self.time_scale = tk.Scale(
            self.frame,
            length=self.x,
            orient=tk.HORIZONTAL,
            showvalue=False,
            command=self.on_scale_move # 動いたときに実行する
            )
        self.time_scale.pack(side="top", fill="x", padx=10)
        self.time_label = tk.Label(self.frame, text="0 / 0")
        self.time_label.pack()
        
        # 一時停止ボタン
        self.pause_button = tk.Button(
            self.frame,
            text="play / pause", 
            command=self.pause, 
            state="disabled"
        )
        self.pause_button.pack(side="top")
        

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
        self.pause_button.config(state="normal")
        self.player.play()
        self.open_video = True
        self.after(500, self.init_duration) # ms後に関数を1度実行する
    
    # 動画の長さを取得してスライダー範囲設定
    def init_duration(self):
        if not self.open_video:
            return
        length = self.player.get_length()
        if length > 0:
            self.time_scale.config(to=length)
            self.total_length = length
            self.time_label.config(text=f"0 / {length // 1000}s")
            if not self.is_updating:
                self.is_updating = True 
                self.update_slider() # 再生中のみ更新
        else:
            self.after(500, self.init_duration)
        
    # 定期的なスライダー更新（VLCの再生位置を取得）
    def update_slider(self):
        if self.open_video and not self.is_dragging:
            current = self.player.get_time()
            self.time_scale.set(current)
            self.time_label.config(text=f"{current // 1000}s / {self.total_length // 1000}s")
        
        # 再生中のみ更新する
        if self.open_video and self.player.is_playing():
            self.after(2000, self.update_slider) # 再帰的に呼び出すことで永続的に実行する
        else:
            self.is_updating = False
        

    # スライダー操作時（ユーザーが移動中）
    def on_scale_move(self, val):
        if self.open_video:
            self.is_dragging = True
            self.player.set_time(int(float(val))) # なぜか知らないけどstrで戻ってくるらしい（ソースコードより）
            self.after(300, self.reset_drag_flag)
    
    def reset_drag_flag(self):
        self.is_dragging = False

    # ファイル選択をもとにVLC起動
    def open_file(self):
        file = filedialog.askopenfilename()
        if file:
            self.VLC(file)

    def start(self):
        self.player.play()

    # 一時停止
    def pause(self):
        self.player.pause()

    # 終了
    def end(self):
        # 第1引数に第2引数が存在するか判定
        if hasattr(self, 'player'):
            self.player.stop()
            print("stop")
        self.destroy()
        


if __name__ == "__main__":
    vlc_player = videoPlayer()
    vlc_player.mainloop()
