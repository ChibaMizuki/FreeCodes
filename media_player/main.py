import os
import sys
from PySide6.QtWidgets import QApplication
from player import VideoPlayer

base_dir = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
vlc_dir = os.path.join(base_dir, "vlc")

os.environ["VLC_PLUGIN_PATH"] = os.path.join(vlc_dir, "plugins")

def main():
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
