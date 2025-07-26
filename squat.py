

# import cv2
# import csv
# import time
# import mediapipe as mp
# from mediapipe.framework.formats import landmark_pb2

# # === ステップ②：お手本動画そのものを流す ===
# example_video = cv2.VideoCapture('movie/squat.mp4')
# cv2.namedWindow('Pose Comparison', cv2.WND_PROP_FULLSCREEN)
# cv2.setWindowProperty('Pose Comparison', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# while example_video.isOpened():
#     ret, frame = example_video.read()
#     if not ret:
#         break
#     frame = cv2.resize(frame, (1280, 720))
#     cv2.imshow('Pose Comparison', frame)
#     if cv2.waitKey(30) & 0xFF == ord('q'):
#         break

# example_video.release()
# cv2.destroyAllWindows()

# # === 以下は既存コード ===

# mp_pose = mp.solutions.pose
# POSE_CONNECTIONS = mp_pose.POSE_CONNECTIONS

# # 蛍光色系に変えて、より目立つカラーにしたよ
# LANDMARK_COLORS = [
#     (0, 255, 255),  # シアン
#     (0, 255, 0),    # ネオングリーン
#     (255, 0, 255),  # マゼンタ
#     (255, 255, 0),  # イエロー
#     (255, 105, 180),# ホットピンク
#     (0, 255, 127),  # スプリンググリーン
#     (255, 69, 0),   # オレンジレッド
#     (0, 191, 255),  # ディープスカイブルー
#     (255, 20, 147), # ディープピンク
#     (124, 252, 0),  # ローングリーン
#     (30, 144, 255), # ドッジブルー
#     (50, 205, 50),  # ライムグリーン
#     (255, 0, 0),    # レッド
#     (0, 0, 255),    # ブルー
#     (255, 165, 0),  # オレンジ
#     (0, 255, 255),  # アクア
#     (255, 255, 255) # ホワイト
# ] * 2

# landmark_dict = {}
# with open('landmarks_output_squat.csv', newline='') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         frame = int(row['frame'])
#         if frame not in landmark_dict:
#             landmark_dict[frame] = []
#         landmark = landmark_pb2.NormalizedLandmark(
#             x=float(row['x']),
#             y=float(row['y']),
#             z=float(row['z']),
#             visibility=float(row['visibility'])
#         )
#         landmark_dict[frame].append(landmark)

# # === グローバル変数 ===
# initial_offset_x = 0
# initial_offset_y = 0
# scale_factor = 1.0
# offset_initialized = False
# calibration_done = False

# cap = cv2.VideoCapture(0)
# frame_counter = 0

# cv2.namedWindow('Pose Comparison', cv2.WND_PROP_FULLSCREEN)
# cv2.setWindowProperty('Pose Comparison', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# mode = 'waiting'
# countdown_start_time = None

# user_csv = open('landmarks_user_squat.csv', 'w', newline='')
# user_writer = csv.writer(user_csv)
# user_writer.writerow(['frame', 'id', 'x', 'y', 'z', 'visibility'])

# with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         frame = cv2.flip(frame, 1)
#         image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = pose.process(image_rgb)

#         h, w, _ = frame.shape

#         # === ジェスチャー検出 ===
#         if mode == 'waiting' and results.pose_landmarks:
#             lms = results.pose_landmarks.landmark
#             lw_y = lms[mp_pose.PoseLandmark.LEFT_WRIST].y
#             rw_y = lms[mp_pose.PoseLandmark.RIGHT_WRIST].y
#             ls_y = lms[mp_pose.PoseLandmark.LEFT_SHOULDER].y
#             rs_y = lms[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
#             if lw_y < ls_y and rw_y < rs_y:
#                 mode = 'countdown'
#                 countdown_start_time = time.time()

#         if mode == 'countdown':
#             elapsed = time.time() - countdown_start_time
#             remaining = 3 - int(elapsed)
#             if remaining > 0:
#                 cv2.putText(frame, str(remaining), (300, 200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 7)
#             else:
#                 if not calibration_done and results.pose_landmarks:
#                     user_lms = results.pose_landmarks.landmark
#                     user_shoulder_y = (user_lms[11].y + user_lms[12].y) / 2
#                     user_hip_y = (user_lms[23].y + user_lms[24].y) / 2
#                     user_len = abs(user_shoulder_y - user_hip_y)
#                     user_center_x = (user_lms[23].x + user_lms[24].x) / 2
#                     user_center_y = (user_lms[23].y + user_lms[24].y) / 2
#                     ex_lms = landmark_dict[0]
#                     ex_shoulder_y = (ex_lms[11].y + ex_lms[12].y) / 2
#                     ex_hip_y = (ex_lms[23].y + ex_lms[24].y) / 2
#                     ex_len = abs(ex_shoulder_y - ex_hip_y)
#                     ex_center_x = (ex_lms[23].x + ex_lms[24].x) / 2
#                     ex_center_y = (ex_lms[23].y + ex_lms[24].y) / 2
#                     scale_factor = user_len / ex_len if ex_len > 0 else 1.0
#                     initial_offset_x = user_center_x - ex_center_x
#                     initial_offset_y = user_center_y - ex_center_y
#                     calibration_done = True
#                 mode = 'running'
#                 frame_counter = 0

#         if mode == 'running' and frame_counter in landmark_dict and calibration_done:
#             overlay = frame.copy()
#             landmarks = landmark_dict[frame_counter]
#             cx = (landmarks[23].x + landmarks[24].x) / 2
#             cy = (landmarks[23].y + landmarks[24].y) / 2
#             cz = (landmarks[23].z + landmarks[24].z) / 2
#             SCALE = 1.3
#             OFFSET_Y = -0.05
#             example_landmarks = []
#             for lm in landmarks:
#                 new_lm = landmark_pb2.NormalizedLandmark()
#                 new_lm.x = min(max(cx + (lm.x - cx) * SCALE * scale_factor + initial_offset_x, 0.0), 1.0)
#                 new_lm.y = min(max(cy + (lm.y - cy) * SCALE * scale_factor + OFFSET_Y + initial_offset_y, 0.0), 1.0)
#                 new_lm.z = (lm.z - cz) * SCALE * scale_factor + cz
#                 new_lm.visibility = lm.visibility
#                 example_landmarks.append(new_lm)
#             for i, lm in enumerate(example_landmarks):
#                 if (1 <= i <= 10) or (17 <= i <= 22) or (29 <= i <= 32):
#                     continue
#                 px, py = int(lm.x * w), int(lm.y * h)
#                 color = LANDMARK_COLORS[i]
#                 cv2.circle(frame, (px, py), 8, color, -1)
#             for a, b in POSE_CONNECTIONS:
#                 if a < len(example_landmarks) and b < len(example_landmarks):
#                     if (a != 0 and a < 11) or (b != 0 and b < 11):
#                         continue
#                     xa, ya = int(example_landmarks[a].x * w), int(example_landmarks[a].y * h)
#                     xb, yb = int(example_landmarks[b].x * w), int(example_landmarks[b].y * h)
#                     color = LANDMARK_COLORS[a]
#                     cv2.line(frame, (xa, ya), (xb, yb), color, 4)

#         if results.pose_landmarks:
#             user_lms = results.pose_landmarks.landmark
#             if mode == 'running' and frame_counter in landmark_dict:
#                 for i, lm in enumerate(user_lms):
#                     if (1 <= i <= 10) or (17 <= i <= 22) or (29 <= i <= 32):
#                         continue
#                     user_writer.writerow([frame_counter, i, lm.x, lm.y, lm.z, lm.visibility])

#         screen_rect = cv2.getWindowImageRect('Pose Comparison')
#         screen_width = screen_rect[2]
#         screen_height = screen_rect[3]
#         frame_aspect = frame.shape[1] / frame.shape[0]
#         screen_aspect = screen_width / screen_height
#         if screen_aspect > frame_aspect:
#             new_height = screen_height
#             new_width = int(frame_aspect * new_height)
#         else:
#             new_width = screen_width
#             new_height = int(new_width / frame_aspect)
#         resized_frame = cv2.resize(frame, (new_width, new_height))
#         cv2.imshow('Pose Comparison', resized_frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#         if mode == 'running':
#             frame_counter += 1

# cap.release()
# user_csv.close()
# cv2.destroyAllWindows()



# import cv2
# import csv
# import time
# import mediapipe as mp
# from collections import defaultdict
# from mediapipe.framework.formats import landmark_pb2

# # === 腰が一番低いフレームを抽出 ===
# landmark_y = defaultdict(list)

# with open('landmarks_output_squat.csv', newline='') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         frame = int(row['frame'])
#         id = int(row['joint'])
#         if id == 23 or id == 24:
#             y = float(row['y'])
#             landmark_y[frame].append(y)

# min_y_frame = None
# min_y_value = -1

# for frame, y_list in landmark_y.items():
#     if len(y_list) == 2:
#         avg_y = sum(y_list) / 2
#         if avg_y > min_y_value:
#             min_y_value = avg_y
#             min_y_frame = frame

# # === お手本動画の再生 ===
# example_video = cv2.VideoCapture('movie/squat.mp4')
# cv2.namedWindow('Pose Comparison', cv2.WND_PROP_FULLSCREEN)
# cv2.setWindowProperty('Pose Comparison', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# while example_video.isOpened():
#     ret, frame = example_video.read()
#     if not ret:
#         break
#     frame = cv2.resize(frame, (1280, 720))
#     cv2.imshow('Pose Comparison', frame)
#     if cv2.waitKey(30) & 0xFF == ord('q'):
#         break

# example_video.release()
# cv2.destroyAllWindows()

# # === ここからPose処理 ===
# mp_pose = mp.solutions.pose
# POSE_CONNECTIONS = mp_pose.POSE_CONNECTIONS

# LANDMARK_COLORS = [
#     (0, 255, 255), (0, 255, 0), (255, 0, 255), (255, 255, 0), (255, 105, 180),
#     (0, 255, 127), (255, 69, 0), (0, 191, 255), (255, 20, 147), (124, 252, 0),
#     (30, 144, 255), (50, 205, 50), (255, 0, 0), (0, 0, 255), (255, 165, 0),
#     (0, 255, 255), (255, 255, 255)
# ] * 2

# landmark_dict = {}
# with open('landmarks_output_squat.csv', newline='') as csvfile:
#     reader = csv.DictReader(csvfile)
#     for row in reader:
#         frame = int(row['frame'])
#         if frame not in landmark_dict:
#             landmark_dict[frame] = []
#         landmark = landmark_pb2.NormalizedLandmark(
#             x=float(row['x']), y=float(row['y']), z=float(row['z']), visibility=float(row['visibility'])
#         )
#         landmark_dict[frame].append(landmark)

# initial_offset_x = 0
# initial_offset_y = 0
# scale_factor = 1.0
# calibration_done = False
# second_waiting = False
# show_fixed_example = False

# cap = cv2.VideoCapture(0)
# frame_counter = 0

# cv2.namedWindow('Pose Comparison', cv2.WND_PROP_FULLSCREEN)
# cv2.setWindowProperty('Pose Comparison', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# mode = 'waiting'
# countdown_start_time = None

# user_csv = open('landmarks_user_squat.csv', 'w', newline='')
# user_writer = csv.writer(user_csv)
# user_writer.writerow(['frame', 'id', 'x', 'y', 'z', 'visibility'])

# with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
#         frame = cv2.flip(frame, 1)
#         image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = pose.process(image_rgb)

#         h, w, _ = frame.shape

#         if mode == 'waiting' and results.pose_landmarks:
#             lms = results.pose_landmarks.landmark
#             lw_y = lms[mp_pose.PoseLandmark.LEFT_WRIST].y
#             rw_y = lms[mp_pose.PoseLandmark.RIGHT_WRIST].y
#             ls_y = lms[mp_pose.PoseLandmark.LEFT_SHOULDER].y
#             rs_y = lms[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
#             if lw_y < ls_y and rw_y < rs_y:
#                 mode = 'countdown'
#                 countdown_start_time = time.time()

#         if mode == 'countdown':
#             elapsed = time.time() - countdown_start_time
#             remaining = 3 - int(elapsed)
#             if remaining > 0:
#                 cv2.putText(frame, str(remaining), (300, 200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 7)
#             else:
#                 if not calibration_done and results.pose_landmarks:
#                     user_lms = results.pose_landmarks.landmark
#                     user_shoulder_y = (user_lms[11].y + user_lms[12].y) / 2
#                     user_hip_y = (user_lms[23].y + user_lms[24].y) / 2
#                     user_len = abs(user_shoulder_y - user_hip_y)
#                     user_center_x = (user_lms[23].x + user_lms[24].x) / 2
#                     user_center_y = (user_lms[23].y + user_lms[24].y) / 2
#                     ex_lms = landmark_dict[0]
#                     ex_shoulder_y = (ex_lms[11].y + ex_lms[12].y) / 2
#                     ex_hip_y = (ex_lms[23].y + ex_lms[24].y) / 2
#                     ex_len = abs(ex_shoulder_y - ex_hip_y)
#                     ex_center_x = (ex_lms[23].x + ex_lms[24].x) / 2
#                     ex_center_y = (ex_lms[23].y + ex_lms[24].y) / 2
#                     scale_factor = user_len / ex_len if ex_len > 0 else 1.0
#                     initial_offset_x = user_center_x - ex_center_x
#                     initial_offset_y = user_center_y - ex_center_y
#                     calibration_done = True
#                 mode = 'running'
#                 frame_counter = 0

#         if mode == 'running' and frame_counter in landmark_dict and calibration_done:
#             landmarks = landmark_dict[frame_counter]
#             cx = (landmarks[23].x + landmarks[24].x) / 2
#             cy = (landmarks[23].y + landmarks[24].y) / 2
#             cz = (landmarks[23].z + landmarks[24].z) / 2
#             SCALE = 1.3
#             OFFSET_Y = -0.05
#             example_landmarks = []
#             for lm in landmarks:
#                 new_lm = landmark_pb2.NormalizedLandmark()
#                 new_lm.x = min(max(cx + (lm.x - cx) * SCALE * scale_factor + initial_offset_x, 0.0), 1.0)
#                 new_lm.y = min(max(cy + (lm.y - cy) * SCALE * scale_factor + OFFSET_Y + initial_offset_y, 0.0), 1.0)
#                 new_lm.z = (lm.z - cz) * SCALE * scale_factor + cz
#                 new_lm.visibility = lm.visibility
#                 example_landmarks.append(new_lm)
#             for i, lm in enumerate(example_landmarks):
#                 if (1 <= i <= 10) or (17 <= i <= 22) or (29 <= i <= 32): continue
#                 px, py = int(lm.x * w), int(lm.y * h)
#                 color = LANDMARK_COLORS[i]
#                 cv2.circle(frame, (px, py), 8, color, -1)
#             for a, b in POSE_CONNECTIONS:
#                 if a < len(example_landmarks) and b < len(example_landmarks):
#                     if (a != 0 and a < 11) or (b != 0 and b < 11): continue
#                     xa, ya = int(example_landmarks[a].x * w), int(example_landmarks[a].y * h)
#                     xb, yb = int(example_landmarks[b].x * w), int(example_landmarks[b].y * h)
#                     color = LANDMARK_COLORS[a]
#                     cv2.line(frame, (xa, ya), (xb, yb), color, 4)

#             if frame_counter >= max(landmark_dict.keys()):
#                 mode = 'fixed'

#         elif mode == 'fixed' and min_y_frame in landmark_dict:
#             landmarks = landmark_dict[min_y_frame]
#             cx = (landmarks[23].x + landmarks[24].x) / 2
#             cy = (landmarks[23].y + landmarks[24].y) / 2
#             cz = (landmarks[23].z + landmarks[24].z) / 2
#             SCALE = 1.3
#             OFFSET_Y = -0.05
#             example_landmarks = []
#             for lm in landmarks:
#                 new_lm = landmark_pb2.NormalizedLandmark()
#                 new_lm.x = min(max(cx + (lm.x - cx) * SCALE * scale_factor + initial_offset_x, 0.0), 1.0)
#                 new_lm.y = min(max(cy + (lm.y - cy) * SCALE * scale_factor + OFFSET_Y + initial_offset_y, 0.0), 1.0)
#                 new_lm.z = (lm.z - cz) * SCALE * scale_factor + cz
#                 new_lm.visibility = lm.visibility
#                 example_landmarks.append(new_lm)
#             for i, lm in enumerate(example_landmarks):
#                 if (1 <= i <= 10) or (17 <= i <= 22) or (29 <= i <= 32): continue
#                 px, py = int(lm.x * w), int(lm.y * h)
#                 color = LANDMARK_COLORS[i]
#                 cv2.circle(frame, (px, py), 8, color, -1)
#             for a, b in POSE_CONNECTIONS:
#                 if a < len(example_landmarks) and b < len(example_landmarks):
#                     if (a != 0 and a < 11) or (b != 0 and b < 11): continue
#                     xa, ya = int(example_landmarks[a].x * w), int(example_landmarks[a].y * h)
#                     xb, yb = int(example_landmarks[b].x * w), int(example_landmarks[b].y * h)
#                     color = LANDMARK_COLORS[a]
#                     cv2.line(frame, (xa, ya), (xb, yb), color, 4)

#         screen_rect = cv2.getWindowImageRect('Pose Comparison')
#         screen_width = screen_rect[2]
#         screen_height = screen_rect[3]
#         frame_aspect = frame.shape[1] / frame.shape[0]
#         screen_aspect = screen_width / screen_height
#         if screen_aspect > frame_aspect:
#             new_height = screen_height
#             new_width = int(frame_aspect * new_height)
#         else:
#             new_width = screen_width
#             new_height = int(new_width / frame_aspect)
#         resized_frame = cv2.resize(frame, (new_width, new_height))
#         cv2.imshow('Pose Comparison', resized_frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#         if mode == 'running':
#             frame_counter += 1

# cap.release()
# user_csv.close()
# cv2.destroyAllWindows()


import cv2
import csv
import time
import mediapipe as mp
from collections import defaultdict
from mediapipe.framework.formats import landmark_pb2

# === 腰が一番低いフレームを抽出 ===
landmark_y = defaultdict(list)

with open('landmarks_output_squat.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        frame = int(row['frame'])
        id = int(row['joint'])
        if id == 23 or id == 24:
            y = float(row['y'])
            landmark_y[frame].append(y)

min_y_frame = None
min_y_value = -1

for frame, y_list in landmark_y.items():
    if len(y_list) == 2:
        avg_y = sum(y_list) / 2
        if avg_y > min_y_value:
            min_y_value = avg_y
            min_y_frame = frame

# === お手本動画の再生 ===
example_video = cv2.VideoCapture('movie/squat.mp4')
cv2.namedWindow('Pose Comparison', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('Pose Comparison', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while example_video.isOpened():
    ret, frame = example_video.read()
    if not ret:
        break
    frame = cv2.resize(frame, (1280, 720))
    cv2.imshow('Pose Comparison', frame)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

example_video.release()
cv2.destroyAllWindows()

# === ここからPose処理 ===
mp_pose = mp.solutions.pose
POSE_CONNECTIONS = mp_pose.POSE_CONNECTIONS

LANDMARK_COLORS = [
    (0, 255, 255), (0, 255, 0), (255, 0, 255), (255, 255, 0), (255, 105, 180),
    (0, 255, 127), (255, 69, 0), (0, 191, 255), (255, 20, 147), (124, 252, 0),
    (30, 144, 255), (50, 205, 50), (255, 0, 0), (0, 0, 255), (255, 165, 0),
    (0, 255, 255), (255, 255, 255)
] * 2

landmark_dict = {}
with open('landmarks_output_squat.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        frame = int(row['frame'])
        if frame not in landmark_dict:
            landmark_dict[frame] = []
        landmark = landmark_pb2.NormalizedLandmark(
            x=float(row['x']), y=float(row['y']), z=float(row['z']), visibility=float(row['visibility'])
        )
        landmark_dict[frame].append(landmark)

initial_offset_x = 0
initial_offset_y = 0
scale_factor = 1.0
calibration_done = False
second_waiting = False
show_fixed_example = False

# === 終了ポーズ検出用 ===
end_gesture_start_time = None
END_HOLD_DURATION = 2  # 秒

cap = cv2.VideoCapture(0)
frame_counter = 0

cv2.namedWindow('Pose Comparison', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('Pose Comparison', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

mode = 'waiting'
countdown_start_time = None

user_csv = open('landmarks_user_squat.csv', 'w', newline='')
user_writer = csv.writer(user_csv)
user_writer.writerow(['frame', 'id', 'x', 'y', 'z', 'visibility'])

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        h, w, _ = frame.shape

        if mode == 'waiting' and results.pose_landmarks:
            lms = results.pose_landmarks.landmark
            lw_y = lms[mp_pose.PoseLandmark.LEFT_WRIST].y
            rw_y = lms[mp_pose.PoseLandmark.RIGHT_WRIST].y
            ls_y = lms[mp_pose.PoseLandmark.LEFT_SHOULDER].y
            rs_y = lms[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
            if lw_y < ls_y and rw_y < rs_y:
                mode = 'countdown'
                countdown_start_time = time.time()

        if mode == 'countdown':
            elapsed = time.time() - countdown_start_time
            remaining = 3 - int(elapsed)
            if remaining > 0:
                cv2.putText(frame, str(remaining), (300, 200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 7)
            else:
                if not calibration_done and results.pose_landmarks:
                    user_lms = results.pose_landmarks.landmark
                    user_shoulder_y = (user_lms[11].y + user_lms[12].y) / 2
                    user_hip_y = (user_lms[23].y + user_lms[24].y) / 2
                    user_len = abs(user_shoulder_y - user_hip_y)
                    user_center_x = (user_lms[23].x + user_lms[24].x) / 2
                    user_center_y = (user_lms[23].y + user_lms[24].y) / 2
                    ex_lms = landmark_dict[0]
                    ex_shoulder_y = (ex_lms[11].y + ex_lms[12].y) / 2
                    ex_hip_y = (ex_lms[23].y + ex_lms[24].y) / 2
                    ex_len = abs(ex_shoulder_y - ex_hip_y)
                    ex_center_x = (ex_lms[23].x + ex_lms[24].x) / 2
                    ex_center_y = (ex_lms[23].y + ex_lms[24].y) / 2
                    scale_factor = user_len / ex_len if ex_len > 0 else 1.0
                    initial_offset_x = user_center_x - ex_center_x
                    initial_offset_y = user_center_y - ex_center_y
                    calibration_done = True
                mode = 'running'
                frame_counter = 0

        if mode == 'running' and frame_counter in landmark_dict and calibration_done:
            landmarks = landmark_dict[frame_counter]
            cx = (landmarks[23].x + landmarks[24].x) / 2
            cy = (landmarks[23].y + landmarks[24].y) / 2
            cz = (landmarks[23].z + landmarks[24].z) / 2
            SCALE = 1.3
            OFFSET_Y = -0.05
            example_landmarks = []
            for lm in landmarks:
                new_lm = landmark_pb2.NormalizedLandmark()
                new_lm.x = min(max(cx + (lm.x - cx) * SCALE * scale_factor + initial_offset_x, 0.0), 1.0)
                new_lm.y = min(max(cy + (lm.y - cy) * SCALE * scale_factor + OFFSET_Y + initial_offset_y, 0.0), 1.0)
                new_lm.z = (lm.z - cz) * SCALE * scale_factor + cz
                new_lm.visibility = lm.visibility
                example_landmarks.append(new_lm)
            for i, lm in enumerate(example_landmarks):
                if (1 <= i <= 10) or (17 <= i <= 22) or (29 <= i <= 32): continue
                px, py = int(lm.x * w), int(lm.y * h)
                color = LANDMARK_COLORS[i]
                cv2.circle(frame, (px, py), 8, color, -1)
            for a, b in POSE_CONNECTIONS:
                if a < len(example_landmarks) and b < len(example_landmarks):
                    if (a != 0 and a < 11) or (b != 0 and b < 11): continue
                    xa, ya = int(example_landmarks[a].x * w), int(example_landmarks[a].y * h)
                    xb, yb = int(example_landmarks[b].x * w), int(example_landmarks[b].y * h)
                    color = LANDMARK_COLORS[a]
                    cv2.line(frame, (xa, ya), (xb, yb), color, 4)

            if frame_counter >= max(landmark_dict.keys()):
                mode = 'fixed'

        elif mode == 'fixed' and min_y_frame in landmark_dict:
            landmarks = landmark_dict[min_y_frame]
            cx = (landmarks[23].x + landmarks[24].x) / 2
            cy = (landmarks[23].y + landmarks[24].y) / 2
            cz = (landmarks[23].z + landmarks[24].z) / 2
            SCALE = 1.3
            OFFSET_Y = -0.05
            example_landmarks = []
            for lm in landmarks:
                new_lm = landmark_pb2.NormalizedLandmark()
                new_lm.x = min(max(cx + (lm.x - cx) * SCALE * scale_factor + initial_offset_x, 0.0), 1.0)
                new_lm.y = min(max(cy + (lm.y - cy) * SCALE * scale_factor + OFFSET_Y + initial_offset_y, 0.0), 1.0)
                new_lm.z = (lm.z - cz) * SCALE * scale_factor + cz
                new_lm.visibility = lm.visibility
                example_landmarks.append(new_lm)
            for i, lm in enumerate(example_landmarks):
                if (1 <= i <= 10) or (17 <= i <= 22) or (29 <= i <= 32): continue
                px, py = int(lm.x * w), int(lm.y * h)
                color = LANDMARK_COLORS[i]
                cv2.circle(frame, (px, py), 8, color, -1)
            for a, b in POSE_CONNECTIONS:
                if a < len(example_landmarks) and b < len(example_landmarks):
                    if (a != 0 and a < 11) or (b != 0 and b < 11): continue
                    xa, ya = int(example_landmarks[a].x * w), int(example_landmarks[a].y * h)
                    xb, yb = int(example_landmarks[b].x * w), int(example_landmarks[b].y * h)
                    color = LANDMARK_COLORS[a]
                    cv2.line(frame, (xa, ya), (xb, yb), color, 4)

            # === 終了ポーズ判定 ===
            if results.pose_landmarks:
                lms = results.pose_landmarks.landmark
                lw = lms[mp_pose.PoseLandmark.LEFT_WRIST]
                rw = lms[mp_pose.PoseLandmark.RIGHT_WRIST]
                nose = lms[mp_pose.PoseLandmark.NOSE]
                le = lms[mp_pose.PoseLandmark.LEFT_ELBOW]
                re = lms[mp_pose.PoseLandmark.RIGHT_ELBOW]

                wrists_above_head = lw.y < nose.y and rw.y < nose.y
                wrists_close = abs(lw.x - rw.x) < 0.1
                elbows_below_wrists = le.y > lw.y and re.y > rw.y

                if wrists_above_head and wrists_close and elbows_below_wrists:
                    if end_gesture_start_time is None:
                        end_gesture_start_time = time.time()
                    elif time.time() - end_gesture_start_time > END_HOLD_DURATION:
                        mode = 'end'
                else:
                    end_gesture_start_time = None

        elif mode == 'end':
            cv2.putText(frame, 'Training Finished!', (200, 400), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 5)
            cv2.imshow('Pose Comparison', frame)
            cv2.waitKey(3000)
            break

        screen_rect = cv2.getWindowImageRect('Pose Comparison')
        screen_width = screen_rect[2]
        screen_height = screen_rect[3]
        frame_aspect = frame.shape[1] / frame.shape[0]
        screen_aspect = screen_width / screen_height
        if screen_aspect > frame_aspect:
            new_height = screen_height
            new_width = int(frame_aspect * new_height)
        else:
            new_width = screen_width
            new_height = int(new_width / frame_aspect)
        resized_frame = cv2.resize(frame, (new_width, new_height))
        cv2.imshow('Pose Comparison', resized_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if mode == 'running':
            frame_counter += 1

cap.release()
user_csv.close()
cv2.destroyAllWindows()
