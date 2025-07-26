import csv
import math
from collections import defaultdict

# --- ステップ1：腰のYを読み込み ---
landmark_y = defaultdict(list)
landmarks_by_frame = defaultdict(dict)

with open('landmarks_output_squat.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        frame = int(row['frame'])
        joint = int(row['joint'])
        x = float(row['x'])
        y = float(row['y'])
        z = float(row['z'])

        landmarks_by_frame[frame][joint] = (x, y, z)

        if joint == 23 or joint == 24:  # 左右の腰
            landmark_y[frame].append(y)

# --- ステップ2：最下点のフレーム特定 ---
min_frame = None
max_y = -1  # Mediapipeではyが大きいほど下

for frame, y_list in landmark_y.items():
    if len(y_list) == 2:
        avg_y = sum(y_list) / 2
        if avg_y > max_y:
            max_y = avg_y
            min_frame = frame

print(f"最下点フレーム: {min_frame}")

# --- ステップ3：膝角度の計算関数 ---
def calculate_angle(a, b, c):
    """b を中心にした a-b-c の角度を返す"""
    ba = [a[i] - b[i] for i in range(3)]
    bc = [c[i] - b[i] for i in range(3)]
    dot = sum(ba[i] * bc[i] for i in range(3))
    mag_ba = math.sqrt(sum(x ** 2 for x in ba))
    mag_bc = math.sqrt(sum(x ** 2 for x in bc))
    if mag_ba * mag_bc == 0:
        return None
    angle_rad = math.acos(dot / (mag_ba * mag_bc))
    angle_deg = math.degrees(angle_rad)
    return angle_deg

# --- ステップ4：最下点で膝の角度を計算 ---
lm = landmarks_by_frame[min_frame]

left_angle = calculate_angle(lm[23], lm[25], lm[27])  # 股-膝-足首
right_angle = calculate_angle(lm[24], lm[26], lm[28])

print(f"左膝の角度: {left_angle:.2f}°")
print(f"右膝の角度: {right_angle:.2f}°")
