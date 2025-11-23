from skimage.filters import gaussian
import numpy as np


def gaussian_blur(clip, sigma=2):
    """Apply Gaussian blur to each frame of the clip."""

    def apply_blur(frame):
        # frame: (H, W, 3) uint8
        img_float = frame.astype(np.float32) / 255.0
        blurred = gaussian(img_float, sigma=sigma, channel_axis=-1)
        blurred_uint8 = (blurred * 255).clip(0, 255).astype(np.uint8)
        return blurred_uint8

    return clip.fl_image(apply_blur)
