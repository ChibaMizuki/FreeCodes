import subprocess
import sys, os
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp

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

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s')
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("完了", "ダウンロードが完了しました")
    except Exception as e:
        messagebox.showerror("エラー", f"ダウンロードに失敗しました\n{e}")

def close():
    root.destroy()

def clear_entry():
    url_entry.delete(0, tk.END)


root = tk.Tk()
root.title("動画ダウンローダー")
root.geometry("600x300")

tk.Label(root, text="動画URL: ").pack(anchor="w", padx=10, pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack(padx=10, pady=5)
tk.Button(root, text="URLクリア", command=clear_entry).pack(anchor="w", padx=10, pady=5)

save_path = tk.StringVar()
tk.Label(root, text="保存先: ").pack(anchor="w", padx=10, pady=5)
tk.Entry(root, textvariable=save_path, width=45).pack(side="left", padx=10, pady=5)
tk.Button(root, text="選択", command=select_folder).pack(side="left", padx=5)

tk.Button(root, text="ダウンロード", command=download_video).pack(pady=20)
tk.Button(root, text="終了", command=close).pack(pady=5)

root.mainloop()
