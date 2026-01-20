import math
import numpy as np

MODE = {"s", "v", "h"}
CELL_SIZE = 120

def color_palette(color:list, mode:str=None):
    if not color:
        raise ValueError("colors must not be empty")
    if not mode or not mode in MODE:
        mode = "s"

    if mode == "s":
        d = math.ceil(math.sqrt(len(color)))
        size = d * CELL_SIZE
        palette = np.zeros((size, size, 3), dtype=np.uint8)

        for i in range(d):
            for j in range(d):
                if (i * d + j) < len(color):
                    palette[i*CELL_SIZE:(i+1)*CELL_SIZE, j*CELL_SIZE:(j+1)*CELL_SIZE, :] = color[i*d+j][::-1]

    elif mode == "v":
        d = len(color)
        width = CELL_SIZE
        height = CELL_SIZE * d
        palette = np.zeros((height, width, 3), dtype=np.uint8)

        for i in range(d):
            palette[i*CELL_SIZE:(i+1)*CELL_SIZE, :, :] = color[i][::-1]

    elif mode == "h":
        d = len(color)
        width = CELL_SIZE * d
        height = CELL_SIZE
        palette = np.zeros((height, width, 3), dtype=np.uint8)

        for i in range(d):
            palette[:, i*CELL_SIZE:(i+1)*CELL_SIZE, :] = color[i][::-1]

    return palette
