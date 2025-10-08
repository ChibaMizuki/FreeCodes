import os
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import threading

# yt-dlpのアプデ
# pip install --upgrade yt-dlp

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        save_path.set(folder)

def download_video():
    url = url_entry.get()
    folder = save_path.get()

    if not url:
        messagebox.showerror("エラー", "URLを入力してください")
        return
    if not folder:
        messagebox.showerror("エラー", "保存先フォルダを選択してください")
        return
    
    os.makedirs(folder, exist_ok=True)

    download_button.config(state="disabled")
    progress.set("ダウンロード開始...")

    thread = threading.Thread(target=run_download, args=(url, folder), daemon=True)
    thread.start()

def run_download(url, folder):
    # yt-dlpのprogress_hooksは随時情報更新し、指定した関数を毎回呼び出して辞書を渡す
    # {
    # 'status': 'downloading',     # 現在の状態: downloading / finished など
    # 'filename': 'example.mp4',   # 出力中のファイル名
    # 'downloaded_bytes': 1234567, # 今ダウンロード済みのバイト数
    # 'total_bytes': 5678901,      # 全体のファイルサイズ
    # '_percent_str': '21.3%',     # 見やすい形での進行率（文字列）
    # '_eta_str': '00:34',         # 残り時間（見やすい文字列）
    # '_speed_str': '1.4MiB/s',    # 現在の速度
    # 'elapsed': 4.23,             # 経過時間（秒）
    # }

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '').strip()
            eta = d.get('_eta_str', '').strip()
            speed = d.get('_speed_str', '').strip()
            progress.set(f"進行中: {percent} | 残り: {eta} | 速度: {speed}")
        elif d['status'] == 'finished':
            progress.set("変換中...")

    # key: 取り出したいキー名　default: キーがなかった時に返す値
    # d.get('key', 'default') とすることにより、keyが存在しなかった場合（＝ KeyErrorが発生）に
    # プログラムが終了しないようにしている（defaultを返す）

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
        progress.set("ダウンロード完了")
        messagebox.showinfo("完了", "ダウンロードが完了しました")
    except Exception as e:
        progress.set("エラー発生")
        messagebox.showerror("エラー", f"ダウンロードに失敗しました\n{e}")
    finally:
        download_button.config(state="normal")

def close():
    root.destroy()

def clear_entry():
    url_entry.delete(0, tk.END)


root = tk.Tk()
root.title("動画ダウンローダー")
root.geometry("600x300")

tk.Label(root, text="動画URL:").pack(anchor="w", padx=10, pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack(padx=10, pady=5)
tk.Button(root, text="URLクリア", command=clear_entry).pack(anchor="w", padx=10, pady=5)

save_path = tk.StringVar()
path_frame = tk.Frame(root)
path_frame.pack(anchor="w", padx=10, pady=5)
tk.Label(path_frame, text="保存先: ").pack(side="left")
tk.Entry(path_frame, textvariable=save_path, width=45).pack(side="left", padx=5)
tk.Button(path_frame, text="選択", command=select_folder).pack(side="left")

download_button = tk.Button(root, text="ダウンロード", command=download_video)
download_button.pack(pady=15)

progress = tk.StringVar()
progress.set("待機中...")
tk.Label(root, textvariable=progress, fg="blue").pack(pady=5)

tk.Button(root, text="終了", command=close).pack(pady=5)

root.mainloop()
