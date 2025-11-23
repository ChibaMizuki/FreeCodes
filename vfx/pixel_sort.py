import numpy as np

def pixel_sort(clip, mode="brightness"):
    """
    Pixel sorting effect.
    mode = "brightness" / "red" / "green" / "blue"
    """

    def apply(frame):
        # frame: (H, W, 3) の uint8

        # 画像を float にする（計算しやすくする）
        img = frame.astype(np.float32)

        # H:行数, W:列数
        H, W, _ = img.shape

        # 出力画像
        sorted_img = np.zeros_like(img)

        for y in range(H):
            row = img[y]   # (W, 3) y行目のRGBを取得

            if mode == "brightness":
                # 輝度（明るさ）= 0.299R + 0.587G + 0.114B
                key = 0.299 * row[:, 0] + 0.587 * row[:, 1] + 0.114 * row[:, 2]
            elif mode == "red":
                key = row[:, 0]
            elif mode == "green":
                key = row[:, 1]
            elif mode == "blue":
                key = row[:, 2]
            else:
                key = np.random.rand(W)

            # sort()が配列を返すのに対し、argsort()はソート後のインデックスを返す
            # 並び替えたインデックスを取得
            idx = np.argsort(key)

            # ピクセルを並び替え
            sorted_img[y] = row[idx]

        # uint8 に戻す
        return np.clip(sorted_img, 0, 255).astype(np.uint8)

    return clip.fl_image(apply)

# 0  1  2  3  4  行番号
# 30 78 66 40 19　輝度
# 1  4  3  2  0　　順番
# ->
# 4  0  3  2  1
# 19 30 40 66 78 sorted_img

