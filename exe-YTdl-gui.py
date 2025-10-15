import os
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import threading
import cv2

# もともと関数ベースで作成していたものをクラスベースに変更（ChatGPTに完全委託）
# 軽く目を通したけどおそらく問題なし
# なんかあったら10/15の自分とChatGPTを恨め

class VideoDownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
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
        # self.cancel_flag = False

        # 各UI部品を構築
        self.create_widgets()

    # ----------------------------
    # UI構築
    # ----------------------------
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

        # # キャンセルボタン（今は無効）
        # self.cancel_button = tk.Button(button_frame, text="キャンセル", command=self.cancel_download, state="disabled")
        # self.cancel_button.pack(side="left", padx=5)

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

    # ----------------------------
    # 基本操作
    # ----------------------------
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

    # ----------------------------
    # ダウンロード処理
    # ----------------------------
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
        def progress_hook(d):
            if d['status'] == 'downloading':
                percent = d.get('_percent_str', '').strip()
                eta = d.get('_eta_str', '').strip()
                speed = d.get('_speed_str', '').strip()
                self.progress.set(f"進行中: {percent} | 残り: {eta} | 速度: {speed}")
            elif d['status'] == 'finished':
                self.progress.set("変換中...")

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
            self.progress.set("ダウンロード完了")
            messagebox.showinfo("完了", "ダウンロードが完了しました")
        except Exception as e:
            self.progress.set("エラー発生")
            messagebox.showerror("エラー", f"ダウンロードに失敗しました\n{e}")
        finally:
            self.download_button.config(state="normal")
            # self.cancel_button.config(state="disabled")


if __name__ == "__main__":
    app = VideoDownloaderApp()
    app.mainloop()
