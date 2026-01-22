from color_palette import color_palette
import cv2
import numpy as np

# ここら辺の処理はlexsortで簡略化できるっぽい
def rgb_diff(color_array:np.ndarray):
    r_max, g_max, b_max = color_array.max(axis=0)
    r_min, g_min, b_min = color_array.min(axis=0)
    r_diff = r_max - r_min
    g_diff = g_max - g_min
    b_diff = b_max - b_min

    max_value = max(r_diff, g_diff, b_diff)
    if r_diff == max_value:
        sort_value = "r"
    elif g_diff == max_value:
        sort_value = "g"
    elif b_diff == max_value:
        sort_value = "b"

    return sort_value

def three_to_two(color_array:np.ndarray):
    return np.reshape(color_array, [-1, 3])

def two_to_three(color_array:np.ndarray, h:int, w:int):
    return np.reshape(color_array, [h, w, 3])

def sort_colors(color_array:np.ndarray, value:str):
    if value == "r":
        color_array = color_array[color_array[:, 0].argsort()]
    elif value == "g":
        color_array = color_array[color_array[:, 1].argsort()]
    elif value == "b":
        color_array = color_array[color_array[:, 2].argsort()]

    return color_array

def divide_colors(color_array:np.ndarray):
    size = color_array.shape[0]
    num = size // 2
    forward = color_array[:num, :]
    backward = color_array[num:, :]
    return forward, backward

def make_color(color_array:np.ndarray):
    color_array = three_to_two(color_array)
    num = color_array.shape[0]
    total_rgb = np.sum(color_array, axis=0)
    rgb = np.round((total_rgb / num)).astype(np.uint8)
    rgb = rgb.tolist()
    return rgb

def median_cut(color_bucket:np.ndarray):
    sort_value = rgb_diff(color_bucket)
    sorted_color = sort_colors(color_bucket, sort_value)
    forward, backward = divide_colors(sorted_color)
    return forward, backward

def get_max_range_index(bucket:np.ndarray):
    max_value = []
    for b in bucket:
        r_max, g_max, b_max = b.max(axis=0)
        r_min, g_min, b_min = b.min(axis=0)
        r_diff = r_max - r_min
        g_diff = g_max - g_min
        b_diff = b_max - b_min

        max_value.append(max(r_diff, g_diff, b_diff).item())
    max_range = max(max_value)
    max_index = max_value.index(max_range)
    return max_index

if __name__ == "__main__":
    img = cv2.imread("video/small_img.png")
    if img is None:
        raise RuntimeError("画像の読み込みに失敗しています")

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    need_color = 8
    color = []
    bucket = [three_to_two(img)]
    # 1.バケット選択 <- 最大レンジを持つバケット
    # 2.カラーチャンネル取得
    # 3.2.でソート
    # 4.中央値で分割
    # 5.繰り返し
    while len(bucket) < need_color:
        index = get_max_range_index(bucket)
        max_range_bucket = bucket.pop(index)

        forward, backward = median_cut(max_range_bucket)
        bucket.append(forward)
        bucket.append(backward)

    for i in range(len(bucket)):
        color.append(make_color(bucket[i]))
    print(color)
    palette = color_palette(color)
    cv2.imshow("", palette)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
