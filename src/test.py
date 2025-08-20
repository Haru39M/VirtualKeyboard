import cv2
import mediapipe as mp

# MediaPipeのモジュール初期化
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Webカメラを開く
# cap = cv2.VideoCapture(0)
file_path = "../testYOLO/video03.mp4"
cap = cv2.VideoCapture(file_path)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

fps = cap.get(cv2.CAP_PROP_FPS)
out_file = "out.mp4"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(out_file,fourcc,fps,(width,height),True)
# MediaPipe Hands 初期化
with mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
) as hands:

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("カメラが読み込めませんでした")
            break
            # continue
        # frame = cv2.resize(frame,(int(width/2),int(height/2)))

        # OpenCVはBGR、MediaPipeはRGBなので変換
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame.flags.writeable = False  # 高速化のために書き込み不可に

        # 手の検出
        results = hands.process(frame)

        # 描画のために再びBGRに変換
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # ランドマークの描画
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

        # ウィンドウ表示
        cv2.imshow('Hand Tracking', frame)
        out.write(frame)

        # ESCキーで終了
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# 終了処理
cap.release()
out.release()
cv2.destroyAllWindows()