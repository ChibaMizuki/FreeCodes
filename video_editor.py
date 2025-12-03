# 動画編集

# 実装項目
# タイムライン
# 出力
# 編集画面
# 編集機能
# 動画複数連続再生

import tkinter as tk
from tkinter import filedialog
import vlc
import threading
import time


class Editor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.x = 1000
        y = 800
        self.geometry(f"{self.x}x{y}")
        self.title("動画編集")

        self.player = None
        self.media = None
        self.duration = 0   # 秒
        
        self.timeline_scale = 20  # 1秒あたり20px
        self.timeline_cursor = None  # 現在位置の赤線

        self.set_widget()

    # ---------------------------
    # UI 作成
    # ---------------------------
    def set_widget(self):
        # メニューバー
        # 1. バーの作成
        menu = tk.Menu(self)
        
        # 2. バーに追加する枠の作成
        file_menu = tk.Menu(menu, tearoff=0)
        # 3. 枠の中身を作成
        file_menu.add_command(label="open", command=self.open_file_dialog)
        # 4. 枠をバーに追加
        menu.add_cascade(label="file", menu=file_menu)
        
        edit_menu = tk.Menu(menu, tearoff=0)
        edit_menu.add_command(label="open editor")
        menu.add_cascade(label="edit", menu=edit_menu)
        
        self.config(menu=menu)

        # 動画キャンバス
        self.canvas = tk.Canvas(self, bg="black", width=800, height=450)
        self.canvas.pack(expand=True, fill=tk.BOTH)

        # 再生ボタン
        self.play_button = tk.Button(self, text="play", command=self.start_stop)
        self.play_button.pack()

        # 秒単位スライダー
        self.slider = tk.Scale(
            self,
            from_=0,
            to=1,
            resolution=0.01,  # 0.01 秒単位
            orient=tk.HORIZONTAL,
            length=800,
            command=self.on_slider_change,
            showvalue=True
        )
        self.slider.pack(fill="x", expand=True)
    
        # ---------------------------
        # タイムライン Canvas
        # ---------------------------
        frame = tk.Frame(self)
        frame.pack(fill="x")
        
        self.timeline_canvas = tk.Canvas(frame, bg="#222", height=80, scrollregion=(0, 0, 2000, 80))
        # 横スクロールバー
        scrollbar = tk.Scrollbar(frame, orient="horizontal", command=self.timeline_canvas.xview)
        scrollbar.pack(fill="x")
        self.timeline_canvas.pack(fill="x", expand=True)
        
        self.timeline_canvas.configure(xscrollcommand=scrollbar.set)

    # ---------------------------
    # 動画ファイル選択
    # ---------------------------
    def open_file_dialog(self):
        path = filedialog.askopenfilename(
            filetypes=[("動画ファイル", "*.mp4 *.mov *.avi *.mkv")]
        )
        if path:
            self.open_video(path)

    # ---------------------------
    # 動画読み込み
    # ---------------------------
    def open_video(self, url):
        if self.player:
            self.player.stop()

        instance = vlc.Instance()
        self.player = instance.media_player_new()

        self.media = instance.media_new(url)
        self.player.set_media(self.media)

        # Canvas に表示
        hwnd = self.canvas.winfo_id()
        self.player.set_hwnd(hwnd)

        # 再生して duration を取得
        self.player.play()
        self.after(50, lambda: self.player.pause())

        def load_duration():
            time.sleep(0.3)
            dur = self.player.get_length() / 1000
            while dur <= 0:
                time.sleep(0.1)
                dur = self.player.get_length() / 1000

            self.duration = dur
            # スライダーを動画時間に合わせる
            self.slider.config(from_=0, to=dur)
            
            self.create_timeline()

        threading.Thread(target=load_duration, daemon=True).start()

        # Ended 状態監視
        self.check_end()
        
    def create_timeline(self):
        self.timeline_canvas.delete("all")
        
        width = int(self.duration * self.timeline_scale)
        if width < self.x:
            width = self.x
            
        self.timeline_canvas.config(scrollregion=(0, 0, width, 80))
        
        self.timeline_canvas.create_rectangle(0, 20, width, 60, fill="#333", outline="")
        
        for sec in range(int(self.duration) + 1):
            x = sec * self.timeline_scale
            self.timeline_canvas.create_line(x, 20, x, 10, fill="white")
            self.timeline_canvas.create_text(x + 2, 5, text=str(sec), anchor="w", fill="white")
            
        self.timeline_cursor = self.timeline_canvas.create_line(0, 0, 0, 80, fill="red", width=2)
        

    # ---------------------------
    # Ended 状態監視
    # ---------------------------
    def check_end(self):
        if self.player:
            if self.player.get_state() == vlc.State.Ended:
                # Media 再設定で確実に復帰
                self.player.stop()
                self.player.set_media(self.media)
                self.player.play()
                self.after(50, self.player.set_time(int(self.duration - 1)))
                self.after(50, lambda: self.player.pause())
                

        self.after(200, self.check_end)

    # ---------------------------
    # スライダー操作 → 動画移動
    # ---------------------------
    def on_slider_change(self, value):
        if not self.player or self.duration == 0:
            return

        sec = float(value)
        # duration ぴったりだと VLC が Ended に入るので安全マージンを取る
        if sec >= self.duration - 0.02:
            sec = self.duration - 0.02

        self.player.set_time(int(sec * 1000))
        
        if self.timeline_cursor:
            x = sec * self.timeline_scale
            self.timeline_canvas.coords(self.timeline_cursor, x, 0, x, 80)

    # ---------------------------
    # 再生・停止ボタン
    # ---------------------------
    def start_stop(self):
        if not self.player:
            return

        state = self.player.get_state()

        # Ended → 再生できないので再セット
        if state == vlc.State.Ended:
            self.player.stop()
            self.player.set_media(self.media)
            self.player.play()
            self.player.set_time(0)
            self.slider.set(0)
            return

        if state == vlc.State.Playing:
            self.player.pause()
            ms = self.player.get_time()
            sec = ms / 1000
            self.slider.set(sec)

        elif state in (vlc.State.Paused, vlc.State.Stopped, vlc.State.NothingSpecial):
            self.player.play()


if __name__ == "__main__":
    app = Editor()
    app.mainloop()
