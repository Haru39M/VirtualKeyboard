from keymap2coordinate2 import loadKeyBoard
import cv2
import mediapipe as mp
import numpy as np
from KeyboardMapper import KeyboardMapper # KeyboardMapper.py からインポート
import time

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
    
    def process_frame(self, frame):
        """フレームを処理して手の検出結果を返す"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)
        return results
    
    def get_finger_positions(self, results, width, height):
        """指先の座標を取得"""
        finger_positions = []
        
        if results.multi_handedness and results.multi_hand_landmarks:
            for i in range(len(results.multi_hand_landmarks)):
                hand_landmarks = results.multi_hand_landmarks[i]
                handedness = results.multi_handedness[i]
                
                # ラベル判定の修正（元コードの逆転処理を維持）
                label = handedness.classification[0].label
                if label == "Left":
                    label = "Right"
                else:
                    label = "Left"
                
                # 指先の座標を取得 (指の先端のランドマークIDは4, 8, 12, 16, 20)
                finger_tips = [4, 8, 12, 16, 20]
                hand_fingers = []
                
                for tip_id in finger_tips:
                    landmark = hand_landmarks.landmark[tip_id]
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    hand_fingers.append((tip_id, x, y))
                
                finger_positions.append({
                    'label': label,
                    'landmarks': hand_landmarks,
                    'fingers': hand_fingers
                })
        
        return finger_positions
    
    def draw_landmarks(self, frame, results):
        """ランドマークを描画"""
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )



def main():
    # print(cv2.getBuildInformation())#ビルド情報を確認

    # キーボードの4角座標をベタ書き（カメラ画面内の座標）
    # 形式: [左上, 右上, 右下, 左下]
    KEYBOARD_CORNERS = [
        [10, 20],  # 左上
        [642, 20],  # 右上
        [598, 215],  # 右下
        [51, 215]   # 左下
    ]
    
    # キーボードデータを読み込み
    keyboard = loadKeyBoard("keymap2.xml")
    keyboard.normalize()
    
    # 各種クラスを初期化
    hand_tracker = HandTracker()
    keyboard_mapper = KeyboardMapper(keyboard, KEYBOARD_CORNERS)
    
    # Webカメラを開く
    cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
    time.sleep(0.1)

    # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640*2)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360*2)

    time.sleep(0.1)

    actual_fourcc_int = int(cap.get(cv2.CAP_PROP_FOURCC))
    print(f"Requested FOURCC: H264, Actual FOURCC from cam: '{fourcc}' (int: {hex(actual_fourcc_int)})")
    
    exit()

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"カメラ解像度: {width}x{height}")

    #自動露出、オートフォーカスを有効化(リセット)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # auto mode
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

    time.sleep(2)

    exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
    focus = cap.get(cv2.CAP_PROP_FOCUS)
    print(f"got focus={focus},exposure={exposure}")

    # # 自動露出を無効化
    # cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # manual mode
    # cap.set(cv2.CAP_PROP_EXPOSURE, exposure)  # 固定露出値

    # オートフォーカスを無効化
    # cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    # cap.set(cv2.CAP_PROP_FOCUS, focus)  # 固定フォーカス値

    time.sleep(0.1)

    print(f"setting focus={focus},exposure={exposure}")

    exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
    focus = cap.get(cv2.CAP_PROP_FOCUS)
    print(f"setted focus={focus},exposure={exposure}")
    time.sleep(3)

    try:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("カメラが読み込めませんでした")
                break
            
            # print(cap.get(cv2.CAP_PROP_FOCUS))
            # フレームを上下左右反転
            # frame = cv2.flip(frame, flipCode=-1)
            
            # 手の検出
            results = hand_tracker.process_frame(frame)
            
            # 指の座標を取得
            finger_positions = hand_tracker.get_finger_positions(results, width, height)
            
            # ランドマークを描画
            hand_tracker.draw_landmarks(frame, results)
            
            # 人差し指の座標を表示
            for hand in finger_positions:
                for tip_id, x, y in hand['fingers']:
                    if tip_id == 8:  # 人差し指
                        cv2.putText(frame, f"{x},{y}", (x-20, y-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # キーボードを描画
            keyboard_mapper.draw_keyboard(frame, finger_positions)
            
            # キーボード領域の枠を描画（参考用）
            keyboard_corners = np.array(KEYBOARD_CORNERS, np.int32)
            keyboard_corners = keyboard_corners.reshape((-1, 1, 2))
            cv2.polylines(frame, [keyboard_corners], True, (255, 255, 0), 1)
            
            # ウィンドウ表示
            cv2.imshow('Hand Tracking with Virtual Keyboard', frame)
            
            # ESCキーで終了
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
    
    finally:
        # 終了処理
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()