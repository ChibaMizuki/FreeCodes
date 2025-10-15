import os
import tkinter as tk
from tkinter import filedialog, messagebox
import yt_dlp
import threading

# yt-dlpのアプデ
# pip install --upgrade yt-dlp
# exe化
# pyinstaller --noconsole --onefile main.py

# キャンセル管理
cancel_flag = False

# 保存フォルダを開く
def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        save_path.set(folder)

# ダウンロードを開始する
def download_video():
    global cancel_flag
    cancel_flag = False

    url = url_entry.get()
    folder = save_path.get()

    if not url:
        messagebox.showerror("エラー", "URLを入力してください")
        return
    if not folder:
        messagebox.showerror("エラー", "保存先フォルダを選択してください")
        return
    
    # withがなくても動作自体はするが、使うことにより処理が安全に終了する
    try:
        ydl_opts = {'quiet': True, 'no_warning': True, 'skip_dowaload': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get("title", "不明なタイトル")
    except Exception as e:
        messagebox.showerror("エラー", f"動画情報の取得に失敗しました\n{e}")
        return
    
    confirm = messagebox.askyesno("確認", f"『{title}』をダウンロードしますか？")
    if not confirm:
        progress.set("キャンセルされました")
        return
    
    os.makedirs(folder, exist_ok=True)

    download_button.config(state="disabled")
    progress.set("ダウンロード開始...")

    thread = threading.Thread(target=run_download, args=(url, folder), daemon=True)
    thread.start()

# ダウンロード状況の確認と実行
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
        global cancel_flag
        if cancel_flag:
            raise yt_dlp.utils.DownloadError("ユーザーによるキャンセル")
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
    except yt_dlp.utils.DownloadError as e:
        if "キャンセル" in str(e):
            progress.set("キャンセルしました")
        else:
            progress.set("エラー発生")
            messagebox.showerror("エラー", f"ダウンロードに失敗しました\n{e}")
    except Exception as e:
        progress.set("エラー発生")
        messagebox.showerror("エラー", f"ダウンロードに失敗しました\n{e}")
    finally:
        download_button.config(state="normal")
        cancel_button.config(state="disabled")

# キャンセル処理
def cancel_download():
    global cancel_flag
    cancel_flag = True
    progress.set("キャンセル中...")

# ウィンドウを閉じる
def close():
    root.destroy()

# URLをクリア
def clear_entry():
    url_entry.delete(0, tk.END)

# ダウンロードフォルダの取得
def get_user_download_folder():
    user_folder = os.path.expanduser("~")
    folder = os.path.join(user_folder, "Downloads")
    
    return folder


root = tk.Tk()
root.title("動画ダウンローダー")
root.geometry("1000x600")

# URL
tk.Label(root, text="動画URL:").pack(anchor="w", padx=10, pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.pack(padx=10, pady=5)
tk.Button(root, text="URLクリア", command=clear_entry).pack(anchor="w", padx=10, pady=5)

# 保存先
# StringVarはvalue=""で初期値を設定する
init_save_path = get_user_download_folder()
save_path = tk.StringVar(value=init_save_path)
path_frame = tk.Frame(root)
path_frame.pack(anchor="w", padx=10, pady=5)
tk.Label(path_frame, text="保存先: ").pack(side="left")
tk.Entry(path_frame, textvariable=save_path, width=45).pack(side="left", padx=5)
tk.Button(path_frame, text="選択", command=select_folder).pack(side="left")

# ダウンロード
button_frame = tk.Frame(root)
button_frame.pack(pady=10)
download_button = tk.Button(button_frame, text="ダウンロード", command=download_video)
download_button.pack(side="left", padx=5)
cancel_button = tk.Button(button_frame, text="キャンセル", command=cancel_download, state="disabled")
cancel_button.pack(side="left", padx=5)

# チェックボックス
confirm_frame = tk.Frame(root)
confirm_frame.pack(pady=10)
title_confirm = tk.BooleanVar(value=True)
tc_button = tk.Checkbutton(root, text="ダウンロード前に確認ダイアログを表示する", variable=title_confirm)
tc_button.pack(side="left")

# 進捗
progress = tk.StringVar()
progress.set("待機中...")
tk.Label(root, textvariable=progress, fg="blue").pack(pady=5)

# 閉じるボタン
tk.Button(root, text="終了", command=close).pack(pady=5)

root.mainloop()
