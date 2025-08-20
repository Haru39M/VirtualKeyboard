from keymap2coordinate2 import loadKeyBoard # ユーザーの環境に存在することを前提とします
import cv2
import mediapipe as mp
import numpy as np
from KeyboardMapper import KeyboardMapper # KeyboardMapper.py からインポート
import threading
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
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        results = self.hands.process(rgb_frame)
        rgb_frame.flags.writeable = True # 後でフレームを再利用する場合
        return results
    
    def get_finger_positions(self, results, width, height):
        finger_positions = []
        if results.multi_handedness and results.multi_hand_landmarks:
            for i in range(len(results.multi_hand_landmarks)):
                hand_landmarks = results.multi_hand_landmarks[i]
                handedness = results.multi_handedness[i]
                label = handedness.classification[0].label
                if label == "Left":
                    label = "Right"
                else:
                    label = "Left"
                
                finger_tips = [4, 8, 12, 16, 20]
                hand_fingers = []
                for tip_id in finger_tips:
                    landmark = hand_landmarks.landmark[tip_id]
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    hand_fingers.append((tip_id, x, y))
                
                finger_positions.append({
                    'label': label,
                    'landmarks': hand_landmarks, # 描画用に正規化座標を保持
                    'fingers': hand_fingers
                })
        return finger_positions
    
    def draw_landmarks(self, frame, results):
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

class WebcamVideoStream:
    def __init__(self, src=0, width=1280, height=720, fps=30):
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            raise IOError("Webカメラを開けませんでした。")

        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.stream.set(cv2.CAP_PROP_FPS, fps)
        
        # 露出・フォーカス設定 (現状のものを維持)
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1) 
        self.stream.set(cv2.CAP_PROP_AUTOFOCUS, 1)
        # 必要に応じて固定値を設定
        # self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
        # self.stream.set(cv2.CAP_PROP_EXPOSURE, -5) 
        self.stream.set(cv2.CAP_PROP_AUTOFOCUS, 0)
        self.stream.set(cv2.CAP_PROP_FOCUS, 400)

        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True

    def start(self):
        self.stopped = False
        self.thread.start()
        # カメラの初期化と最初のフレーム取得のために少し待つ
        time.sleep(1.0) 
        return self

    def update(self):
        while not self.stopped:
            (grabbed, frame) = self.stream.read()
            if not grabbed:
                print("ストリームの終端またはエラー。スレッドを停止します。")
                self.stop() # エラーや終端で自身を停止
                break
            self.frame = frame # grabbed フラグはここでは不要、常に最新フレームを保持

    def read(self):
        return self.frame # 最新のフレームを返す

    def stop(self):
        self.stopped = True
        if self.thread.is_alive():
             self.thread.join(timeout=1.0) # スレッドが終了するのを待つ (タイムアウト付き)
        self.stream.release()
        print("Webカメラリソースを解放しました。")

    def get_actual_props(self):
        width = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.stream.get(cv2.CAP_PROP_FPS)
        focus = self.stream.get(cv2.CAP_PROP_FOCUS) # 起動直後のフォーカス値を取得
        return width, height, fps, focus

def main():
    KEYBOARD_CORNERS = [
        [10, 20], [642, 20], [598, 215], [51, 215]
    ]
    
    # ユーザーの環境に合わせて keymap2.xml を用意してください
    try:
        keyboard = loadKeyBoard("keymap2.xml")
        keyboard.normalize()
    except Exception as e:
        print(f"キーボードデータの読み込みに失敗しました: {e}")
        print("ダミーキーボードデータを使用します。")
        # ダミーのキーボードデータ (もし loadKeyBoard が失敗した場合)
        class DummyKey:
            def __init__(self, x, y, width, height, keycode):
                self.x, self.y, self.width, self.height, self.keycode = x, y, width, height, keycode
        class DummyKeyboard:
            def __init__(self): self.keys = [DummyKey(0.1,0.1,0.1,0.1,"A")]
            def normalize(self): pass
        keyboard = DummyKeyboard()


    hand_tracker = HandTracker()
    keyboard_mapper = KeyboardMapper(keyboard, KEYBOARD_CORNERS)
    
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 360
    REQUESTED_FPS = 30
    
    vs = WebcamVideoStream(src=0, width=FRAME_WIDTH, height=FRAME_HEIGHT, fps=REQUESTED_FPS).start()
    
    actual_width, actual_height, actual_fps, initial_focus = vs.get_actual_props()
    print(f"要求カメラ設定: {FRAME_WIDTH}x{FRAME_HEIGHT} @ {REQUESTED_FPS} FPS")
    print(f"実カメラ設定: {actual_width}x{actual_height} @ {actual_fps} FPS")
    print(f"初期フォーカス値 (参考): {initial_focus}")

    if actual_width == 0 or actual_height == 0:
        print("カメラから有効な解像度を取得できませんでした。終了します。")
        vs.stop()
        return

    try:
        while not vs.stopped: # スレッドが停止していない間ループ
            frame = vs.read()
            if frame is None:
                # print("フレームを取得できませんでした。スキップします。")
                time.sleep(0.01) # 少し待機
                continue
            
            # フォーカス値の確認 (デバッグ用、頻繁な呼び出しは避ける)
            # current_focus = vs.stream.get(cv2.CAP_PROP_FOCUS) 
            # print(f"現在のフォーカス値: {current_focus}")

            frame = cv2.flip(frame, flipCode=-1)
            
            results = hand_tracker.process_frame(frame)
            # get_finger_positions に渡すのは、描画対象のフレームの解像度
            finger_positions = hand_tracker.get_finger_positions(results, actual_width, actual_height) 
            
            hand_tracker.draw_landmarks(frame, results) # results内の正規化座標で描画
            
            for hand in finger_positions:
                for tip_id, x, y in hand['fingers']:
                    if tip_id == 8: # 人差し指
                        cv2.putText(frame, f"{x},{y}", (x-20, y-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        
            #=======================================================================
            
            keyboard_mapper.draw_keyboard(frame, finger_positions)
            
            keyboard_corners_np = np.array(KEYBOARD_CORNERS, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [keyboard_corners_np], True, (255, 255, 0), 1)
            
            cv2.imshow('Hand Tracking with Virtual Keyboard', frame)
            
            # waitKeyの値を小さくして、より多くのフレームを処理できるようにする
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    finally:
        print("メインループ終了処理を開始します。")
        vs.stop()
        cv2.destroyAllWindows()
        print("すべてのリソースを解放し、ウィンドウを閉じました。")

if __name__ == "__main__":
    main()