# # import csv
# # import math
# # import matplotlib.pyplot as plt
# # from collections import defaultdict
# # import numpy as np
# # from scipy.signal import find_peaks

# # def calculate_angle_from_coords(a, b, c):
# #     """3点の座標から角度を計算（度）
# #     a, b, c はそれぞれ (x, y) のタプル"""
# #     ba = [a[0] - b[0], a[1] - b[1]]
# #     bc = [c[0] - b[0], c[1] - b[1]]
    
# #     dot_product = ba[0]*bc[0] + ba[1]*bc[1]
# #     magnitude_ba = math.hypot(ba[0], ba[1])
# #     magnitude_bc = math.hypot(bc[0], bc[1])
    
# #     if magnitude_ba * magnitude_bc == 0:
# #         return 0
    
# #     angle = math.acos(max(-1, min(1, dot_product / (magnitude_ba * magnitude_bc))))
# #     return math.degrees(angle)

# # def load_user_landmarks(csv_file):
# #     """CSVファイルからユーザーのランドマークデータを読み込み"""
# #     landmark_data = defaultdict(lambda: defaultdict(dict))
    
# #     try:
# #         with open(csv_file, 'r', newline='') as csvfile:
# #             reader = csv.DictReader(csvfile)
# #             for row in reader:
# #                 frame = int(row['frame'])
# #                 joint_id = int(row['id'])
# #                 x = float(row['x'])
# #                 y = float(row['y'])
# #                 z = float(row['z'])
# #                 visibility = float(row['visibility'])
                
# #                 landmark_data[frame][joint_id] = {
# #                     'x': x, 'y': y, 'z': z, 'visibility': visibility
# #                 }
        
# #         print(f"✅ データ読み込み完了！フレーム数: {len(landmark_data)}")
# #         return landmark_data
    
# #     except FileNotFoundError:
# #         print(f"❌ ファイルが見つかりません: {csv_file}")
# #         return None
# #     except Exception as e:
# #         print(f"❌ データ読み込みエラー: {e}")
# #         return None

# # def extract_hip_positions(landmark_data):
# #     """各フレームの腰の位置（Y座標の平均）を抽出"""
# #     hip_positions = {}
    
# #     for frame, joints in landmark_data.items():
# #         # MediaPipeの腰の関節ID: 23(左腰), 24(右腰)
# #         if 23 in joints and 24 in joints:
# #             left_hip_y = joints[23]['y']
# #             right_hip_y = joints[24]['y']
# #             avg_hip_y = (left_hip_y + right_hip_y) / 2
# #             hip_positions[frame] = avg_hip_y
    
# #     return hip_positions

# # def find_squat_checkpoints(hip_positions, min_distance=30, height_threshold=0.02):
# #     """スクワットのチェックポイント（腰の最下点）を検出"""
# #     frames = list(hip_positions.keys())
# #     hip_values = [hip_positions[f] for f in frames]
    
# #     # ピーク検出（腰が最も下がった点 = Y座標が最大の点）
# #     peaks, properties = find_peaks(hip_values, 
# #                                   distance=min_distance,  # 最小間隔
# #                                   prominence=height_threshold)  # 最小の高さ変化
    
# #     checkpoint_frames = [frames[i] for i in peaks]
# #     checkpoint_values = [hip_values[i] for i in peaks]
    
# #     print(f"🎯 検出されたチェックポイント数: {len(checkpoint_frames)}")
    
# #     # 結果をフレーム番号順にソート
# #     checkpoint_data = list(zip(checkpoint_frames, checkpoint_values))
# #     checkpoint_data.sort(key=lambda x: x[0])
    
# #     return checkpoint_data

# # def calculate_knee_angles_at_checkpoints(landmark_data, checkpoint_frames):
# #     """各チェックポイントでの膝角度を計算"""
# #     knee_angles = []
    
# #     for frame, hip_y in checkpoint_frames:
# #         if frame not in landmark_data:
# #             print(f"⚠️  フレーム {frame} のデータがありません")
# #             continue
        
# #         joints = landmark_data[frame]
        
# #         # 必要な関節が存在するかチェック
# #         required_joints = [23, 24, 25, 26, 29, 30]  # 左右の腰、膝、かかと
# #         if not all(joint_id in joints for joint_id in required_joints):
# #             print(f"⚠️  フレーム {frame} に必要な関節データがありません")
# #             continue
        
# #         # 左足の角度計算（腰-膝-かかと）
# #         left_hip = (joints[23]['x'], joints[23]['y'])
# #         left_knee = (joints[25]['x'], joints[25]['y'])
# #         left_heel = (joints[29]['x'], joints[29]['y'])
# #         left_angle = calculate_angle_from_coords(left_hip, left_knee, left_heel)
        
# #         # 右足の角度計算（腰-膝-かかと）
# #         right_hip = (joints[24]['x'], joints[24]['y'])
# #         right_knee = (joints[26]['x'], joints[26]['y'])
# #         right_heel = (joints[30]['x'], joints[30]['y'])
# #         right_angle = calculate_angle_from_coords(right_hip, right_knee, right_heel)
        
# #         # 平均角度
# #         avg_angle = (left_angle + right_angle) / 2
        
# #         knee_angles.append({
# #             'frame': frame,
# #             'hip_y': hip_y,
# #             'left_knee_angle': left_angle,
# #             'right_knee_angle': right_angle,
# #             'avg_knee_angle': avg_angle
# #         })
        
# #         print(f"📐 フレーム {frame}: 左膝 {left_angle:.1f}°, 右膝 {right_angle:.1f}°, 平均 {avg_angle:.1f}°")
    
# #     return knee_angles

# # def evaluate_squat_quality(knee_angles):
# #     """スクワットの品質を評価"""
# #     if not knee_angles:
# #         print("❌ 評価するデータがありません")
# #         return
    
# #     print("\n🏆 スクワット品質評価結果:")
# #     print("="*50)
    
# #     excellent_count = 0
# #     good_count = 0
# #     needs_improvement = 0
    
# #     for i, data in enumerate(knee_angles, 1):
# #         angle = data['avg_knee_angle']
        
# #         if 75 <= angle <= 99:
# #             quality = "Excellent!! 🌟"
# #             excellent_count += 1
# #         elif 100 <= angle <= 159:
# #             quality = "Good! 👍"
# #             good_count += 1
# #         elif angle >= 160:
# #             quality = "もっと膝を曲げて 💪"
# #             needs_improvement += 1
# #         else:
# #             quality = "曲げすぎ注意 ⚠️"
# #             needs_improvement += 1
        
# #         print(f"{i:2d}回目: {angle:5.1f}° - {quality}")
    
# #     total = len(knee_angles)
# #     print("\n📊 まとめ:")
# #     print(f"Excellent: {excellent_count}/{total} ({excellent_count/total*100:.1f}%)")
# #     print(f"Good:      {good_count}/{total} ({good_count/total*100:.1f}%)")
# #     print(f"要改善:     {needs_improvement}/{total} ({needs_improvement/total*100:.1f}%)")

# # def visualize_results(hip_positions, checkpoint_frames, knee_angles):
# #     """結果をグラフで可視化"""
# #     frames = list(hip_positions.keys())
# #     hip_values = [hip_positions[f] for f in frames]
# #     checkpoint_frame_nums = [f for f, _ in checkpoint_frames]
# #     checkpoint_hip_values = [v for _, v in checkpoint_frames]
    
# #     plt.figure(figsize=(12, 8))
    
# #     # 上段: 腰のY座標の変化
# #     plt.subplot(2, 1, 1)
# #     plt.plot(frames, hip_values, 'b-', linewidth=2, label='腰のY座標')
# #     plt.scatter(checkpoint_frame_nums, checkpoint_hip_values, 
# #                color='red', s=100, zorder=5, label='チェックポイント')
# #     plt.xlabel('フレーム番号')
# #     plt.ylabel('腰のY座標')
# #     plt.title('🏃‍♀️ スクワット動作の腰の動き')
# #     plt.legend()
# #     plt.grid(True, alpha=0.3)
    
# #     # 下段: 各チェックポイントでの膝角度
# #     if knee_angles:
# #         plt.subplot(2, 1, 2)
# #         squat_numbers = list(range(1, len(knee_angles) + 1))
# #         angles = [data['avg_knee_angle'] for data in knee_angles]
        
# #         colors = []
# #         for angle in angles:
# #             if 75 <= angle <= 99:
# #                 colors.append('gold')  # Excellent
# #             elif 100 <= angle <= 159:
# #                 colors.append('lightgreen')  # Good
# #             else:
# #                 colors.append('lightcoral')  # 要改善
        
# #         bars = plt.bar(squat_numbers, angles, color=colors, alpha=0.7)
        
# #         # 評価基準ライン
# #         plt.axhspan(75, 99, alpha=0.2, color='gold', label='Excellent (75-99°)')
# #         plt.axhspan(100, 159, alpha=0.2, color='green', label='Good (100-159°)')
        
# #         plt.xlabel('スクワット回数')
# #         plt.ylabel('膝角度 (度)')
# #         plt.title('🎯 各チェックポイントでの膝角度')
# #         plt.legend()
# #         plt.grid(True, alpha=0.3)
        
# #         # 数値をバーの上に表示
# #         for bar, angle in zip(bars, angles):
# #             plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
# #                     f'{angle:.1f}°', ha='center', va='bottom')
    
# #     plt.tight_layout()
# #     plt.show()

# # def main():
# #     """メイン処理"""
# #     print("🏋️‍♀️ スクワット分析プログラム開始！")
# #     print("="*50)
    
# #     # CSVファイル名（必要に応じて変更してね！）
# #     csv_file = 'landmarks_user_squat.csv'
    
# #     # 1. データ読み込み
# #     landmark_data = load_user_landmarks(csv_file)
# #     if landmark_data is None:
# #         return
    
# #     # 2. 腰の位置抽出
# #     hip_positions = extract_hip_positions(landmark_data)
# #     if not hip_positions:
# #         print("❌ 腰の位置データが取得できませんでした")
# #         return
    
# #     print(f"📈 腰の位置データ取得完了: {len(hip_positions)}フレーム")
    
# #     # 3. チェックポイント検出
# #     checkpoint_frames = find_squat_checkpoints(hip_positions)
# #     if not checkpoint_frames:
# #         print("❌ チェックポイントが検出できませんでした")
# #         return
    
# #     # 4. 各チェックポイントでの膝角度計算
# #     knee_angles = calculate_knee_angles_at_checkpoints(landmark_data, checkpoint_frames)
    
# #     # 5. 品質評価
# #     evaluate_squat_quality(knee_angles)
    
# #     # 6. 結果の可視化
# #     visualize_results(hip_positions, checkpoint_frames, knee_angles)
    
# #     print(f"\n🎉 分析完了！{len(knee_angles)}回のスクワットを検出しました！")

# # if __name__ == "__main__":
# #     main()

# import csv
# import math
# import matplotlib.pyplot as plt
# from collections import defaultdict
# import numpy as np
# from scipy.signal import find_peaks

# def calculate_angle_from_coords(a, b, c):
#     """3点の座標から角度を計算（度）"""
#     ba = [a[0] - b[0], a[1] - b[1]]
#     bc = [c[0] - b[0], c[1] - b[1]]
    
#     dot_product = ba[0]*bc[0] + ba[1]*bc[1]
#     magnitude_ba = math.hypot(ba[0], ba[1])
#     magnitude_bc = math.hypot(bc[0], bc[1])
    
#     if magnitude_ba * magnitude_bc == 0:
#         return 0
    
#     angle = math.acos(max(-1, min(1, dot_product / (magnitude_ba * magnitude_bc))))
#     return math.degrees(angle)

# def load_user_landmarks(csv_file):
#     """CSVファイルからユーザーのランドマークデータを読み込み"""
#     landmark_data = defaultdict(lambda: defaultdict(dict))
    
#     try:
#         with open(csv_file, 'r', newline='') as csvfile:
#             reader = csv.DictReader(csvfile)
#             for row in reader:
#                 frame = int(row['frame'])
#                 joint_id = int(row['id'])
#                 x = float(row['x'])
#                 y = float(row['y'])
#                 z = float(row['z'])
#                 visibility = float(row['visibility'])
                
#                 landmark_data[frame][joint_id] = {
#                     'x': x, 'y': y, 'z': z, 'visibility': visibility
#                 }
        
#         print(f"✅ データ読み込み完了！フレーム数: {len(landmark_data)}")
#         return landmark_data
    
#     except FileNotFoundError:
#         print(f"❌ ファイルが見つかりません: {csv_file}")
#         return None
#     except Exception as e:
#         print(f"❌ データ読み込みエラー: {e}")
#         return None

# def calculate_knee_angles_all_frames(landmark_data):
#     """全フレームで膝角度を計算"""
#     knee_angles_by_frame = {}
#     hip_positions = {}
    
#     for frame, joints in landmark_data.items():
#         # 必要な関節が存在するかチェック
#         required_joints = [23, 24, 25, 26, 29, 30]  # 左右の腰、膝、かかと
#         if not all(joint_id in joints for joint_id in required_joints):
#             continue
        
#         # 腰の位置も同時に取得
#         left_hip_y = joints[23]['y']
#         right_hip_y = joints[24]['y']
#         avg_hip_y = (left_hip_y + right_hip_y) / 2
#         hip_positions[frame] = avg_hip_y
        
#         # 膝角度計算
#         # 左足の角度計算（腰-膝-かかと）
#         left_hip = (joints[23]['x'], joints[23]['y'])
#         left_knee = (joints[25]['x'], joints[25]['y'])
#         left_heel = (joints[29]['x'], joints[29]['y'])
#         left_angle = calculate_angle_from_coords(left_hip, left_knee, left_heel)
        
#         # 右足の角度計算（腰-膝-かかと）
#         right_hip = (joints[24]['x'], joints[24]['y'])
#         right_knee = (joints[26]['x'], joints[26]['y'])
#         right_heel = (joints[30]['x'], joints[30]['y'])
#         right_angle = calculate_angle_from_coords(right_hip, right_knee, right_heel)
        
#         # 平均角度
#         avg_angle = (left_angle + right_angle) / 2
        
#         knee_angles_by_frame[frame] = {
#             'left_knee_angle': left_angle,
#             'right_knee_angle': right_angle,
#             'avg_knee_angle': avg_angle,
#             'hip_y': avg_hip_y
#         }
    
#     return knee_angles_by_frame, hip_positions

# def find_checkpoints_by_method(knee_angles_by_frame, hip_positions, method='realtime'):
#     """異なる方法でチェックポイントを検出"""
    
#     if method == 'realtime':
#         # リアルタイム方式（ユーザープログラムと同じロジック）
#         print("🎯 リアルタイム方式でチェックポイント検出中...")
        
#         checkpoints = []
#         squat_in_progress = False
#         lowest_knee_angle = 180
#         lowest_frame = None
        
#         sorted_frames = sorted(knee_angles_by_frame.keys())
        
#         for frame in sorted_frames:
#             avg_knee_angle = knee_angles_by_frame[frame]['avg_knee_angle']
            
#             if avg_knee_angle < 100:  # しゃがみ中
#                 if not squat_in_progress:
#                     squat_in_progress = True
#                     lowest_knee_angle = avg_knee_angle
#                     lowest_frame = frame
#                 else:
#                     # さらに小さければ更新
#                     if avg_knee_angle < lowest_knee_angle:
#                         lowest_knee_angle = avg_knee_angle
#                         lowest_frame = frame
#             else:  # 立ち上がった
#                 if squat_in_progress:
#                     # スクワット完了！
#                     checkpoints.append((lowest_frame, knee_angles_by_frame[lowest_frame]))
#                     print(f"📐 リアルタイム検出: フレーム{lowest_frame}, 膝角度{lowest_knee_angle:.1f}°")
#                     squat_in_progress = False
#                     lowest_knee_angle = 180
        
#         return checkpoints
    
#     elif method == 'hip_based':
#         # 腰Y座標ベース方式（分析プログラムと同じ）
#         print("🎯 腰Y座標ベース方式でチェックポイント検出中...")
        
#         frames = list(hip_positions.keys())
#         hip_values = [hip_positions[f] for f in frames]
        
#         # ピーク検出
#         peaks, properties = find_peaks(hip_values, distance=30, prominence=0.02)
        
#         checkpoints = []
#         for i in peaks:
#             frame = frames[i]
#             if frame in knee_angles_by_frame:
#                 checkpoints.append((frame, knee_angles_by_frame[frame]))
#                 knee_angle = knee_angles_by_frame[frame]['avg_knee_angle']
#                 print(f"📐 腰ベース検出: フレーム{frame}, 膝角度{knee_angle:.1f}°")
        
#         return checkpoints
    
#     elif method == 'knee_based':
#         # 膝角度ベース方式（膝角度が最小になる点を検出）
#         print("🎯 膝角度ベース方式でチェックポイント検出中...")
        
#         frames = list(knee_angles_by_frame.keys())
#         knee_values = [-knee_angles_by_frame[f]['avg_knee_angle'] for f in frames]  # 負数にして最小値を最大値として検出
        
#         # ピーク検出
#         peaks, properties = find_peaks(knee_values, distance=30, prominence=5)  # 5度以上の変化
        
#         checkpoints = []
#         for i in peaks:
#             frame = frames[i]
#             checkpoints.append((frame, knee_angles_by_frame[frame]))
#             knee_angle = knee_angles_by_frame[frame]['avg_knee_angle']
#             print(f"📐 膝角度ベース検出: フレーム{frame}, 膝角度{knee_angle:.1f}°")
        
#         return checkpoints

# def compare_detection_methods(knee_angles_by_frame, hip_positions):
#     """3つの検出方法を比較"""
    
#     print("\n🔍 3つの検出方法で比較分析中...")
#     print("="*60)
    
#     # 各方法でチェックポイント検出
#     realtime_checkpoints = find_checkpoints_by_method(knee_angles_by_frame, hip_positions, 'realtime')
#     hip_based_checkpoints = find_checkpoints_by_method(knee_angles_by_frame, hip_positions, 'hip_based')
#     knee_based_checkpoints = find_checkpoints_by_method(knee_angles_by_frame, hip_positions, 'knee_based')
    
#     # 結果比較
#     print(f"\n📊 検出結果比較:")
#     print(f"🟢 リアルタイム方式: {len(realtime_checkpoints)}個")
#     print(f"🔵 腰Y座標ベース方式: {len(hip_based_checkpoints)}個")
#     print(f"🟡 膝角度ベース方式: {len(knee_based_checkpoints)}個")
    
#     # 詳細比較
#     print(f"\n📋 詳細比較:")
#     max_len = max(len(realtime_checkpoints), len(hip_based_checkpoints), len(knee_based_checkpoints))
    
#     print(f"{'回数':<4} {'リアルタイム':<15} {'腰ベース':<15} {'膝ベース':<15}")
#     print("-" * 60)
    
#     for i in range(max_len):
#         realtime_str = f"F{realtime_checkpoints[i][0]}({realtime_checkpoints[i][1]['avg_knee_angle']:.1f}°)" if i < len(realtime_checkpoints) else "-"
#         hip_str = f"F{hip_based_checkpoints[i][0]}({hip_based_checkpoints[i][1]['avg_knee_angle']:.1f}°)" if i < len(hip_based_checkpoints) else "-"
#         knee_str = f"F{knee_based_checkpoints[i][0]}({knee_based_checkpoints[i][1]['avg_knee_angle']:.1f}°)" if i < len(knee_based_checkpoints) else "-"
        
#         print(f"{i+1:<4} {realtime_str:<15} {hip_str:<15} {knee_str:<15}")
    
#     return realtime_checkpoints, hip_based_checkpoints, knee_based_checkpoints

# def visualize_comparison(knee_angles_by_frame, hip_positions, realtime_checkpoints, hip_based_checkpoints, knee_based_checkpoints):
#     """3つの検出方法を可視化で比較"""
    
#     frames = sorted(knee_angles_by_frame.keys())
#     hip_values = [hip_positions[f] for f in frames]
#     knee_values = [knee_angles_by_frame[f]['avg_knee_angle'] for f in frames]
    
#     fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
    
#     # 上段: 腰のY座標
#     ax1.plot(frames, hip_values, 'b-', linewidth=2, label='腰のY座標', alpha=0.7)
    
#     # チェックポイントをプロット
#     if hip_based_checkpoints:
#         hip_checkpoint_frames = [cp[0] for cp in hip_based_checkpoints]
#         hip_checkpoint_values = [hip_positions[f] for f in hip_checkpoint_frames]
#         ax1.scatter(hip_checkpoint_frames, hip_checkpoint_values, 
#                    color='blue', s=100, marker='s', label='腰ベース検出', zorder=5)
    
#     ax1.set_xlabel('フレーム番号')
#     ax1.set_ylabel('腰のY座標')
#     ax1.set_title('🍑 腰の位置変化とチェックポイント')
#     ax1.legend()
#     ax1.grid(True, alpha=0.3)
    
#     # 下段: 膝角度
#     ax2.plot(frames, knee_values, 'g-', linewidth=2, label='膝角度', alpha=0.7)
    
#     # 各方法のチェックポイントをプロット
#     if realtime_checkpoints:
#         realtime_frames = [cp[0] for cp in realtime_checkpoints]
#         realtime_angles = [cp[1]['avg_knee_angle'] for cp in realtime_checkpoints]
#         ax2.scatter(realtime_frames, realtime_angles, 
#                    color='red', s=100, marker='o', label='🟢 リアルタイム検出', zorder=5)
    
#     if hip_based_checkpoints:
#         hip_frames = [cp[0] for cp in hip_based_checkpoints]
#         hip_angles = [cp[1]['avg_knee_angle'] for cp in hip_based_checkpoints]
#         ax2.scatter(hip_frames, hip_angles, 
#                    color='blue', s=80, marker='s', label='🔵 腰ベース検出', zorder=4)
    
#     if knee_based_checkpoints:
#         knee_frames = [cp[0] for cp in knee_based_checkpoints]
#         knee_angles = [cp[1]['avg_knee_angle'] for cp in knee_based_checkpoints]
#         ax2.scatter(knee_frames, knee_angles, 
#                    color='orange', s=60, marker='^', label='🟡 膝ベース検出', zorder=3)
    
#     # 評価基準ライン
#     ax2.axhspan(75, 99, alpha=0.2, color='gold', label='Excellent (75-99°)')
#     ax2.axhspan(100, 159, alpha=0.2, color='green', label='Good (100-159°)')
    
#     ax2.set_xlabel('フレーム番号')
#     ax2.set_ylabel('膝角度 (度)')
#     ax2.set_title('🦵 膝角度変化と各検出方法の比較')
#     ax2.legend()
#     ax2.grid(True, alpha=0.3)
    
#     plt.tight_layout()
#     plt.show()

# def main():
#     """メイン処理"""
#     print("🔍 チェックポイント検出方法比較分析プログラム")
#     print("="*60)
    
#     csv_file = 'landmarks_user_squat.csv'
    
#     # データ読み込み
#     landmark_data = load_user_landmarks(csv_file)
#     if landmark_data is None:
#         return
    
#     # 全フレームの膝角度と腰位置を計算
#     knee_angles_by_frame, hip_positions = calculate_knee_angles_all_frames(landmark_data)
    
#     if not knee_angles_by_frame:
#         print("❌ 膝角度データが取得できませんでした")
#         return
    
#     print(f"📈 膝角度データ取得完了: {len(knee_angles_by_frame)}フレーム")
    
#     # 3つの方法で比較分析
#     realtime_checkpoints, hip_based_checkpoints, knee_based_checkpoints = compare_detection_methods(
#         knee_angles_by_frame, hip_positions)
    
#     # 可視化
#     visualize_comparison(knee_angles_by_frame, hip_positions, 
#                         realtime_checkpoints, hip_based_checkpoints, knee_based_checkpoints)
    
#     print(f"\n🎉 比較分析完了！")
#     print(f"💡 どの方法が一番適切か確認してみてね〜✨")

# if __name__ == "__main__":
#     main()

import csv
import math
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from scipy.signal import find_peaks

def calculate_angle_from_coords(a, b, c):
    """3点の座標から角度を計算（度）"""
    ba = [a[0] - b[0], a[1] - b[1]]
    bc = [c[0] - b[0], c[1] - b[1]]
    
    dot_product = ba[0]*bc[0] + ba[1]*bc[1]
    magnitude_ba = math.hypot(ba[0], ba[1])
    magnitude_bc = math.hypot(bc[0], bc[1])
    
    if magnitude_ba * magnitude_bc == 0:
        return 0
    
    angle = math.acos(max(-1, min(1, dot_product / (magnitude_ba * magnitude_bc))))
    return math.degrees(angle)

def load_user_landmarks(csv_file):
    """CSVファイルからユーザーのランドマークデータを読み込み"""
    landmark_data = defaultdict(lambda: defaultdict(dict))
    
    try:
        with open(csv_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                frame = int(row['frame'])
                joint_id = int(row['id'])
                x = float(row['x'])
                y = float(row['y'])
                z = float(row['z'])
                visibility = float(row['visibility'])
                
                landmark_data[frame][joint_id] = {
                    'x': x, 'y': y, 'z': z, 'visibility': visibility
                }
        
        print(f"✅ データ読み込み完了！フレーム数: {len(landmark_data)}")
        return landmark_data
    
    except FileNotFoundError:
        print(f"❌ ファイルが見つかりません: {csv_file}")
        return None
    except Exception as e:
        print(f"❌ データ読み込みエラー: {e}")
        return None

def calculate_knee_angles_all_frames(landmark_data):
    """全フレームで膝角度を計算"""
    knee_angles_by_frame = {}
    hip_positions = {}
    
    for frame, joints in landmark_data.items():
        # 必要な関節が存在するかチェック
        required_joints = [23, 24, 25, 26, 29, 30]  # 左右の腰、膝、かかと
        if not all(joint_id in joints for joint_id in required_joints):
            continue
        
        # 腰の位置も記録（可視化用）
        left_hip_y = joints[23]['y']
        right_hip_y = joints[24]['y']
        avg_hip_y = (left_hip_y + right_hip_y) / 2
        hip_positions[frame] = avg_hip_y
        
        # 膝角度計算
        # 左足の角度計算（腰-膝-かかと）
        left_hip = (joints[23]['x'], joints[23]['y'])
        left_knee = (joints[25]['x'], joints[25]['y'])
        left_heel = (joints[29]['x'], joints[29]['y'])
        left_angle = calculate_angle_from_coords(left_hip, left_knee, left_heel)
        
        # 右足の角度計算（腰-膝-かかと）
        right_hip = (joints[24]['x'], joints[24]['y'])
        right_knee = (joints[26]['x'], joints[26]['y'])
        right_heel = (joints[30]['x'], joints[30]['y'])
        right_angle = calculate_angle_from_coords(right_hip, right_knee, right_heel)
        
        # 平均角度
        avg_angle = (left_angle + right_angle) / 2
        
        knee_angles_by_frame[frame] = {
            'left_knee_angle': left_angle,
            'right_knee_angle': right_angle,
            'avg_knee_angle': avg_angle,
            'hip_y': avg_hip_y
        }
    
    return knee_angles_by_frame, hip_positions

def find_knee_angle_checkpoints(knee_angles_by_frame, min_distance=30, prominence=5):
    """膝角度が最小になるチェックポイントを検出"""
    frames = sorted(knee_angles_by_frame.keys())
    # 膝角度を負数にして、最小値を最大値として検出
    knee_values = [-knee_angles_by_frame[f]['avg_knee_angle'] for f in frames]
    
    # ピーク検出（膝角度の最小値 = 負数での最大値）
    peaks, properties = find_peaks(knee_values, 
                                  distance=min_distance,  # 最小間隔（フレーム数）
                                  prominence=prominence)   # 最小の角度変化（度）
    
    checkpoint_data = []
    for i in peaks:
        frame = frames[i]
        data = knee_angles_by_frame[frame]
        checkpoint_data.append((frame, data))
    
    print(f"🎯 検出されたチェックポイント数: {len(checkpoint_data)}")
    
    # 結果をフレーム番号順にソート
    checkpoint_data.sort(key=lambda x: x[0])
    
    return checkpoint_data

def evaluate_squat_quality(checkpoint_data):
    """スクワットの品質を評価"""
    if not checkpoint_data:
        print("❌ 評価するデータがありません")
        return
    
    print("\n🏆 スクワット品質評価結果 (膝角度ベース):")
    print("="*60)
    
    excellent_count = 0
    good_count = 0
    needs_improvement = 0
    
    for i, (frame, data) in enumerate(checkpoint_data, 1):
        angle = data['avg_knee_angle']
        left_angle = data['left_knee_angle']
        right_angle = data['right_knee_angle']
        
        if 75 <= angle <= 99:
            quality = "Excellent!! 🌟"
            excellent_count += 1
        elif 100 <= angle <= 159:
            quality = "Good! 👍"
            good_count += 1
        elif angle >= 160:
            quality = "もっと膝を曲げて 💪"
            needs_improvement += 1
        else:
            quality = "曲げすぎ注意 ⚠️"
            needs_improvement += 1
        
        print(f"{i:2d}回目: フレーム{frame:4d} - 平均{angle:5.1f}° (左{left_angle:.1f}°/右{right_angle:.1f}°) - {quality}")
    
    total = len(checkpoint_data)
    print(f"\n📊 まとめ:")
    print(f"Excellent: {excellent_count:2d}/{total} ({excellent_count/total*100:5.1f}%)")
    print(f"Good:      {good_count:2d}/{total} ({good_count/total*100:5.1f}%)")
    print(f"要改善:     {needs_improvement:2d}/{total} ({needs_improvement/total*100:5.1f}%)")
    
    # 平均値も計算
    avg_angle = sum(data['avg_knee_angle'] for _, data in checkpoint_data) / total
    min_angle = min(data['avg_knee_angle'] for _, data in checkpoint_data)
    max_angle = max(data['avg_knee_angle'] for _, data in checkpoint_data)
    
    print(f"\n📈 統計情報:")
    print(f"平均角度: {avg_angle:.1f}°")
    print(f"最小角度: {min_angle:.1f}°")
    print(f"最大角度: {max_angle:.1f}°")
    print(f"角度範囲: {max_angle - min_angle:.1f}°")

def visualize_knee_based_analysis(knee_angles_by_frame, hip_positions, checkpoint_data):
    """膝角度ベース分析結果を可視化"""
    frames = sorted(knee_angles_by_frame.keys())
    hip_values = [hip_positions[f] for f in frames]
    knee_values = [knee_angles_by_frame[f]['avg_knee_angle'] for f in frames]
    
    # チェックポイントのデータ
    checkpoint_frames = [frame for frame, _ in checkpoint_data]
    checkpoint_knee_angles = [data['avg_knee_angle'] for _, data in checkpoint_data]
    checkpoint_hip_values = [hip_positions[frame] for frame, _ in checkpoint_data]
    
    plt.figure(figsize=(15, 10))
    
    # 上段: 腰のY座標の変化
    plt.subplot(3, 1, 1)
    plt.plot(frames, hip_values, 'b-', linewidth=2, label='腰のY座標', alpha=0.7)
    plt.scatter(checkpoint_frames, checkpoint_hip_values, 
               color='red', s=100, zorder=5, label='膝角度最小点', marker='v')
    plt.xlabel('フレーム番号')
    plt.ylabel('腰のY座標')
    plt.title('🍑 腰の位置変化（参考）')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 中段: 膝角度の変化
    plt.subplot(3, 1, 2)
    plt.plot(frames, knee_values, 'g-', linewidth=2, label='膝角度', alpha=0.8)
    plt.scatter(checkpoint_frames, checkpoint_knee_angles, 
               color='red', s=120, zorder=5, label='チェックポイント', marker='o')
    
    # 評価基準ライン
    plt.axhspan(75, 99, alpha=0.2, color='gold', label='Excellent (75-99°)')
    plt.axhspan(100, 159, alpha=0.2, color='lightgreen', label='Good (100-159°)')
    plt.axhline(y=160, color='orange', linestyle='--', alpha=0.7, label='要改善ライン (160°)')
    
    plt.xlabel('フレーム番号')
    plt.ylabel('膝角度 (度)')
    plt.title('🦵 膝角度変化とチェックポイント検出')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 下段: 各チェックポイントでの膝角度（棒グラフ）
    plt.subplot(3, 1, 3)
    squat_numbers = list(range(1, len(checkpoint_data) + 1))
    
    # 色分け
    colors = []
    for angle in checkpoint_knee_angles:
        if 75 <= angle <= 99:
            colors.append('gold')  # Excellent
        elif 100 <= angle <= 159:
            colors.append('lightgreen')  # Good
        elif angle >= 160:
            colors.append('lightcoral')  # 要改善
        else:
            colors.append('lightblue')  # 曲げすぎ
    
    bars = plt.bar(squat_numbers, checkpoint_knee_angles, color=colors, alpha=0.8)
    
    # 評価基準ライン
    plt.axhspan(75, 99, alpha=0.15, color='gold', label='Excellent')
    plt.axhspan(100, 159, alpha=0.15, color='green', label='Good')
    
    plt.xlabel('スクワット回数')
    plt.ylabel('膝角度 (度)')
    plt.title('🎯 各チェックポイント（膝角度最小点）での評価')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 数値をバーの上に表示
    for bar, angle in zip(bars, checkpoint_knee_angles):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f'{angle:.1f}°', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.show()

def export_results(checkpoint_data, csv_file='squat_analysis_results.csv'):
    """分析結果をCSVファイルに出力"""
    try:
        with open(csv_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['squat_number', 'frame', 'avg_knee_angle', 'left_knee_angle', 
                           'right_knee_angle', 'evaluation'])
            
            for i, (frame, data) in enumerate(checkpoint_data, 1):
                angle = data['avg_knee_angle']
                
                if 75 <= angle <= 99:
                    evaluation = "Excellent"
                elif 100 <= angle <= 159:
                    evaluation = "Good"
                elif angle >= 160:
                    evaluation = "Needs_Improvement_Bend_More"
                else:
                    evaluation = "Needs_Improvement_Too_Much"
                
                writer.writerow([i, frame, data['avg_knee_angle'], 
                               data['left_knee_angle'], data['right_knee_angle'], evaluation])
        
        print(f"✅ 分析結果を '{csv_file}' に保存しました！")
    
    except Exception as e:
        print(f"❌ CSV出力エラー: {e}")

def main():
    """メイン処理"""
    print("🦵 膝角度ベース スクワット分析プログラム開始！")
    print("="*60)
    
    # CSVファイル名（必要に応じて変更してね！）
    csv_file = 'landmarks_user_squat.csv'
    
    # 1. データ読み込み
    landmark_data = load_user_landmarks(csv_file)
    if landmark_data is None:
        return
    
    # 2. 全フレームの膝角度計算
    knee_angles_by_frame, hip_positions = calculate_knee_angles_all_frames(landmark_data)
    if not knee_angles_by_frame:
        print("❌ 膝角度データが取得できませんでした")
        return
    
    print(f"📈 膝角度データ取得完了: {len(knee_angles_by_frame)}フレーム")
    
    # 3. 膝角度ベースでチェックポイント検出
    checkpoint_data = find_knee_angle_checkpoints(knee_angles_by_frame)
    if not checkpoint_data:
        print("❌ チェックポイントが検出できませんでした")
        print("💡 パラメーターを調整してください:")
        print("   - min_distance を小さくする（例: 20）")
        print("   - prominence を小さくする（例: 3）")
        return
    
    # 4. 品質評価
    evaluate_squat_quality(checkpoint_data)
    
    # 5. 結果の可視化
    visualize_knee_based_analysis(knee_angles_by_frame, hip_positions, checkpoint_data)
    
    # 6. 結果をCSVに出力
    export_results(checkpoint_data)
    
    print(f"\n🎉 膝角度ベース分析完了！{len(checkpoint_data)}回のスクワットを検出しました！")
    print(f"💪 これで一番正確なチェックポイントが分析できたね〜✨")

if __name__ == "__main__":
    main()