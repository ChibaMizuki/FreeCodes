# VLCを使って動画を開く
# tkinterのcanvasに描画する

# 実装したい機能
# シークバー（済）
# 動画を閉じる（済）
# 動画編集機能
# ループ再生
# 音量（済）
# yt-dlp機能（済）
# 別窓（済）
# ダークモード(済)
# 動画サイズ、画面サイズ変更（済）
# 保存、出力機能
# 

import vlc
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import os
import threading


class videoPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.x = 800
        self.y = 600
        size = str(self.x) + "x" + str(self.y)
        self.config(background="#202020")

        self.title("メディアプレイヤー")
        self.geometry(size)

        self.open_video = False
        self.is_dragging = False
        self.slider_id = None
        self.share_path = None
        self.move_slider = tk.BooleanVar(value=False)
        self.set_mute = tk.BooleanVar(value=False)

        self.set_widget()

    def set_widget(self):
        # pack, grid, placeは同じコンテナで混在不可
        # メニューバー(ファイル)
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)
        
        file = tk.Menu(menu_bar, tearoff=False)
        window = tk.Menu(menu_bar, tearoff=False)
        size = tk.Menu(window, tearoff=False)
        download = tk.Menu(menu_bar, tearoff=False)
        
        # 動画ファイルを開く項目
        menu_bar.add_cascade(label="file", menu=file) # メニューバーに追加
        file.add_command(label="open file", command=self.open_file) # 選択肢の追加
        # ウィンドウサイズ
        menu_bar.add_cascade(label="window", menu=window) # メニューバーに追加
        window.add_cascade(label="resize", menu=size) # 選択肢付き選択肢を追加
        size.add_cascade(label="set", command=self.set_window_size)
        size.add_cascade(label="1280x720", command=lambda: self.geometry("1280x720"))
        size.add_cascade(label="1440x900", command=lambda: self.geometry("1440x900"))
        # ダウンロード
        menu_bar.add_cascade(label="download", menu=download)
        download.add_command(label="download", command=lambda: DL(self))


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
        self.sld_confirm = tk.Checkbutton(
            self.frame, 
            variable=self.move_slider,
            background="#202020",
            )
        self.sld_confirm.pack(side="left")
        tk.Label(self.frame, text="move slider in real time", background="#202020", foreground="#e0e0e0").pack(side="left")
        
        # 音量
        self.audio_scale = tk.Scale(
            self.frame,
            length=100,
            to=100,
            orient=tk.HORIZONTAL,
            command=self.audio,
            background="#202020",
            foreground="#e0e0e0"
        )
        self.audio_scale.set(50)
        self.audio_scale.pack(side="left")
        
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
        
        # ミュートボタン
        self.mute = tk.Checkbutton(self.frame, variable=self.set_mute, command=self.mute_video, background="#202020")
        self.mute.pack(side="left")
        tk.Label(self.frame ,text="mute", background="#202020", foreground="#e0e0e0").pack(side="left")

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
        self.after(500, lambda: self.player.audio_set_volume(int(self.audio_scale.get())))
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
        move = self.move_slider.get()
        if self.open_video and not self.is_dragging and move:
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

    # ダウンロード後に動画を開く
    def recieve_path(self):
        if self.share_path != None:
            self.after(1500, lambda: self.VLC(str(self.share_path)))

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

    # 動画を閉じる
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
    
    # 音量
    def audio(self, value):
        if self.open_video:
            self.player.audio_set_volume(int(float(value)))
    
    # ミュート
    def mute_video(self):
        if hasattr(self, "player"):
            state = self.set_mute.get()
            self.player.audio_set_mute(state)
        
    # リサイズ
    def set_window_size(self):
        winsize_input_window = tk.Toplevel()
        winsize_input_window.geometry("300x300")
        label = tk.Label(winsize_input_window, text="resize")
        label.pack()
        
        x_label = tk.Label(winsize_input_window, text="x: ")
        x_label.pack()
        entry_x = tk.Entry(winsize_input_window)
        entry_x.pack()
        y_label = tk.Label(winsize_input_window, text="y: ")
        y_label.pack()
        entry_y = tk.Entry(winsize_input_window)
        entry_y.pack()
        
        def apply_user_settings():
            x = entry_x.get()
            y = entry_y.get()
            try:
                self.geometry(f"{int(x)}x{int(y)}")
                self.winsize_input_window.destroy()
            except ValueError as e:
                messagebox.showerror("eroor", "please input integer value")
            
        apply_button = tk.Button(winsize_input_window, command=apply_user_settings, text="apply")
        apply_button.pack()

    # 終了
    def end(self):
        # 第1引数に第2引数が存在するか判定
        if hasattr(self, 'player') and self.player != None:
            self.player.stop()
        self.destroy()


class DL(tk.Toplevel):
    def __init__(self, master=None): # masterは親ウィジェット
        super().__init__(master) # masterに何かを渡さないとエラーを吐く
        x = 600
        y = 400
        size = str(x) + "x" + str(y)

        self.title("動画ダウンローダー")
        self.geometry(size)

        # 初期値設定
        self.save_path = tk.StringVar(value=self.get_user_download_folder())
        self.progress = tk.StringVar(value="待機中...")
        self.title_confirm = tk.BooleanVar(value=True)
        self.open_confirm = tk.BooleanVar(value=False)

        # 各UI部品を構築
        self.create_widgets()

    # UI
    def create_widgets(self):
        # URL入力欄
        tk.Label(self, text="動画URL:").pack(anchor="w", padx=10, pady=5)
        self.url_entry = tk.Entry(self, width=60)
        self.url_entry.pack(padx=10, pady=5)
        tk.Button(self, text="URLクリア", command=self.clear_entry).pack(anchor="w", padx=10, pady=5)

        # 保存先設定
        path_frame = tk.Frame(self)
        path_frame.pack(anchor="w", padx=10, pady=5)
        tk.Label(path_frame, text="保存先: ").pack(side="left")
        tk.Entry(path_frame, textvariable=self.save_path, width=45).pack(side="left", padx=5)
        tk.Button(path_frame, text="選択", command=self.select_folder).pack(side="left")

        # ダウンロードボタン
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        self.download_button = tk.Button(button_frame, text="ダウンロード", command=self.download_video)
        self.download_button.pack(side="left", padx=5)

        # 確認チェックボックス
        confirm_frame = tk.Frame(self)
        confirm_frame.pack(pady=10)
        tk.Checkbutton(
            confirm_frame,
            text="ダウンロード前に確認ダイアログを表示する",
            variable=self.title_confirm
        ).grid(row=0, column=0, sticky="w")
        tk.Checkbutton(
            confirm_frame,
            text="ダウンロード後に動画ファイルを開く",
            variable=self.open_confirm
        ).grid(row=1, column=0, sticky="w")
        

        # 進捗表示
        progress_frame = tk.Frame(self)
        progress_frame.pack(pady=10)
        tk.Label(progress_frame, textvariable=self.progress, fg="blue").pack(pady=5)

        # 終了ボタン
        finish_frame = tk.Frame(self)
        finish_frame.pack(pady=10)
        tk.Button(finish_frame, text="終了", command=self.close).pack(padx=5)

    def clear_entry(self):
        self.url_entry.delete(0, tk.END)

    def close(self):
        self.destroy()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_path.set(folder)

    @staticmethod
    def get_user_download_folder():
        user_folder = os.path.expanduser("~")
        return os.path.join(user_folder, "Downloads")

    def download_video(self):
        url = self.url_entry.get()
        folder = self.save_path.get()

        if not url:
            messagebox.showerror("エラー", "URLを入力してください")
            return
        if not folder:
            messagebox.showerror("エラー", "保存先フォルダを選択してください")
            return

        if self.title_confirm.get():
            try:
                ydl_opts = {'quiet': True, 'no_warning': True, 'skip_download': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get("title", "不明なタイトル")
            except Exception as e:
                messagebox.showerror("エラー", f"動画情報の取得に失敗しました\n{e}")
                return
            
            confirm = messagebox.askyesno("確認", f"『{title}』をダウンロードしますか？")
            if not confirm:
                self.progress.set("キャンセルされました")
                return

        os.makedirs(folder, exist_ok=True)

        self.download_button.config(state="disabled")
        self.progress.set("ダウンロード開始...")

        thread = threading.Thread(target=self.run_download, args=(url, folder), daemon=True)
        thread.start()

    def run_download(self, url, folder):
        dl_path = None

        def progress_hook(d):
            nonlocal dl_path # nonlocal宣言することで上位階層の変数の変更ができる
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '').strip()
                eta = d.get('_eta_str', '').strip()
                speed = d.get('_speed_str', '').strip()
                self.progress.set(f"進行中: {percent} | 残り: {eta} | 速度: {speed}")
            elif d['status'] == 'finished':
                self.progress.set("変換中...")
                dl_path = d.get('filename', None) # ファイル名の取得
        
        def send_path(dl_path):
            if dl_path and os.path.exists(dl_path):
                self.master.share_path = dl_path
                self.master.recieve_path()
                self.destroy()
            else:
                messagebox.showerror("error", "could not get file path")
            

        ydl_opts = {
            'format': 'mp4',
            'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'quiet': True,
            'no_warning': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, lambda: self.progress.set("ダウンロード完了")) # UI変更はメインウィンドウで実行
            self.after(0, lambda: messagebox.showinfo("完了", "ダウンロードが完了しました"))
            if self.open_confirm.get():
                self.after(0, lambda: send_path(dl_path))
        except Exception as e:
            self.after(0, lambda: self.progress.set("エラー発生"))
            self.after(0, lambda: messagebox.showerror("エラー", f"ダウンロードに失敗しました\n{e}"))
        finally:
            self.after(0, lambda: self.download_button.config(state="normal"))


if __name__ == "__main__":
    vlc_player = videoPlayer()
    vlc_player.mainloop()
