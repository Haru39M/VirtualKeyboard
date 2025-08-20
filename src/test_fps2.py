import cv2
import mediapipe as mp
import time

# MediaPipeのモジュール初期化
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Webカメラを開く
cap = cv2.VideoCapture(0,cv2.CAP_V4L2)#あってもなくてもあんま変わらん
# cap = cv2.VideoCapture(0)

time.sleep(0.1)

# cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)#これをいれるとなぜかFPS下がる
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))#なんか一列になる。デコードが必要?
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))#遅い。
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))#圧縮してFPSを上げる

cap.set(cv2.CAP_PROP_FPS, 30)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640*2)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360*2)

time.sleep(0.1)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
print(f"カメラ解像度: {width}x{height}")


#自動露出、オートフォーカスを有効化(リセット)
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # auto mode
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
time.sleep(0.1)

exposure = cap.get(cv2.CAP_PROP_EXPOSURE)
focus = cap.get(cv2.CAP_PROP_FOCUS)

# 自動露出を無効化
cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)  # manual mode
cap.set(cv2.CAP_PROP_EXPOSURE, exposure)  # 固定露出値

# # オートフォーカスを無効化
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FOCUS, focus)  # 固定フォーカス値

time.sleep(0.1)

# fps = cap.get(cv2.CAP_PROP_FPS)
# out_file = "out.mp4"
# fourcc = cv2.VideoWriter_fourcc(*'mp4v')
# out = cv2.VideoWriter(out_file,fourcc,fps,(width,height),True)

print(f"focus={focus},exposure={exposure}")
time.sleep(4)

start_t = time.perf_counter()
N=100
for i in range(N):
    if cap.isOpened():
        # print("read")
        success, frame = cap.read()
        if not success:
            print("カメラが読み込めませんでした")
            break
    else:
        break
end_t = time.perf_counter()
ave_time = (end_t-start_t)/N
print(f"ave time(s) = {ave_time}")
print(f"FPS = {1/ave_time}")
# 終了処理
cap.release()
# out.release()
cv2.destroyAllWindows()