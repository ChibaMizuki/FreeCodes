import cv2
import os

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
        for n in range(start, finish):
            video.set(cv2.CAP_PROP_POS_FRAMES, n)
            ret, frame = video.read()

            if ret:
                cv2.imwrite(f"{base_path}_{f:04}.jpg", frame)
                f += 1
            else:
                return
    

start = 30
finish = 45 
video = "test/video/irisout.mp4"
output_path = "video"
basename = "test"

seq_output(video, output_path, basename, start=start, finish=finish)