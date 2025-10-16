import os
from tkinter import filedialog, Tk, simpledialog, messagebox
from PIL import Image
import pillow_heif

# HEIC対応をPillowに登録
pillow_heif.register_heif_opener()

# tkinterのrootウィンドウを非表示にする
root = Tk()
root.withdraw()

# 対応形式
input_formats = [("画像ファイル", "*.png *.jpg *.jpeg *.heic")]

# 画像ファイルを選択
file_path = filedialog.askopenfilename(title="画像を選択", filetypes=input_formats)

if not file_path:
    print("ファイルが選択されませんでした。")
    exit()

# 画像を開く
try:
    image = Image.open(file_path)
except Exception as e:
    messagebox.showerror("エラー", f"画像の読み込みに失敗しました: {e}")
    exit()

# 元のサイズを取得
original_width, original_height = image.size

# 拡大・縮小率の入力（％）
scale_percent = simpledialog.askfloat("倍率入力", "拡大・縮小率を入力（例：50 = 半分, 200 = 2倍）:")

if scale_percent is None or scale_percent <= 0:
    messagebox.showerror("エラー", "倍率は0より大きい数値で指定してください。")
    exit()

# 新しいサイズを計算
new_width = int(original_width * scale_percent / 100)
new_height = int(original_height * scale_percent / 100)

# リサイズ
resized_image = image.resize((new_width, new_height))

# 出力形式の選択
output_format = simpledialog.askstring("出力形式", "出力形式を入力（png または jpg）:")
if output_format is None or output_format.lower() not in ["png", "jpg"]:
    messagebox.showerror("エラー", "png または jpg のみ対応しています。")
    exit()
output_format = output_format.lower()

# 保存先を選択
save_path = filedialog.asksaveasfilename(
    defaultextension=f".{output_format}",
    filetypes=[(f"{output_format.upper()} files", f"*.{output_format}")]
)

if not save_path:
    print("保存先が指定されませんでした。")
    exit()

# JPG保存時はRGBに変換
if output_format == "jpg" and resized_image.mode in ("RGBA", "P"):
    resized_image = resized_image.convert("RGB")

# 保存
try:
    resized_image.save(save_path)
    messagebox.showinfo("保存完了", f"画像が保存されました: {save_path}")
except Exception as e:
    messagebox.showerror("保存エラー", f"画像の保存に失敗しました: {e}")
