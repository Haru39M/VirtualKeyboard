import cv2
import time
import threading

class WebcamVideoStream:
    def __init__(self, src=0, width=1280, height=720, fps=30):
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened(): #
            raise IOError("Webカメラを開けませんでした。")

        # カメラ設定を適用
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG')) #
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width) #
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height) #
        self.stream.set(cv2.CAP_PROP_FPS, fps) #

        # 露出・フォーカス設定 (元のコードの設定を反映)
        self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)  # manual mode とコメントがありますが、1は自動モードの可能性が高いです
        self.stream.set(cv2.CAP_PROP_AUTOFOCUS, 1) #

        # 自動露出を無効化 (必要に応じてコメント解除)
        # self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0) #
        # self.stream.set(cv2.CAP_PROP_EXPOSURE, -6) #

        # オートフォーカスを無効化 (必要に応じてコメント解除)
        # self.stream.set(cv2.CAP_PROP_AUTOFOCUS, 0) #
        # self.stream.set(cv2.CAP_PROP_FOCUS, 480) #

        # 最初のフレームを読み込んでおく
        (self.grabbed, self.frame) = self.stream.read() #
        self.stopped = False
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True

    def start(self):
        self.stopped = False
        self.thread.start()
        # カメラの初期化と最初のフレーム取得のために少し待つ
        time.sleep(1.0) # スレッドがフレームを更新し始めるのを待つ
        return self

    def update(self):
        while not self.stopped:
            (grabbed, frame) = self.stream.read()
            if not grabbed:
                print("ストリームの終端またはエラー。スレッドを停止します。")
                self.stop() # エラーや終端で自身を停止
                break
            self.frame = frame

    def read(self):
        # 最新のフレームを返す
        return self.frame

    def stop(self):
        self.stopped = True
        if self.thread.is_alive():
             self.thread.join(timeout=1.0) # スレッドが終了するのを待つ (タイムアウト付き)
        if self.stream.isOpened(): # ストリームがまだ開いているか確認
            self.stream.release()
        print("Webカメラリソースを解放しました。")

    def get_actual_props(self):
        width = int(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)) #
        height = int(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)) #
        fps = self.stream.get(cv2.CAP_PROP_FPS) #
        return width, height, fps

# --- メインのFPS計測処理 ---
REQUESTED_WIDTH = 640 * 2 #
REQUESTED_HEIGHT = 360 * 2 #
REQUESTED_FPS = 30 #

# WebcamVideoStream を使用してカメラを初期化
vs = WebcamVideoStream(src=0, width=REQUESTED_WIDTH, height=REQUESTED_HEIGHT, fps=REQUESTED_FPS)
vs.start()

# 実際のカメラ解像度を取得
actual_width, actual_height, actual_fps = vs.get_actual_props()
print(f"要求カメラ設定: {REQUESTED_WIDTH}x{REQUESTED_HEIGHT} @ {REQUESTED_FPS} FPS")
print(f"実カメラ設定: {actual_width}x{actual_height} @ {actual_fps} FPS")

if actual_width == 0 or actual_height == 0:
    print("カメラから有効な解像度を取得できませんでした。終了します。")
    vs.stop()
    exit()

N = 500 # 計測フレーム数を増やすとより安定した平均値が得られます
print(f"{N}フレームの読み取り時間を計測します...")

# 最初の数フレームはカメラのウォームアップやスレッドの安定のためにスキップする (任意)
# for _ in range(10):
#    frame = vs.read()
#    if frame is None:
#        time.sleep(0.01) # フレームがまだ準備できていない場合

frames_read = 0
start_t = time.perf_counter()

for i in range(N):
    frame = vs.read()
    if frame is None:
        print(f"フレーム {i+1} の取得に失敗しました。計測を中断します。")
        break
    frames_read += 1
    # ここでフレームに対する処理（例: MediaPipeなど）を行うこともできますが、
    # 今回は純粋な読み込み速度を計測します。
    # cv2.imshow("Frame", frame) # 表示するとFPSに影響する可能性あり
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #    break

end_t = time.perf_counter()

if frames_read > 0:
    total_time = end_t - start_t
    ave_time = total_time / frames_read
    measured_fps = 1 / ave_time
    print(f"計測完了: {frames_read} フレーム")
    print(f"合計時間(s) = {total_time:.4f}")
    print(f"平均フレーム時間(s) = {ave_time:.6f}") #
    print(f"計測FPS = {measured_fps:.2f}") #
else:
    print("フレームを1つも読み取れませんでした。")

# 終了処理
vs.stop() #
cv2.destroyAllWindows() #