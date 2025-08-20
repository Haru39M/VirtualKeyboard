from keymap2coordinate import loadKeyBoard
import cv2
import mediapipe as mp

# MediaPipeのモジュール初期化
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

"""
使える解像度(anker powerconf c200)
[0]: 'MJPG' (Motion-JPEG, compressed)
        Size: Discrete 2560x1440
                Interval: Discrete 0.033s (30.000 fps)
        Size: Discrete 1920x1080
                Interval: Discrete 0.033s (30.000 fps)
        Size: Discrete 1280x720
                Interval: Discrete 0.033s (30.000 fps)
        Size: Discrete 640x480
                Interval: Discrete 0.033s (30.000 fps)
        Size: Discrete 640x360
                Interval: Discrete 0.033s (30.000 fps)
        Size: Discrete 320x240
                Interval: Discrete 0.033s (30.000 fps)
"""

# Webカメラを開く
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(width, height)

keyboard = loadKeyBoard("keymap.xml")
keyboard.normalize()
for key in keyboard.keys:
    print(key)
# exit()

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

        # OpenCVはBGR、MediaPipeはRGBなので変換
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame,flipCode=-1)#上下左右反転
        frame.flags.writeable = False  # 高速化のために書き込み不可に

        # 手の検出
        results = hands.process(frame)

        # 描画のために再びBGRに変換
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        # ランドマークの描画と座標取得
        if results.multi_handedness and results.multi_hand_landmarks:
            for i in range(len(results.multi_hand_landmarks)):
                handedness = results.multi_handedness[i]
                hand_landmarks = results.multi_hand_landmarks[i]

                label = handedness.classification[0].label  # "Left" or "Right"
                #なんか判定が逆だったので入れ替える
                if label == "Left":
                    label = "Right"
                else:
                    label = "Left"
                print(f"Hand label: {label}")

                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                # 指先の座標を取得 (指の先端のランドマークIDは4, 8, 12, 16, 20)
                finger_tips = [4, 8, 12, 16, 20]

                for tip_id in finger_tips:
                    x, y = hand_landmarks.landmark[tip_id].x * width, hand_landmarks.landmark[tip_id].y * height
                    # 指先の座標をフレームに書き込む
                    # cv2.putText(frame, str(tip_id), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                    if tip_id == 8:
                        cv2.putText(frame, f"{int(x)},{int(y)}", org=(int(x)-20, int(y)-10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, color=(0, 0, 255), thickness=2)
                        #判定領域の描画(テスト)
                        mid = (100,100)
                        size = (40,30)
                        pt1 = (mid[0]-int(size[0]/2),mid[1]-int(size[1]/2))
                        pt2 = (mid[0]+int(size[0]/2),mid[1]+int(size[1]/2))
                        if (pt1[0] < x < pt2[0]) and (pt1[1] < y < pt2[1]):
                            cv2.rectangle(frame,pt1,pt2,(0, 255, 0),thickness=2)
                        else:
                            cv2.rectangle(frame,pt1,pt2,(0, 0, 255),thickness=2)
                    print(f"指先{tip_id}の座標: ({int(x)}, {int(y)})")
                    # キーを描画
        scale = width
        for key in keyboard.keys:
            cv2.rectangle(frame,(int(scale * key.x),int(scale * key.y)),(int(scale * (key.x+key.width)),int(scale * (key.y+key.height))),(0,0,255),thickness=1)
        # ウィンドウ表示
        cv2.imshow('Hand Tracking', frame)

        # ESCキーで終了
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# 終了処理
cap.release()
cv2.destroyAllWindows()
