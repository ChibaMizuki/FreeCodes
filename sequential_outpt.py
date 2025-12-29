import cv2
import os
import glob

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
            
    video.release()

def make_video_from_seq(file_path, output_path=None):
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    video = cv2.VideoWriter("test.mp4", fourcc, 30, (1920, 1080))

    i = 1
    while True:
        file = glob.glob(f"{file_path}/*_%04d.jpg" % i)
        if not file:
            break
        img = cv2.imread(file[0])
        i += 1

        if img is None:
            break

        video.write(img)

    video.release()



start = 30
finish = 180
video = "test/video/irisout.mp4"
output_path = "video"
basename = "test"

# seq_output(video, output_path, basename, start=start, finish=finish)
make_video_from_seq(output_path)