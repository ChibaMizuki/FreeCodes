# import yt_dlp
# import os

# def get_user_download_folder():
#         user_folder = os.path.expanduser("~")
#         return os.path.join(user_folder, "Downloads")

# url = "https://youtu.be/BI9Ue6JwJic?si=9dPcet32E44l9OYz"

# ydl_opts = {
#     "quiet": True,
#     "skip_download": True,  # 明示的にダウンロードしない
#     "remote_components": ["ejs:github"],
# }

# with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#     info = ydl.extract_info(url, download=False)

# formats = info["formats"]

# for f in formats:
#     print(
#         f"format_id={f.get('format_id')}, "
#         f"ext={f.get('ext')}, "
#         f"resolution={f.get('resolution')}, "
#         f"fps={f.get('fps')}, "
#         f"vcodec={f.get('vcodec')}, "
#         f"acodec={f.get('acodec')}"
#     )

import yt_dlp

url = "https://youtu.be/BI9Ue6JwJic?si=9dPcet32E44l9OYz"

ydl_opts = {
    # 最高品質（video+audio を自動で選択）
    "format": "bv*+ba/b",

    # JSチャレンジ対応（最重要）
    "remote_components": ["ejs:github"],

    # 出力ファイル名
    "outtmpl": "%(title)s.%(ext)s",
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([url])
