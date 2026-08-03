import cv2
import numpy as np

src = cv2.imread("image/img.png")

H, W = src.shape[:2]

src_cx = W / 2
src_cy = H / 2
max_r = min(src_cx, src_cy)

R = H
size = R * 2

dst = np.zeros((size, size, 3), np.uint8)

cx = cy = R

for Y in range(size):
    for X in range(size):

        dx = X - cx
        dy = Y - cy

        rho = np.sqrt(dx*dx + dy*dy)

        if rho >= R:
            continue

        theta = np.arctan2(dy, dx)

        if theta < 0:
            theta += 2*np.pi

        # 極座標変換
        # u = theta / (2*np.pi) * W
        # v = rho / R * H

        r_dash = (rho / R) ** 2 * max_r # 中心拡大
        r_dash = np.sqrt(rho / R) * max_r # 外側拡大
        u = src_cx + r_dash * np.cos(theta)
        v = src_cy + r_dash * np.sin(theta)

        dst[Y, X] = src[int(v), int(u)]

cv2.imwrite("circle.png", dst)