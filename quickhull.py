import numpy as np
import matplotlib.pyplot as plt

def find_farthest_pair(point_array, num):
    dist = 0
    for i in range(num):
        for j in range(i, num):
            d = np.linalg.norm(point_array[i] - point_array[j])
            if d > dist:
                dist = d
                p1 = i
                p2 = j

    return p1, p2

def cross_product(a, b, p):
    # 2次元の場合は直接計算式を記述する仕様になってるっぽい？
    # return np.cross(b-a, p-a) 
    
    v1 = b - a
    v2 = p - a
    return v1[0] * v2[1] - v1[1] * v2[0]

def search_farthest_point(point_array, a, b):
    norm_ab = np.linalg.norm(b - a)
    distance = 0
    for p in point_array:
        c =  np.abs(cross_product(a, b, p))
        l = c / norm_ab
        if l > distance:
            distance = l
            farthest = p

    return farthest

def search_outside(point_array, a, b, fp):
    os_c1 = []
    os_c2 = []
    for p in point_array:
        c1 = cross_product(a, fp, p)
        c2 = cross_product(fp, b, p)
        if c1 > 0:
            os_c1.append(p)
        if c2 > 0:
            os_c2.append(p)
            
    return os_c1, os_c2

def quickhull(edge, array, a, b):
    fp = search_farthest_point(array, a, b)
    # plt.plot(fp[0], fp[1], c="gold", marker="*", markersize=15)
    os_c1, os_c2 = search_outside(array, a, b, fp)
    # for p in os_c1:
    #     plt.plot(p[0], p[1], c="red", marker="o")
    # for p in os_c2:
    #     plt.plot(p[0], p[1], c="green", marker="o")
    
    if os_c1:
        quickhull(edge, os_c1, a, fp)
    else:
        edge.append((a, fp))
        
    if os_c2:
        quickhull(edge, os_c2, fp, b)
    else:
        edge.append((fp, b))
        
    

point_num = 50
x = np.random.rand(point_num) * 100
y = np.random.rand(point_num) * 100
points = np.stack([x, y], 1)
plt.figure()
plt.scatter(x, y, marker=".")
plt.axis("off") # 目盛りや枠を全部非表示
plt.axis('equal')

p1, p2 = find_farthest_pair(points, point_num)
# plt.plot(
#     [points[p1][0], points[p2][0]],
#     [points[p1][1], points[p2][1]],
#     c="blue",
#     marker="."
#     )

a = points[p1]
b = points[p2]
upper_points = []
lower_points = []
for i, p in enumerate(points):
    if i == p1 or i == p2:
        continue
    c = cross_product(a, b, p)
    if c > 0:
        upper_points.append(p)
    elif c < 0:
        lower_points.append(p)
    else:
        continue

edge = []
quickhull(edge, upper_points, a, b)
quickhull(edge, lower_points, b, a)
print(edge)
for a, b, in edge:
    plt.plot([a[0], b[0]], [a[1], b[1]], c="red", marker="*", lw=1)


plt.show()