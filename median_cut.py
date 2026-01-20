from color_palette import color_palette
import cv2
import numpy as np


img = cv2.imread("video/small_img.png")
if img is None:
    raise RuntimeError("画像の読み込みに失敗しています")

img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# # 要素の取得の例
# py_array = [[[ 30, 128,   0], [240, 120,  24], [ 39, 100, 140]], 
#             [[222, 220, 255], [  3, 249,  99], [180, 181, 182]],
#             [[ 50,  60, 250], [ 44,  69, 175], [239, 205,   1]]]
# np_array = np.array(py_array)

# # axisは潰すという考え方らしい
# # np_array[i][j][k]
# # i -> axis0
# # j -> axis1
# # k -> axis2
# print(np_array.max(axis=0))
# print(np_array.max(axis=1))
# print(np_array.max(axis=2))
# # axis = 0
# # [[222 220 255]
# #  [240 249 175]
# #  [239 205 182]]

# # axis = 1
# # [[240 128 140]
# #  [222 249 255]
# #  [239 205 250]]

# # axis = 2
# # [[128 240 140]
# #  [255 249 182]
# #  [250 175 239]]
# print(np_array.max(axis=(0, 1))) # 縦と横の同時比較      -> RGBの全体比較
# print(np_array.max(axis=(1, 2))) # 横とその要素の同時比較 -> 行の最大値
# print(np_array.max(axis=(0, 2))) # 縦とその要素の同時比較 -> 列の最大値
# # sxis = 0, 1
# # [240 249 255]
# # axis = 1, 2
# # [240 255 250]
# # axis = 0, 2
# # [255 249 239]

# axisは i, j, kのうちどれを動かして比較するか指定する
print(img.shape)
r_min, g_min, b_min = img.min(axis=(0, 1))
r_max, g_max, b_max = img.max(axis=(0, 1))

print()
print(f"max: r{r_max} g{g_max} b{b_max}")
print(f"min: r{r_min} g{g_min} b{b_min}")