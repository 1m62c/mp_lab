import csv
import math
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from scipy.signal import find_peaks
from datetime import datetime
import warnings

# 警告メッセージを非表示
warnings.filterwarnings('ignore')
import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

# 日本語フォント設定（環境に応じて調整）
plt.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']

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

def calculate_knee_angles_all_frames(landmark_data, fps=30):
    """全フレームで膝角度を計算（時間軸付き）"""
    knee_angles_by_frame = {}
    hip_positions = {}
    
    for frame, joints in landmark_data.items():
        # 必要な関節が存在するかチェック
        required_joints = [23, 24, 25, 26, 29, 30]  # 左右の腰、膝、かかと
        if not all(joint_id in joints for joint_id in required_joints):
            continue
        
        # 時間軸計算
        time_sec = frame / fps
        
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
            'hip_y': avg_hip_y,
            'time_sec': time_sec
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
    """スクワットの品質を評価（統計情報も含む）"""
    if not checkpoint_data:
        print("❌ 評価するデータがありません")
        return {}
    
    print("\n🏆 スクワット品質評価結果:")
    print("="*60)
    
    evaluation_stats = {
        'excellent': 0,
        'good': 0,
        'bend_more': 0,
        'too_much': 0,
        'total': len(checkpoint_data),
        'angles': [],
        'evaluations': []
    }
    
    for i, (frame, data) in enumerate(checkpoint_data, 1):
        angle = data['avg_knee_angle']
        left_angle = data['left_knee_angle']
        right_angle = data['right_knee_angle']
        time_sec = data['time_sec']
        
        if 65 <= angle <= 89:
            quality = "Excellent!! 🌟"
            evaluation_stats['excellent'] += 1
            eval_category = 'Excellent'
        elif 90 <= angle <= 139:
            quality = "Good! 👍"
            evaluation_stats['good'] += 1
            eval_category = 'Good'
        elif angle >= 140:
            quality = "もっと膝を曲げて 💪"
            evaluation_stats['bend_more'] += 1
            eval_category = 'Bend More'
        else:
            quality = "曲げすぎ注意 ⚠️"
            evaluation_stats['too_much'] += 1
            eval_category = 'Too Much'
        
        evaluation_stats['angles'].append(angle)
        evaluation_stats['evaluations'].append(eval_category)
        
        print(f"{i:2d}回目: {time_sec:5.1f}秒 - 平均{angle:5.1f}° (左{left_angle:.1f}°/右{right_angle:.1f}°) - {quality}")
    
    # 統計情報計算
    total = evaluation_stats['total']
    avg_angle = sum(evaluation_stats['angles']) / total
    min_angle = min(evaluation_stats['angles'])
    max_angle = max(evaluation_stats['angles'])
    
    evaluation_stats.update({
        'avg_angle': avg_angle,
        'min_angle': min_angle,
        'max_angle': max_angle,
        'range_angle': max_angle - min_angle
    })
    
    print(f"\n📊 統計サマリー:")
    print(f"検知したスクワット回数: {total}回")
    print(f"Excellent: {evaluation_stats['excellent']:2d}回 ({evaluation_stats['excellent']/total*100:5.1f}%)")
    print(f"Good:      {evaluation_stats['good']:2d}回 ({evaluation_stats['good']/total*100:5.1f}%)")
    print(f"要改善:    {evaluation_stats['bend_more'] + evaluation_stats['too_much']:2d}回 ({(evaluation_stats['bend_more'] + evaluation_stats['too_much'])/total*100:5.1f}%)")
    print(f"平均角度: {avg_angle:.1f}° | 最小角度: {min_angle:.1f}° | 最大角度: {max_angle:.1f}°")
    
    return evaluation_stats

def create_simplified_report(knee_angles_by_frame, checkpoint_data, evaluation_stats):
    """シンプルで見やすいレポートグラフを作成"""
    # データ準備
    frames = sorted(knee_angles_by_frame.keys())
    time_values = [knee_angles_by_frame[f]['time_sec'] for f in frames]
    knee_values = [knee_angles_by_frame[f]['avg_knee_angle'] for f in frames]
    
    # チェックポイントのデータ
    checkpoint_times = [data['time_sec'] for _, data in checkpoint_data]
    checkpoint_angles = [data['avg_knee_angle'] for _, data in checkpoint_data]
    
    # 図全体の設定（上下分割レイアウト）
    fig = plt.figure(figsize=(14, 10))
    
    # 1. メイン時系列グラフ（上半分全体）
    ax1 = plt.subplot(2, 1, 1)
    
    # 背景色分け（より薄く）- 64度以下も赤に
    ax1.axhspan(0, 64, alpha=0.1, color='lightcoral', label='Too Much (0-64°)')
    ax1.axhspan(65, 89, alpha=0.1, color='gold', label='Excellent Zone (65-89°)')
    ax1.axhspan(90, 139, alpha=0.1, color='lightgreen', label='Good Zone (90-139°)')
    ax1.axhspan(140, 180, alpha=0.1, color='lightcoral', label='Needs Improvement (140°+)')
    
    # メインライン（太く）
    ax1.plot(time_values, knee_values, 'b-', linewidth=3, alpha=0.8, label='膝角度')
    
    # チェックポイントをハイライト
    colors_for_points = []
    for angle in checkpoint_angles:
        if 65 <= angle <= 89:
            colors_for_points.append('gold')
        elif 90 <= angle <= 139:
            colors_for_points.append('green')
        else:  # 140度以上 or 64度以下は赤
            colors_for_points.append('red')
    
    ax1.scatter(checkpoint_times, checkpoint_angles, 
               c=colors_for_points, s=150, zorder=5, 
               edgecolors='black', linewidth=2, label='スクワット ポイント')
    
    # 回数ラベル追加
    for i, (time, angle) in enumerate(zip(checkpoint_times, checkpoint_angles), 1):
        ax1.annotate(f'{i}', (time, angle), xytext=(0, 20), 
                    textcoords='offset points', ha='center', va='bottom',
                    fontweight='bold', fontsize=12, color='white',
                    bbox=dict(boxstyle='circle,pad=0.3', facecolor='black', alpha=0.8))
    
    # 軸の設定（グラフ開始位置に合わせて調整）
    min_time = min(time_values)
    max_time = max(time_values)
    time_margin = (max_time - min_time) * 0.02  # 2%のマージン
    ax1.set_xlim(min_time - time_margin, max_time + time_margin)
    ax1.set_ylim(0, 180)
    ax1.set_xlabel('経過時間(秒)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('膝角度 (°)', fontsize=12, fontweight='bold')
    ax1.set_title('膝角度の時系列変化', fontsize=16, fontweight='bold', pad=15)
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    
    # 2. 評価割合 円グラフ（下段左）
    ax2 = plt.subplot(2, 2, 3)
    
    labels = []
    sizes = []
    colors = []
    legend_labels = []
    
    if evaluation_stats['excellent'] > 0:
        labels.append(f"Excellent\n{evaluation_stats['excellent']}回")
        sizes.append(evaluation_stats['excellent'])
        colors.append('#FFD700')  # ゴールド
        legend_labels.append('Excellent (65-89°)')
    
    if evaluation_stats['good'] > 0:
        labels.append(f"Good\n{evaluation_stats['good']}回")
        sizes.append(evaluation_stats['good'])
        colors.append('#90EE90')  # ライトグリーン
        legend_labels.append('Good (90-139°)')
    
    improvement_count = evaluation_stats['bend_more'] + evaluation_stats['too_much']
    if improvement_count > 0:
        labels.append(f"要改善\n{improvement_count}回")
        sizes.append(improvement_count)
        colors.append('#FFB6C1')  # ライトピンク
        legend_labels.append('要改善 (140°+)')
    
    if sizes:  # データがある場合のみ描画
        wedges, texts, autotexts = ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                          startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
        
        # パーセンテージの色を白に
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(12)
    
    ax2.set_title('評価分布', fontsize=16, fontweight='bold', pad=15)
    
    # 凡例を円グラフの右横に追加
    legend_colors = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=12) for color in colors]
    ax2.legend(legend_colors, legend_labels, loc='center left', bbox_to_anchor=(1.0, 0.5), fontsize=10)
    
    # 3. 統計サマリー（下段右、タイトルなし）
    ax3 = plt.subplot(2, 2, 4)
    ax3.axis('off')
    
    # 統計サマリーテキスト（簡略化・記号なし）
    stats_text = f"""検知したスクワット回数: {evaluation_stats['total']}回

Excellent: {evaluation_stats['excellent']}回 ({evaluation_stats['excellent']/evaluation_stats['total']*100:.1f}%)
Good: {evaluation_stats['good']}回 ({evaluation_stats['good']/evaluation_stats['total']*100:.1f}%)
要改善: {improvement_count}回 ({improvement_count/evaluation_stats['total']*100:.1f}%)

角度統計:
  平均: {evaluation_stats['avg_angle']:.1f}°
  最小: {evaluation_stats['min_angle']:.1f}°
  最大: {evaluation_stats['max_angle']:.1f}°
   
トレーニング時間: {max(time_values):.1f}秒"""
    
    # 統計テキストを中央に配置
    ax3.text(0.5, 0.5, stats_text, transform=ax3.transAxes, fontsize=11,
            verticalalignment='center', horizontalalignment='center',
            bbox=dict(boxstyle='round,pad=1', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.4, wspace=0.3)  # 間隔調整
    
    # 現在時刻でファイル名生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"squat_report_simplified_{timestamp}.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"📊 レポートを '{filename}' に保存しました！")
    
    plt.show()

def export_detailed_results(checkpoint_data, evaluation_stats, csv_file='squat_results.csv'):
    """詳細な分析結果をCSVファイルに出力"""
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # ヘッダー
            writer.writerow(['squat_number', 'time_sec', 'frame', 'avg_knee_angle', 'left_knee_angle', 
                           'right_knee_angle', 'evaluation', 'evaluation_score'])
            
            # データ
            for i, (frame, data) in enumerate(checkpoint_data, 1):
                angle = data['avg_knee_angle']
                time_sec = data['time_sec']
                
                if 65 <= angle <= 89:
                    evaluation = "Excellent"
                    score = 4
                elif 90 <= angle <= 139:
                    evaluation = "Good" 
                    score = 3
                elif angle >= 140:
                    evaluation = "Bend_More"
                    score = 2
                else:
                    evaluation = "Too_Much"
                    score = 1
                
                writer.writerow([i, f"{time_sec:.1f}", frame, f"{data['avg_knee_angle']:.1f}", 
                               f"{data['left_knee_angle']:.1f}", f"{data['right_knee_angle']:.1f}", 
                               evaluation, score])
            
            # 統計サマリーも追加
            writer.writerow([])  # 空行
            writer.writerow(['=== SUMMARY STATISTICS ==='])
            writer.writerow(['Total Squats', evaluation_stats['total']])
            writer.writerow(['Excellent Count', evaluation_stats['excellent']])
            writer.writerow(['Good Count', evaluation_stats['good']])
            writer.writerow(['Needs Improvement', evaluation_stats['bend_more'] + evaluation_stats['too_much']])
            writer.writerow(['Average Angle', f"{evaluation_stats['avg_angle']:.1f}"])
            writer.writerow(['Min Angle', f"{evaluation_stats['min_angle']:.1f}"])
            writer.writerow(['Max Angle', f"{evaluation_stats['max_angle']:.1f}"])
        
        print(f"✅ 詳細結果を '{csv_file}' に保存しました！")
    
    except Exception as e:
        print(f"❌ CSV出力エラー: {e}")

def main():
    """メイン処理"""
    print("🏋️‍♀️ スクワット トレーニング レポート システム開始！")
    print("="*60)
    
    # CSVファイル名（必要に応じて変更）
    csv_file = 'user_squat.csv'
    
    # フレームレート設定（動画に合わせて調整）
    fps = 30  # 1秒間のフレーム数
    
    # 1. データ読み込み
    landmark_data = load_user_landmarks(csv_file)
    if landmark_data is None:
        return
    
    # 2. 全フレームの膝角度計算（時間軸付き）
    knee_angles_by_frame, hip_positions = calculate_knee_angles_all_frames(landmark_data, fps)
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
    
    # 4. 品質評価と統計
    evaluation_stats = evaluate_squat_quality(checkpoint_data)
    
    # 5. シンプルなレポート作成
    create_simplified_report(knee_angles_by_frame, checkpoint_data, evaluation_stats)
    
    # 6. 詳細結果をCSVに出力
    export_detailed_results(checkpoint_data, evaluation_stats)
    
    print(f"\n🎉 レポート作成完了！{evaluation_stats['total']}回のスクワットを分析しました！")

if __name__ == "__main__":
    main()