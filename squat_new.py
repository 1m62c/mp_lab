def draw_text_with_background(frame, text, position, font_scale=1, color=(0, 255, 255), bg_color=(50, 50, 50), thickness=2, padding=15):
    """背景色付きでテキストを描画する関数"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # テキストサイズを取得
    (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    
    # 背景の矩形座標を計算
    x, y = position
    bg_x1 = x - padding
    bg_y1 = y - text_height - padding
    bg_x2 = x + text_width + padding
    bg_y2 = y + baseline + padding
    
    # 背景の矩形を描画
    cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), bg_color, -1)
    cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), color, 2)  # 枠線も追加
    
    # テキストを描画
    cv2.putText(frame, text, position, font, font_scale, color, thickness)

import cv2
import csv
import time
import mediapipe as mp
from collections import defaultdict
from mediapipe.framework.formats import landmark_pb2

import math

def calculate_angle(a, b, c):
    """ 3点の座標から角度を計算（度）"""
    ba = [a.x - b.x, a.y - b.y]
    bc = [c.x - b.x, c.y - b.y]
    dot_product = ba[0]*bc[0] + ba[1]*bc[1]
    magnitude_ba = math.hypot(ba[0], ba[1])
    magnitude_bc = math.hypot(bc[0], bc[1])
    if magnitude_ba * magnitude_bc == 0:
        return 0
    angle = math.acos(dot_product / (magnitude_ba * magnitude_bc))
    return math.degrees(angle)

def create_instruction_screen(width=1280, height=720, bg_color=(30, 30, 30)):
    """指示画面を作成する関数"""
    screen = np.zeros((height, width, 3), dtype=np.uint8)
    screen[:] = bg_color
    return screen

def draw_centered_text(frame, text, font_scale=2, color=(255, 255, 255), thickness=3, y_offset=0, line_spacing=40):
    """画面中央にテキストを描画する関数（行間調整可能）"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # テキストを複数行に分割
    lines = text.split('\n')
    
    # 各行のサイズを計算
    line_heights = []
    line_widths = []
    
    for line in lines:
        (text_width, text_height), baseline = cv2.getTextSize(line, font, font_scale, thickness)
        line_heights.append(text_height)
        line_widths.append(text_width)
    
    # 全体の高さを計算（行間をline_spacingで調整）
    total_height = sum(line_heights) + (len(lines) - 1) * line_spacing
    
    # 開始Y座標を計算（中央揃え）
    h, w = frame.shape[:2]
    start_y = (h - total_height) // 2 + y_offset
    
    # 各行を描画
    current_y = start_y
    for i, line in enumerate(lines):
        # X座標を計算（中央揃え）
        text_x = (w - line_widths[i]) // 2
        text_y = current_y + line_heights[i]
        
        # 背景矩形を描画（オプション）
        padding = 20
        bg_x1 = text_x - padding
        bg_y1 = text_y - line_heights[i] - padding
        bg_x2 = text_x + line_widths[i] + padding
        bg_y2 = text_y + padding
        
        cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), (50, 50, 50), -1)
        cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), color, 2)
        
        # テキストを描画
        cv2.putText(frame, line, (text_x, text_y), font, font_scale, color, thickness)
        
        current_y += line_heights[i] + line_spacing  # 次の行へ（行間調整）

def draw_countdown_circle(frame, remaining_time, total_time=5):
    """残り時間を円形で表示する関数（2倍サイズ）"""
    h, w = frame.shape[:2]
    center = (w - 120, 120)  # 位置を少し調整（大きくなった分）
    radius = 60  # 2倍のサイズ（30 → 60）
    
    # 背景円
    cv2.circle(frame, center, radius, (50, 50, 50), -1)
    cv2.circle(frame, center, radius, (255, 255, 255), 3)  # 線も太く
    
    # プログレス円
    angle = int(360 * (total_time - remaining_time) / total_time)
    if angle > 0:
        # 円弧を描画（上から時計回り）
        cv2.ellipse(frame, center, (radius-8, radius-8), -90, 0, angle, (0, 255, 255), 8)  # 太さも2倍
    
    # 残り秒数を表示（フォントサイズも大きく）
    cv2.putText(frame, str(int(remaining_time) + 1), 
               (center[0] - 15, center[1] + 10), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)  # フォントサイズ1.5倍

def evaluate_squat_angle(angle):
    """スクワット角度を評価してメッセージを返す"""
    if angle >= 160:
        return "Bend your knees more.", (0, 100, 255)  # オレンジ色
    elif 100 <= angle <= 159:
        return "Good!", (0, 255, 0)  # 緑色
    elif 75 <= angle <= 99:
        return "Excellent!!", (0, 255, 255)  # 黄色
    else:  # 74度以下
        return "Too much.", (0, 0, 255)  # 赤色

def draw_evaluation_message(frame, message, color, angle):
    """評価メッセージを画面に描画（右上）"""
    h, w, _ = frame.shape
    x_pos = w - 400
    y_pos = 10
    
    cv2.rectangle(frame, (x_pos, y_pos), (x_pos + 390, y_pos + 70), (0, 0, 0), -1)
    cv2.rectangle(frame, (x_pos, y_pos), (x_pos + 390, y_pos + 70), color, 2)
    
    cv2.putText(frame, message, (x_pos + 10, y_pos + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    cv2.putText(frame, f"Knee Angle: {angle:.1f}°", (x_pos + 10, y_pos + 55), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

# 必要なライブラリをインポート
import numpy as np

# === 指示メッセージの定義 ===
INSTRUCTIONS = {
    'intro': "Watch the demonstration.",
    'learning': "Learn the correct posture.",
    'checkpoint': "Pay attention to the checkpoints.\nTo finish, make a circle with both arms."
}

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

# === 変数初期化 ===
initial_offset_x = 0
initial_offset_y = 0
scale_factor = 1.0
calibration_done = False

end_gesture_start_time = None
END_HOLD_DURATION = 2

current_evaluation_message = ""
current_evaluation_color = (255, 255, 255)
current_knee_angle = 0

cap = cv2.VideoCapture(0)
frame_counter = 0

cv2.namedWindow('Squat Training System', cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty('Squat Training System', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# === メインループのモード管理 ===
mode = 'instruction_intro'  # 'instruction_intro' -> 'example_video' -> 'instruction_learning' -> 'waiting' -> 'countdown' -> 'running' -> 'instruction_checkpoint' -> 'fixed' -> 'end'
countdown_start_time = None
squat_in_progress = False
lowest_knee_angle = 180

# 指示画面のタイマー管理
instruction_start_time = None
INSTRUCTION_DURATION = 5  # 指示画面表示時間（秒）

# ユーザーの保存用csv用意
user_csv = open('landmarks_user_squat.csv', 'w', newline='')
user_writer = csv.writer(user_csv)
user_writer.writerow(['frame', 'id', 'x', 'y', 'z', 'visibility'])

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        key = cv2.waitKey(1) & 0xFF
        
        # === 指示画面の表示 ===
        if mode in ['instruction_intro', 'instruction_learning', 'instruction_checkpoint']:
            # タイマー開始
            if instruction_start_time is None:
                instruction_start_time = time.time()
            
            # 指示画面を作成
            instruction_frame = create_instruction_screen()
            
            if mode == 'instruction_intro':
                draw_centered_text(instruction_frame, INSTRUCTIONS['intro'], font_scale=1.5, line_spacing=50)
            elif mode == 'instruction_learning':
                draw_centered_text(instruction_frame, INSTRUCTIONS['learning'], font_scale=1.5, line_spacing=50)
            elif mode == 'instruction_checkpoint':
                draw_centered_text(instruction_frame, INSTRUCTIONS['checkpoint'], font_scale=1.2, line_spacing=60)
            
            # 残り時間を計算して円形タイマー表示
            elapsed_time = time.time() - instruction_start_time
            remaining_time = INSTRUCTION_DURATION - elapsed_time
            
            if remaining_time > 0:
                draw_countdown_circle(instruction_frame, remaining_time, INSTRUCTION_DURATION)
                cv2.imshow('Squat Training System', instruction_frame)
            else:
                # 5秒経過したら次のモードへ
                instruction_start_time = None  # タイマーリセット
                if mode == 'instruction_intro':
                    mode = 'example_video'
                elif mode == 'instruction_learning':
                    mode = 'waiting'
                elif mode == 'instruction_checkpoint':
                    mode = 'fixed'
            
            if key == ord('q'):
                break
            continue
        
        # === お手本動画の再生 ===
        elif mode == 'example_video':
            # お手本動画を再生（コメントアウト部分を使用）
            example_video = cv2.VideoCapture('movie/squat.mp4')
            
            while example_video.isOpened():
                ret, frame = example_video.read()
                if not ret:
                    break
                frame = cv2.resize(frame, (1280, 720))
                cv2.imshow('Squat Training System', frame)
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break
            
            example_video.release()
            mode = 'instruction_learning'
            continue
        
        # === カメラ処理 ===
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        h, w, _ = frame.shape

        if mode == 'waiting' and results.pose_landmarks:
            # 両手上げポーズの検出
            lms = results.pose_landmarks.landmark
            lw_y = lms[mp_pose.PoseLandmark.LEFT_WRIST].y
            rw_y = lms[mp_pose.PoseLandmark.RIGHT_WRIST].y
            ls_y = lms[mp_pose.PoseLandmark.LEFT_SHOULDER].y
            rs_y = lms[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
            if lw_y < ls_y and rw_y < rs_y:
                mode = 'countdown'
                countdown_start_time = time.time()
            
            # 待機メッセージを背景付きで表示
            draw_text_with_background(frame, "Raise both hands to start!", (50, 100), 
                                    font_scale=1, color=(0, 255, 255), bg_color=(50, 50, 50))

        elif mode == 'countdown':
            elapsed = time.time() - countdown_start_time
            remaining = 3 - int(elapsed)
            if remaining > 0:
                cv2.putText(frame, str(remaining), (w//2-50, h//2), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 7)
            else:
                if not calibration_done and results.pose_landmarks:
                    # キャリブレーション処理
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

        elif mode == 'running' and frame_counter in landmark_dict and calibration_done:
            # お手本データを表示
            landmarks = landmark_dict[frame_counter]
            cx = (landmarks[23].x + landmarks[24].x) / 2
            cy = (landmarks[23].y + landmarks[24].y) / 2
            cz = (landmarks[23].z + landmarks[24].z) / 2
            SCALE = 1.0
            OFFSET_Y = 0
            example_landmarks = []
            for lm in landmarks:
                new_lm = landmark_pb2.NormalizedLandmark()
                new_lm.x = min(max(cx + (lm.x - cx) * SCALE * scale_factor + initial_offset_x, 0.0), 1.0)
                new_lm.y = min(max(cy + (lm.y - cy) * SCALE * scale_factor + OFFSET_Y + initial_offset_y, 0.0), 1.0)
                new_lm.z = (lm.z - cz) * SCALE * scale_factor + cz
                new_lm.visibility = lm.visibility
                example_landmarks.append(new_lm)
            
            # 関節点を描画
            for i, lm in enumerate(example_landmarks):
                if (1 <= i <= 10) or (17 <= i <= 22) or (29 <= i <= 32): continue
                px, py = int(lm.x * w), int(lm.y * h)
                color = LANDMARK_COLORS[i]
                cv2.circle(frame, (px, py), 8, color, -1)
            
            # 骨格を描画
            for a, b in POSE_CONNECTIONS:
                if a < len(example_landmarks) and b < len(example_landmarks):
                    if (a != 0 and a < 11) or (b != 0 and b < 11): continue
                    xa, ya = int(example_landmarks[a].x * w), int(example_landmarks[a].y * h)
                    xb, yb = int(example_landmarks[b].x * w), int(example_landmarks[b].y * h)
                    color = LANDMARK_COLORS[a]
                    cv2.line(frame, (xa, ya), (xb, yb), color, 4)

            if frame_counter >= max(landmark_dict.keys()):
                mode = 'instruction_checkpoint'

        elif mode == 'fixed' and min_y_frame in landmark_dict:
            # チェックポイント表示
            landmarks = landmark_dict[min_y_frame]
            cx = (landmarks[23].x + landmarks[24].x) / 2
            cy = (landmarks[23].y + landmarks[24].y) / 2
            cz = (landmarks[23].z + landmarks[24].z) / 2
            SCALE = 1.3
            OFFSET_Y = 0
            example_landmarks = []
            for lm in landmarks:
                new_lm = landmark_pb2.NormalizedLandmark()
                new_lm.x = min(max(cx + (lm.x - cx) * SCALE * scale_factor + initial_offset_x, 0.0), 1.0)
                new_lm.y = min(max(cy + (lm.y - cy) * SCALE * scale_factor + OFFSET_Y + initial_offset_y, 0.0), 1.0)
                new_lm.z = (lm.z - cz) * SCALE * scale_factor + cz
                new_lm.visibility = lm.visibility
                example_landmarks.append(new_lm)
            
            # 関節点とスケルトン描画
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

            # ユーザーデータ保存
            if results.pose_landmarks: 
                for i, landmark in enumerate(results.pose_landmarks.landmark):
                    user_writer.writerow([
                        frame_counter, i, landmark.x, landmark.y, landmark.z, landmark.visibility
                    ])

            # 終了ジェスチャー検出
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
            
            # 膝角度計算と評価
            if results.pose_landmarks:
                lms = results.pose_landmarks.landmark
                left_angle = calculate_angle(lms[mp_pose.PoseLandmark.LEFT_HIP],
                                            lms[mp_pose.PoseLandmark.LEFT_KNEE],
                                            lms[mp_pose.PoseLandmark.LEFT_ANKLE])
                right_angle = calculate_angle(lms[mp_pose.PoseLandmark.RIGHT_HIP],
                                            lms[mp_pose.PoseLandmark.RIGHT_KNEE],
                                            lms[mp_pose.PoseLandmark.RIGHT_ANKLE])
                avg_knee_angle = (left_angle + right_angle) / 2
                current_knee_angle = avg_knee_angle

                message, color = evaluate_squat_angle(avg_knee_angle)
                current_evaluation_message = message
                current_evaluation_color = color

                # スクワット進行管理
                if avg_knee_angle < 100:
                    if not squat_in_progress:
                        squat_in_progress = True
                        lowest_knee_angle = avg_knee_angle
                    else:
                        if avg_knee_angle < lowest_knee_angle:
                            lowest_knee_angle = avg_knee_angle
                else:
                    if squat_in_progress:
                        print(f"✅ 最下点の膝角度: {lowest_knee_angle:.2f} 度")
                        squat_in_progress = False

            # 評価メッセージ表示
            if current_evaluation_message:
                draw_evaluation_message(frame, current_evaluation_message, current_evaluation_color, current_knee_angle)

        elif mode == 'end':
            text = "Training Finished!"
            font = cv2.FONT_HERSHEY_SIMPLEX
            scale = 2
            thickness = 5
            (text_width, text_height), baseline = cv2.getTextSize(text, font, scale, thickness)
            text_x = (frame.shape[1] - text_width) // 2
            text_y = (frame.shape[0] + text_height) // 2
            cv2.putText(frame, text, (text_x, text_y), font, scale, (0, 255, 255), thickness)
            cv2.imshow('Squat Training System', frame)
            cv2.waitKey(3000)
            break

        # フレーム表示（指示画面以外）
        if mode not in ['instruction_intro', 'instruction_learning', 'instruction_checkpoint']:
            cv2.imshow('Squat Training System', frame)

        if key == ord('q'):
            break

        if mode in ['running', 'fixed']:
            frame_counter += 1

cap.release()
user_csv.close()
cv2.destroyAllWindows()