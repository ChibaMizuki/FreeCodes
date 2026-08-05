import numpy as np
import matplotlib.pyplot as plt

def distance(x, y, num):
    point_array = np.stack([x, y], 1)
    dist = 0
    for i in range(num):
        for j in range(i, num):
            d = np.linalg.norm(point_array[i] - point_array[j])
            if d > dist:
                dist = d
                p1 = i
                p2 = j
    
    print(dist)
    print(p1, p2)

    return p1, p2


point_num = 20
x = np.random.rand(point_num) * 100
y = np.random.rand(point_num) * 100
p1, p2 = distance(x, y, point_num)
_x = [x[p1], x[p2]]
_y = [y[p1], y[p2]]

plt.figure()
plt.scatter(x, y, s=5, c="blue", alpha=0.6) # s→size, c→color
plt.plot(_x, _y)

plt.axis("off") # 目盛りや枠を全部非表示
plt.axis('equal')
plt.show()