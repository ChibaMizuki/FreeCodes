from color_palette import color_palette
import cv2
import numpy as np


img = cv2.imread("video/small_img.png")
if img is None:
    raise RuntimeError("画像の読み込みに失敗しています")

img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# # 要素の取得の例
py_array = [[[ 30, 249,   0], [240, 120,  24], [ 39, 100, 140]], 
            [[222, 220, 255], [ 30, 128,  99], [180, 181, 182]],
            [[ 50,  60, 250], [ 44,  69, 175], [239, 205,   1]]]
np_array = np.array(py_array)
h, w, _ = np_array.shape # 配列サイズ

# RGB情報を保持しておくため3次元配列を2次元配列に変換

# lower_dim = []
# for i in range(np_array.shape[0]):
#     for j in range(np_array.shape[1]):
#         lower_dim.append(np_array[i][j].tolist())

# 上記は以下1行に書き換えられる
lower_dim = np.reshape(np_array, [-1, 3]) # -1とすると、ほかの要素から自動推定してくれる（もしくはh*w）

# # Rの値を取得

# r_array = []
# for i in range(len(lower_dim)):
#     r_array.append(lower_dim[i][0])
# # ソートしてインデックスを取得
# sorted_index = np.argsort(r_array)
# sorted_index = sorted_index.tolist()

# インデックスに基づいてRGB配列を並べかえ
# sorted_array = []
# for i in range(len(sorted_index)):
#     sorted_array.append(lower_dim[sorted_index[i]])
# print(np.array(sorted_array))

# R値でソートするのも以下でまとまる
sorted_array = lower_dim[np.argsort(lower_dim[:, 0])] # 2次元配列のR要素で並べ替え
print(sorted_array)

# # 2次元から3次元に戻す

# array_sorted_by_r = []
# for i in range(np_array.shape[0]):
#     row = []
#     for j in range(np_array.shape[1]):
#         row.append(sorted_array[i*np_array.shape[0]+j])
#     array_sorted_by_r.append(row)
# print(np.array(array_sorted_by_r))

# これもreshapeが使える
array_sorted_by_r = np.reshape(sorted_array, [h, w, 3])
print(array_sorted_by_r)


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
r_diff = r_max - r_min
g_diff = g_max - g_min
b_diff = b_max - b_min

diff_max = max(r_diff, g_diff, b_diff)


print()
print(f"max: r{r_max} g{g_max} b{b_max}")
print(f"min: r{r_min} g{g_min} b{b_min}")