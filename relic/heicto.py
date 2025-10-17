# HEICをJPG or PNG に変換するコード
# 99%ChatGPT製
import os
from tkinter import Tk, filedialog
from PIL import Image
import pillow_heif

def convert_heic_to_image(input_path, output_path, format="JPEG"):
    """HEICファイルをJPEGまたはPNGに変換する関数"""
    heif_file = pillow_heif.read_heif(input_path)
    image = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw"
    )
    image.save(output_path, format=format)
    print(f"変換完了: {output_path}")


if __name__ == "__main__":
    # Tkinterの画面を表示しないようにする
    root = Tk()
    root.withdraw()

    # HEICファイルを選択
    input_file = filedialog.askopenfilename(
        title="変換したいHEICファイルを選択してください",
        filetypes=[("HEIC files", "*.heic"), ("All files", "*.*")]
    )

    if not input_file:
        print("ファイルが選択されませんでした。")
        exit()

    # 保存先を指定
    output_file = filedialog.asksaveasfilename(
        title="保存先を選んでください",
        defaultextension=".jpg",
        filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")]
    )

    if not output_file:
        print("保存先が指定されませんでした。")
        exit()

    # 拡張子から形式を判定
    ext = os.path.splitext(output_file)[1].lower()
    if ext == ".jpg" or ext == ".jpeg":
        fmt = "JPEG"
    elif ext == ".png":
        fmt = "PNG"
    else:
        print("対応していない拡張子です。")
        exit()

    # 変換実行
    convert_heic_to_image(input_file, output_file, format=fmt)
