# お手本と自分同時に移せた
# コードの意味理解する
# 位置調整できないか試す
# 自分が左右反転？

import cv2
import csv
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2

# mediapipe初期化
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# === お手本のランドマークをCSVから読み込み ===
landmark_dict = {}  # frame番号 -> list of landmarks

with open('landmarks_output.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        frame = int(row['frame'])
        if frame not in landmark_dict:
            landmark_dict[frame] = []
        landmark = landmark_pb2.NormalizedLandmark(
            x=float(row['x']),
            y=float(row['y']),
            z=float(row['z']),
            visibility=float(row['visibility'])
        )
        landmark_dict[frame].append(landmark)

# === WebカメラとMediapipe Pose 初期化 ===
cap = cv2.VideoCapture(0)
frame_counter = 0

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # ✅ 左右反転（ミラー表示）
        frame = cv2.flip(frame, 1)

        # ユーザーの姿勢推定
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        # お手本ランドマーク描画（frame_counterに対応するフレーム）
        if frame_counter in landmark_dict:
            OFFSET_Y = 0.1  # 画面下に10%ずらす（必要に応じて調整）
            example_landmarks_offset = []
            for lm in landmark_dict[frame_counter]:
                new_lm = landmark_pb2.NormalizedLandmark()
                new_lm.x = lm.x
                new_lm.y = min(lm.y + OFFSET_Y, 1.0)  # 下にずらす（1.0を超えないように）
                new_lm.z = lm.z
                new_lm.visibility = lm.visibility
                example_landmarks_offset.append(new_lm)

            example_landmarks = landmark_pb2.NormalizedLandmarkList(landmark=example_landmarks_offset)

            mp_drawing.draw_landmarks(
                frame,
                example_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2)  # 緑：お手本
            )

        # ユーザーのランドマーク描画（白）
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2)
            )

        cv2.imshow('Pose Comparison', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        frame_counter += 1

cap.release()
cv2.destroyAllWindows()
