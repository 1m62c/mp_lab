import csv

landmark_output_path = 'landmarks_output_practice.csv'
csv_file = open(landmark_output_path, 'w', newline='')
csv_writer = csv.writer(csv_file)

# ヘッダー行（frame, joint_index, x, y, z, visibility）
csv_writer.writerow(['frame', 'joint', 'x', 'y', 'z', 'visibility'])





import numpy as np
import matplotlib.pyplot as plt
import cv2
import mediapipe as mp
import pandas as pd

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

# 動画ファイル読み込み
input_filename = 'movie_practice.mp4'
video_data = cv2.VideoCapture(input_filename)
video_width = int(video_data.get(cv2.CAP_PROP_FRAME_WIDTH))    
video_hight = int(video_data.get(cv2.CAP_PROP_FRAME_HEIGHT))
video_fps = video_data.get(cv2.CAP_PROP_FPS)

print('FPS:',video_data.get(cv2.CAP_PROP_FPS))
print('Dimensions:',video_width,video_hight)

video_data_array = []

print("VideoFrame:",int(video_data.get(cv2.CAP_PROP_FRAME_COUNT)))

#ファイルが正常に読み込めている間ループする
while video_data.isOpened():
  #1フレームごとに読み込み
  success, image = video_data.read()
  if success:
    #フレームの画像を追加
    video_data_array.append(image)
  else:
    break
video_data.release()
print('Frames Read:',len(video_data_array))


# FPS: 29.97002997002997
# Dimensions: 1920 1080
# VideoFrame: 494
# Frames Read: 494

with mp_pose.Pose(
  static_image_mode=False,
  model_complexity=2,
  enable_segmentation=True,
  min_detection_confidence=0.5) as pose:

  #動画データをループ処理
  for loop_counter,image_data in enumerate(video_data_array):

    #画像解析
    results = pose.process(cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB))
    if not results.pose_landmarks:
      continue

    for i, lm in enumerate(results.pose_landmarks.landmark):
        print(f"Frame {loop_counter}, Joint {i}: x={lm.x:.4f}, y={lm.y:.4f}, z={lm.z:.4f}, visibility={lm.visibility:.4f}")
        csv_writer.writerow([loop_counter, i, lm.x, lm.y, lm.z, lm.visibility])

    #解析結果を動画に描画
    mp_drawing.draw_landmarks(
        image_data,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

plt.imshow(cv2.cvtColor(video_data_array[0], cv2.COLOR_BGR2RGB))
plt.tight_layout()

output_filename = 'output_movie.mp4'
#出力形式を指定する
output_file = cv2.VideoWriter(output_filename,cv2.VideoWriter_fourcc(*'MP4V'),video_fps,(video_width,video_hight))
#動画出力処理
for video_data in video_data_array:
  output_file.write(video_data)

output_file.release()





csv_file.close()