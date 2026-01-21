from color_palette import color_palette
import cv2
import numpy as np

# ここら辺の処理はlexsortで簡略化できるっぽい
def rgb_diff(color_array:np.ndarray):
    r_max, g_max, b_max = color_array.max(axis=(0, 1))
    r_min, g_min, b_min = color_array.min(axis=(0, 1))
    r_diff = r_max - r_min
    g_diff = g_max - g_min
    b_diff = b_max - b_min

    if (r_diff == g_diff) and (g_diff == b_diff):
        diff_order = [0, 1, 2]

    elif (r_diff != g_diff) and (r_diff != b_diff) and (g_diff != b_diff):
        diffs = np.array([r_diff, g_diff, b_diff])
        diff_order = np.argsort(diffs)[::-1].tolist()

    else:
        diffs = [r_diff, g_diff, b_diff]
        max_value = max(diffs)
        min_value = min(diffs)
        if diffs.count(max_value) > diffs.count(min_value):
            diff_order = [0, 1]
            diff_order.insert(diffs.index(min_value), 2)
        else:
            diff_order = [1, 2]
            diff_order.insert(diffs.index(max_value), 0)

    return diff_order

def three_to_two(color_array:np.ndarray):
    return np.reshape(color_array, [-1, 3])

def two_to_three(color_array:np.ndarray, h:int, w:int):
    return np.reshape(color_array, [h, w, 3])

def sort_colors(color_array:np.ndarray, index:list):
    sort_index = np.lexsort((color_array[:, index[2]], color_array[:, index[1]], color_array[:, index[0]]))
    return color_array[sort_index]

def divide_colors(color_array:np.ndarray):
    size = color_array.shape[0]
    num = int(size / 2)
    forward = color_array[:num, :]
    backward = color_array[num:, :]
    return forward, backward

def make_color(color_array:np.ndarray):
    color_array = three_to_two(color_array)
    num = color_array.shape[0]
    total_rgb = np.sum(color_array, axis=0)
    rgb = (total_rgb / num)
    rgb = rgb.astype(int).tolist()
    return rgb

if __name__ == "__main__":
    img = cv2.imread("video/small_img.png")
    if img is None:
        raise RuntimeError("画像の読み込みに失敗しています")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    need_color = 4
    color = []
    divided_colors = []
    while len(color) < need_color:
        if not color:
            h, w, _ = img.shape
            # RGB最大値と最小値の差比較
            color_index = rgb_diff(img)
            # 3次元配列->2次元配列でRGB情報取得
            two_dim_colors = three_to_two(img)
            # 差が最大のものでピクセルをソート
            sorted_color = sort_colors(two_dim_colors, color_index)
            # 半分分割
            forward, backward = np.split(sorted_color, 2)
            # 2次元配列->3次元配列
            forward = two_to_three(forward, int(h/2), w)
            backward = two_to_three(backward, int(h/2), w)
            divided_colors.append(forward)
            divided_colors.append(backward)
            color.append(make_color(forward))
            color.append(make_color(backward))
        else:
            for i in range(len(divided_colors)):
                h, w, _ = divided_colors[i].shape
                # RGB最大値と最小値の差比較
                color_index = rgb_diff(divided_colors[i])
                # 3次元配列->2次元配列でRGB情報取得
                two_dim_colors = three_to_two(divided_colors[i])
                # 差が最大のものでピクセルをソート
                sorted_color = sort_colors(two_dim_colors, color_index)
                # 半分分割
                forward, backward = divide_colors(sorted_color)
                # 2次元配列->3次元配列
                forward_height = int(h / 2)
                backward_height = h - forward_height
                forward = two_to_three(forward, forward_height, w)
                backward = two_to_three(backward, backward_height, w)
                divided_colors.append(forward)
                divided_colors.append(backward)
                color.append(make_color(forward))
                color.append(make_color(backward))

    palette = color_palette(color, mode="h")
    cv2.imshow("", palette)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
