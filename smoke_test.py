"""Smoke-test the uv-managed Python environment."""

from __future__ import annotations

import importlib
import platform
import sys


MODULES = {
    "certifi": "certifi",
    "charset-normalizer": "charset_normalizer",
    "colorama": "colorama",
    "decorator": "decorator",
    "idna": "idna",
    "imageio": "imageio",
    "imageio-ffmpeg": "imageio_ffmpeg",
    "lazy-loader": "lazy_loader",
    "moviepy": "moviepy",
    "networkx": "networkx",
    "numpy": "numpy",
    "opencv-python": "cv2",
    "packaging": "packaging",
    "pillow": "PIL",
    "pillow-heif": "pillow_heif",
    "proglog": "proglog",
    "Pygments": "pygments",
    "PySide6": "PySide6",
    "python-dotenv": "dotenv",
    "python-vlc": "vlc",
    "qrcode": "qrcode",
    "QtPy": "qtpy",
    "requests": "requests",
    "scikit-image": "skimage",
    "scipy": "scipy",
    "superqt": "superqt",
    "tifffile": "tifffile",
    "tqdm": "tqdm",
    "typing-extensions": "typing_extensions",
    "urllib3": "urllib3",
    "yt-dlp": "yt_dlp",
}


def test_python_runtime() -> None:
    values = [5, 1, 4, 2, 3]
    assert sorted(value * value for value in values) == [1, 4, 9, 16, 25]
    print(f"[OK] Python {platform.python_version()}")
    print(f"[OK] Executable: {sys.executable}")


def test_imports() -> None:
    failures: list[str] = []
    for package, module in MODULES.items():
        try:
            imported = importlib.import_module(module)
            version = getattr(imported, "__version__", "version attribute unavailable")
            print(f"[OK] import {module} ({package}: {version})")
        except Exception as exc:  # Report every failed import in one run.
            failures.append(f"{package} -> {module}: {type(exc).__name__}: {exc}")

    if failures:
        raise RuntimeError("Import failures:\n" + "\n".join(failures))


def test_numeric_and_image_processing() -> None:
    import cv2
    import numpy as np
    from scipy.spatial import ConvexHull

    image = np.zeros((8, 8, 3), dtype=np.uint8)
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    assert grayscale.shape == (8, 8)

    points = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0.5, 0.5]])
    hull = ConvexHull(points)
    assert len(hull.vertices) == 4
    print("[OK] NumPy + OpenCV image processing")
    print("[OK] SciPy convex-hull calculation")


def main() -> None:
    test_python_runtime()
    test_imports()
    test_numeric_and_image_processing()
    print("\nAll smoke tests passed.")


if __name__ == "__main__":
    main()
