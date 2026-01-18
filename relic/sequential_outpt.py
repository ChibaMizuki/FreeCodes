import cv2
import os
import glob
import numpy as np
import tempfile

def seq_output(video, output_path, basename, start:int, finish:int):
    if start < 0:
        start = 0
    if finish < 0:
        finish = 0

    video = cv2.VideoCapture(video)
    
    if not video.isOpened():
        return
    
    os.makedirs(output_path, exist_ok=True)
    # output_path/basename という構造を作成
    base_path = os.path.join(output_path, basename)

    f = 1

    if (start != finish) and (start < finish):
        video.set(cv2.CAP_PROP_POS_FRAMES, start)
        for _ in range(start, finish):
            ret, frame = video.read()

            if ret:
                cv2.imwrite(f"{base_path}_{f:04}.jpg", frame)
                f += 1
            else:
                print("could not get image")
                break
            
    video.release()

def make_video_from_seq(file_path, output_path=None, fps=30):

    def sort_file(file:list):
        # spl_list = []
        # sorted_list = []
        # for f in file:
        #     spl = f.split(".")[0]
        #     spl_list.append(int(spl[-4:]))

        # sort_key = np.argsort(spl_list)
        # sort_key = sort_key.tolist()

        # for f in sort_key:
        #     sorted_list.append(file[f])
        # return sorted_list
        # ここまで長ったらしく書かずとも↓で十分とのこと
        return sorted(
            file,
            key=lambda f: int(os.path.splitext(f)[0][-4:])
        )

    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    file = glob.glob(f"{file_path}/*_[0-9][0-9][0-9][0-9].jpg")
    sorted_file = sort_file(file)

    first_image = cv2.imread(sorted_file[0])
    height, width, _ = first_image.shape
    tmp = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    tmp.close()
    video = cv2.VideoWriter(tmp.name, fourcc, fps, (width, height))

    try:
        for f in sorted_file:
            img = cv2.imread(f)
            if img is None:
                print(f"skip: {f}")
                continue
            video.write(img)
    finally:
        video.release()
        os.remove(tmp.name)


start = 30
finish = 180
video = "test/video/irisout.mp4"
output_path = "video"
file_path = "video"
basename = "test"

# seq_output(video, output_path, basename, start=start, finish=finish)
make_video_from_seq(file_path)