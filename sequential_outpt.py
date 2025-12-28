import cv2
import os

def seq_output(video, output_path):
    video = cv2.VideoCapture(video)
    
    if not video.isOpened():
        return
    
    os.makedirs(output_path, exist_ok=True)
    
    
video = "test/video/text.mp4"
output_path = "video/seq_video"
basename = "test"