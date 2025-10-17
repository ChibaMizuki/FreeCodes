# メンバーをシャッフルしてチーム分けするコード
# メンバー記入欄に追加されると新しい欄が動的に生成される
# 100%ChatGPT製
import tkinter as tk
import random

def add_entry(initial_text=""):
    """新しい Entry を作ってリストに追加。最後の欄に文字が入ったら次を追加する仕組み。"""
    var = tk.StringVar()
    entry = tk.Entry(entries_frame, textvariable=var, width=25)
    entry.pack(pady=3, anchor="w")
    entries.append((entry, var))

    # trace_add があれば使い、なければ古い trace を使う（互換処理）
    if hasattr(var, "trace_add"):
        var.trace_add("write", lambda *args, v=var: on_change(v))
    else:
        var.trace("w", lambda *args, v=var: on_change(v))

    entry.focus_set()
    if initial_text:
        var.set(initial_text)
    return entry, var

def on_change(var):
    """監視用コールバック：この var が最後の入力欄で、かつ非空になったら新たに欄を追加する。"""
    # entries の最後の var でなければ何もしない
    if not entries or entries[-1][1] is not var:
        return
    if var.get().strip() != "":
        # 最大数制限を付けたい場合はここでチェック（例: max_entries）
        add_entry()

def get_names():
    """空でない名前のみ取得"""
    return [v.get().strip() for e, v in entries if v.get().strip()]

def shuffle_teams():
    names = get_names()
    if len(names) < 2:
        result_var.set("名前を2人以上入力してください")
        return
    random.shuffle(names)
    half = len(names) // 2
    t1 = names[:half]
    t2 = names[half:]
    result_var.set(f"team1: {t1}\nteam2: {t2}")

# ------- GUI 構築 -------
root = tk.Tk()
root.title("チーム編成（自動追加）")
root.geometry("320x360")

entries_frame = tk.Frame(root)
entries_frame.pack(padx=10, pady=10, fill="both", expand=False)

entries = []
add_entry()  # 最初の1欄

shuffle_btn = tk.Button(root, text="シャッフル", command=shuffle_teams)
shuffle_btn.pack(pady=8)

result_var = tk.StringVar()
result_label = tk.Label(root, textvariable=result_var, justify="left")
result_label.pack(padx=10, pady=6, anchor="w")

root.mainloop()
