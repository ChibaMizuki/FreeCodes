from color_palette import color_palette
import cv2
import numpy as np


img = cv2.imread("video/small_img.png")
if img is None:
    raise RuntimeError("画像の読み込みに失敗しています")

img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

print(img.shape)
r_min, g_min, b_min = img.min(axis=(0, 1))
r_max, g_max, b_max = img.max(axis=(0, 1))

print()
print(f"max: r{r_max} g{g_max} b{b_max}")
print(f"min: r{r_min} g{g_min} b{b_min}")