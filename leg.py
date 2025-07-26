# import cv2
# import csv
# import time
# import mediapipe as mp
# from mediapipe.framework.formats import landmark_pb2

# mp_pose = mp.solutions.pose
# POSE_CONNECTIONS = mp_pose.POSE_CONNECTIONS

# # 角度計算
# import math

# def calculate_angle(a, b, c):
#     """3点（a, b, c）からなる角度（bを中心）を計算して度数で返す"""
#     ba = [a.x - b.x, a.y - b.y]
#     bc = [c.x - b.x, c.y - b.y]
#     dot_product = ba[0]*bc[0] + ba[1]*bc[1]
#     norm_ba = math.sqrt(ba[0]**2 + ba[1]**2)
#     norm_bc = math.sqrt(bc[0]**2 + bc[1]**2)
#     if norm_ba * norm_bc == 0:
#         return None
#     cos_angle = dot_product / (norm_ba * norm_bc)
#     angle = math.acos(min(1.0, max(-1.0, cos_angle)))
#     return math.degrees(angle)


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
# with open('landmarks_output_leg.csv', newline='') as csvfile:
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

# cap = cv2.VideoCapture(0)
# frame_counter = 0

# cv2.namedWindow('Pose Comparison', cv2.WND_PROP_FULLSCREEN)
# cv2.setWindowProperty('Pose Comparison', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


# # === 状態管理 ===
# mode = 'waiting'
# countdown_start_time = None

# # === ユーザー動作保存用CSVの準備 ===
# user_csv = open('landmarks_user_leg.csv', 'w', newline='')
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

#         # === ジェスチャー検出（両手を上げたらスタート）===
#         if mode == 'waiting' and results.pose_landmarks:
#             lms = results.pose_landmarks.landmark
#             lw_y = lms[mp_pose.PoseLandmark.LEFT_WRIST].y
#             rw_y = lms[mp_pose.PoseLandmark.RIGHT_WRIST].y
#             ls_y = lms[mp_pose.PoseLandmark.LEFT_SHOULDER].y
#             rs_y = lms[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
#             if lw_y < ls_y and rw_y < rs_y:
#                 mode = 'countdown'
#                 countdown_start_time = time.time()

#         # === カウントダウン処理 ===
#         if mode == 'countdown':
#             elapsed = time.time() - countdown_start_time
#             remaining = 3 - int(elapsed)
#             if remaining > 0:
#                 cv2.putText(frame, str(remaining), (300, 200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 7)
#             else:
#                 mode = 'running'
#                 frame_counter = 0

#         # === お手本表示（本番） ===
#         if mode == 'running' and frame_counter in landmark_dict:
#             overlay = frame.copy()  # ← 半透明描画用レイヤー
#             landmarks = landmark_dict[frame_counter]
#             if len(landmarks) > 24:
#                 cx = (landmarks[23].x + landmarks[24].x) / 2
#                 cy = (landmarks[23].y + landmarks[24].y) / 2
#                 cz = (landmarks[23].z + landmarks[24].z) / 2
#             else:
#                 cx, cy, cz = 0.5, 0.5, 0.0

#             SCALE = 1.3
#             OFFSET_Y = 0.1
#             example_landmarks = []
#             for lm in landmarks:
#                 new_lm = landmark_pb2.NormalizedLandmark()
#                 new_lm.x = min(max(cx + (lm.x - cx) * SCALE, 0.0), 1.0)
#                 new_lm.y = min(max(cy + (lm.y - cy) * SCALE + OFFSET_Y, 0.0), 1.0)
#                 new_lm.z = (lm.z - cz) * SCALE + cz
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
#                     cv2.line(frame, (xa, ya), (xb, yb), color, 4)  # ← overlayに描画





#         # === ユーザーのランドマーク描画＋保存 ===
#         if results.pose_landmarks:
#             # ==== ユーザーとお手本の角度比較（左脚と右脚） ====
#             try:
#                 if frame_counter in landmark_dict and results.pose_landmarks:
#                     ex_lms = landmark_dict[frame_counter]
#                     user_lms = results.pose_landmarks.landmark

#                     if len(ex_lms) > 28 and len(user_lms) > 28:
#                         ex_left_angle = calculate_angle(ex_lms[23], ex_lms[25], ex_lms[27])
#                         user_left_angle = calculate_angle(user_lms[23], user_lms[25], user_lms[27])
#                         ex_right_angle = calculate_angle(ex_lms[24], ex_lms[26], ex_lms[28])
#                         user_right_angle = calculate_angle(user_lms[24], user_lms[26], user_lms[28])

#                         if ex_left_angle is not None and user_left_angle is not None:
#                             diff_left = abs(ex_left_angle - user_left_angle)
#                             cv2.putText(frame, f"Left Knee Diff: {diff_left:.1f} deg", (30, 50),
#                                         cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)

#                         if ex_right_angle is not None and user_right_angle is not None:
#                             diff_right = abs(ex_right_angle - user_right_angle)
#                             cv2.putText(frame, f"Right Knee Diff: {diff_right:.1f} deg", (30, 100),
#                                         cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
#             except Exception as e:
#                 print(f"[WARN] 角度比較エラー: {e}")
                

#             if frame_counter in landmark_dict and results.pose_landmarks:
#                 # お手本のランドマーク（CSV由来）
#                 ex_lms = landmark_dict[frame_counter]
#                 # ユーザーのランドマーク（MediaPipe）
#                 user_lms = results.pose_landmarks.landmark

#                 # 左脚の角度（23-25-27）※左腰―左膝―左足首
#                 ex_left_angle = calculate_angle(ex_lms[23], ex_lms[25], ex_lms[27])
#                 user_left_angle = calculate_angle(user_lms[23], user_lms[25], user_lms[27])

#                 # 右脚の角度（24-26-28）※右腰―右膝―右足首
#                 ex_right_angle = calculate_angle(ex_lms[24], ex_lms[26], ex_lms[28])
#                 user_right_angle = calculate_angle(user_lms[24], user_lms[26], user_lms[28])

#                 # 差分を表示（例：画面左上）
#                 if ex_left_angle and user_left_angle:
#                     diff_left = abs(ex_left_angle - user_left_angle)
#                     cv2.putText(frame, f"Left Knee Diff: {diff_left:.1f} deg", (30, 50),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)

#                 if ex_right_angle and user_right_angle:
#                     diff_right = abs(ex_right_angle - user_right_angle)
#                     cv2.putText(frame, f"Right Knee Diff: {diff_right:.1f} deg", (30, 100),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

#             user_lms = results.pose_landmarks.landmark
#             user_overlay = frame.copy()

#             for i, lm in enumerate(user_lms):
#                 if (1 <= i <= 10) or (17 <= i <= 22) or (29 <= i <= 32):
#                     continue
#                 ux, uy = int(lm.x * w), int(lm.y * h)
#                 cv2.circle(user_overlay, (ux, uy), 8, LANDMARK_COLORS[i], -1)

#             for a, b in POSE_CONNECTIONS:
#                 if a < len(user_lms) and b < len(user_lms):
#                     if (a != 0 and a < 11) or (b != 0 and b < 11):
#                         continue
#                     xa, ya = int(user_lms[a].x * w), int(user_lms[a].y * h)
#                     xb, yb = int(user_lms[b].x * w), int(user_lms[b].y * h)
#                     cv2.line(user_overlay, (xa, ya), (xb, yb), LANDMARK_COLORS[a], 4)

#             # ★ 半透明でframeに合成（alpha小さめで控えめに）
#             frame = cv2.addWeighted(user_overlay, 0.3, frame, 0.7, 0)


#             # === ランドマークをCSVに保存（modeがrunningのときのみ）===
#             if mode == 'running' and frame_counter in landmark_dict:
#                 for i, lm in enumerate(user_lms):
#                     if (1 <= i <= 10) or (17 <= i <= 22) or (29 <= i <= 32):
#                         continue
#                     user_writer.writerow([frame_counter, i, lm.x, lm.y, lm.z, lm.visibility])

#         # ==== 表示前にアスペクト比を維持してリサイズ ====
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
#             # お手本データが尽きたら止める（任意）
#             if frame_counter >= max(landmark_dict.keys()):
#                 mode = 'done'

# cap.release()
# user_csv.close()
# cv2.destroyAllWindows()





# 何か微妙に肩の位置が高い、、

import cv2
import csv
import time
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2

mp_pose = mp.solutions.pose
POSE_CONNECTIONS = mp_pose.POSE_CONNECTIONS

# 蛍光色系に変えて、より目立つカラーにしたよ
LANDMARK_COLORS = [
    (0, 255, 255),  # シアン
    (0, 255, 0),    # ネオングリーン
    (255, 0, 255),  # マゼンタ
    (255, 255, 0),  # イエロー
    (255, 105, 180),# ホットピンク
    (0, 255, 127),  # スプリンググリーン
    (255, 69, 0),   # オレンジレッド
    (0, 191, 255),  # ディープスカイブルー
    (255, 20, 147), # ディープピンク
    (124, 252, 0),  # ローングリーン
    (30, 144, 255), # ドッジブルー
    (50, 205, 50),  # ライムグリーン
    (255, 0, 0),    # レッド
    (0, 0, 255),    # ブルー
    (255, 165, 0),  # オレンジ
    (0, 255, 255),  # アクア
    (255, 255, 255) # ホワイト
] * 2


landmark_dict = {}
with open('landmarks_output_leg.csv', newline='') as csvfile:
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

# initial_offset_x = 0
# initial_offset_y = 0
# offset_initialized = False

# === グローバル変数 ===
initial_offset_x = 0
initial_offset_y = 0
scale_factor = 1.0
offset_initialized = False
calibration_done = False  # ← 追加

cap = cv2.VideoCapture(0)
frame_counter = 0

cv2.namedWindow('Pose Comparison', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('Pose Comparison', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


# === 状態管理 ===
mode = 'waiting'
countdown_start_time = None

# === ユーザー動作保存用CSVの準備 ===
user_csv = open('landmarks_user_leg.csv', 'w', newline='')
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

        # === ジェスチャー検出（両手を上げたらスタート）===
        if mode == 'waiting' and results.pose_landmarks:
            lms = results.pose_landmarks.landmark
            lw_y = lms[mp_pose.PoseLandmark.LEFT_WRIST].y
            rw_y = lms[mp_pose.PoseLandmark.RIGHT_WRIST].y
            ls_y = lms[mp_pose.PoseLandmark.LEFT_SHOULDER].y
            rs_y = lms[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
            if lw_y < ls_y and rw_y < rs_y:
                mode = 'countdown'
                countdown_start_time = time.time()

        # === カウントダウン処理 ===
        if mode == 'countdown':
            elapsed = time.time() - countdown_start_time
            remaining = 3 - int(elapsed)
            if remaining > 0:
                cv2.putText(frame, str(remaining), (300, 200), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 7)
            else:
                if not calibration_done and results.pose_landmarks:
                    user_lms = results.pose_landmarks.landmark

                    # ユーザーの肩と腰のY座標（Normalized）
                    user_shoulder_y = (user_lms[11].y + user_lms[12].y) / 2
                    user_hip_y = (user_lms[23].y + user_lms[24].y) / 2
                    user_len = abs(user_shoulder_y - user_hip_y)

                    user_center_x = (user_lms[23].x + user_lms[24].x) / 2
                    user_center_y = (user_lms[23].y + user_lms[24].y) / 2

                    # お手本の0フレームから肩と腰のY座標
                    ex_lms = landmark_dict[0]
                    ex_shoulder_y = (ex_lms[11].y + ex_lms[12].y) / 2
                    ex_hip_y = (ex_lms[23].y + ex_lms[24].y) / 2
                    ex_len = abs(ex_shoulder_y - ex_hip_y)

                    ex_center_x = (ex_lms[23].x + ex_lms[24].x) / 2
                    ex_center_y = (ex_lms[23].y + ex_lms[24].y) / 2

                    # 比率とオフセット計算（腰位置合わせ、スケーリング）
                    scale_factor = user_len / ex_len if ex_len > 0 else 1.0
                    initial_offset_x = user_center_x - ex_center_x
                    initial_offset_y = user_center_y - ex_center_y

                    calibration_done = True  # ← 初期キャリブレーション完了フラグ

                mode = 'running'
                frame_counter = 0


        # === お手本表示（本番） ===
        if mode == 'running' and frame_counter in landmark_dict and calibration_done:
            overlay = frame.copy()
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


            # ===== いつもの描画処理（そのままでOK）=====
            for i, lm in enumerate(example_landmarks):
                if (1 <= i <= 10) or (17 <= i <= 22) or (29 <= i <= 32):
                    continue
                px, py = int(lm.x * w), int(lm.y * h)
                color = LANDMARK_COLORS[i]
                cv2.circle(frame, (px, py), 8, color, -1)

            for a, b in POSE_CONNECTIONS:
                if a < len(example_landmarks) and b < len(example_landmarks):
                    if (a != 0 and a < 11) or (b != 0 and b < 11):
                        continue
                    xa, ya = int(example_landmarks[a].x * w), int(example_landmarks[a].y * h)
                    xb, yb = int(example_landmarks[b].x * w), int(example_landmarks[b].y * h)
                    color = LANDMARK_COLORS[a]
                    cv2.line(frame, (xa, ya), (xb, yb), color, 4)





        # === ユーザーのランドマーク描画＋保存 ===
        if results.pose_landmarks:
            user_lms = results.pose_landmarks.landmark
    
            # === ランドマークをCSVに保存（modeがrunningのときのみ）===
            if mode == 'running' and frame_counter in landmark_dict:
                for i, lm in enumerate(user_lms):
                    if (1 <= i <= 10) or (17 <= i <= 22) or (29 <= i <= 32):
                        continue
                    user_writer.writerow([frame_counter, i, lm.x, lm.y, lm.z, lm.visibility])

        # ==== 表示前にアスペクト比を維持してリサイズ ====
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
