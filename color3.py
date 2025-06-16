import cv2
import csv
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2

mp_pose = mp.solutions.pose
POSE_CONNECTIONS = mp_pose.POSE_CONNECTIONS

# 💡 関節ごとの色（33点×2倍）
LANDMARK_COLORS = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255),
    (0, 255, 255), (128, 0, 128), (0, 128, 128), (255, 165, 0),
    (173, 216, 230), (220, 20, 60), (255, 20, 147), (0, 100, 0),
    (139, 0, 0), (72, 61, 139), (0, 0, 0), (255, 255, 255)
] * 2  # 33点ぶん

# === お手本のランドマークCSV読み込み ===
landmark_dict = {}
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

# === WebカメラとPose初期化 ===
cap = cv2.VideoCapture(0)
frame_counter = 0

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        h, w, _ = frame.shape

        # === お手本ランドマーク表示 ===
        if frame_counter in landmark_dict:
            landmarks = landmark_dict[frame_counter]

            # 中心（腰）を基準にスケーリング
            if len(landmarks) > 24:
                cx = (landmarks[23].x + landmarks[24].x) / 2
                cy = (landmarks[23].y + landmarks[24].y) / 2
                cz = (landmarks[23].z + landmarks[24].z) / 2
            else:
                cx, cy, cz = 0.5, 0.5, 0.0

            SCALE = 1.5
            OFFSET_Y = 0.1
            example_landmarks = []
            for lm in landmarks:
                new_lm = landmark_pb2.NormalizedLandmark()
                new_lm.x = min(max(cx + (lm.x - cx) * SCALE, 0.0), 1.0)
                new_lm.y = min(max(cy + (lm.y - cy) * SCALE + OFFSET_Y, 0.0), 1.0)
                new_lm.z = (lm.z - cz) * SCALE + cz
                new_lm.visibility = lm.visibility
                example_landmarks.append(new_lm)

            # 🧍 お手本：点と線を描画（薄めの色）
            for i, lm in enumerate(example_landmarks):
                if i != 0 and i < 11:  # 顔（0以外）をスキップ
                    continue
                px, py = int(lm.x * w), int(lm.y * h)
                color = tuple(int(c * 0.5) for c in LANDMARK_COLORS[i])
                cv2.circle(frame, (px, py), 5, color, -1)

            for a, b in POSE_CONNECTIONS:
                if a < len(example_landmarks) and b < len(example_landmarks):
                    if (a != 0 and a < 11) or (b != 0 and b < 11):  # 顔除外（0番はOK）
                        continue
                    xa, ya = int(example_landmarks[a].x * w), int(example_landmarks[a].y * h)
                    xb, yb = int(example_landmarks[b].x * w), int(example_landmarks[b].y * h)
                    color = tuple(int(c * 0.5) for c in LANDMARK_COLORS[a])
                    cv2.line(frame, (xa, ya), (xb, yb), color, 2)

        # 🧍‍♀️ ユーザーランドマーク描画（濃い色）
        if results.pose_landmarks:
            user_lms = results.pose_landmarks.landmark
            for i, lm in enumerate(user_lms):
                if i != 0 and i < 11:
                    continue
                ux, uy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (ux, uy), 5, LANDMARK_COLORS[i], -1)

            for a, b in POSE_CONNECTIONS:
                if a < len(user_lms) and b < len(user_lms):
                    if (a != 0 and a < 11) or (b != 0 and b < 11):
                        continue
                    xa, ya = int(user_lms[a].x * w), int(user_lms[a].y * h)
                    xb, yb = int(user_lms[b].x * w), int(user_lms[b].y * h)
                    cv2.line(frame, (xa, ya), (xb, yb), LANDMARK_COLORS[a], 2)

        cv2.imshow('Pose Comparison', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame_counter += 1

cap.release()
cv2.destroyAllWindows()
