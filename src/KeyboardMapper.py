import numpy as np
import cv2
class KeyboardMapper:
    def __init__(self, keyboard, camera_corners):
        self.keyboard = keyboard
        self.camera_corners = np.array(camera_corners, dtype=np.float32)
        
        # # キーボードの正規化座標での4角
        # self.keyboard_corners = np.array([
        #     [0.0, 0.0],      # 左上
        #     [1.0, 0.0],      # 右上
        #     [1.0, 1.0],      # 右下
        #     [0.0, 1.0]       # 左下
        # ], dtype=np.float32)

        # キーボードの正規化座標での4角（幅基準の正規化）
        # keymap2coordinate.py の normalize() の仕様に合わせる
        keyboard_h_normalized = self.keyboard.height / self.keyboard.width
        self.keyboard_norm_corners = np.array([
            [0.0, 0.0],                      # 左上
            [1.0, 0.0],                      # 右上
            [1.0, keyboard_h_normalized],    # 右下
            [0.0, keyboard_h_normalized]     # 左下
        ], dtype=np.float32)
        
        # # ホモグラフィ行列を計算
        # self.homography_matrix = cv2.getPerspectiveTransform(
        #     self.keyboard_corners, self.camera_corners
        # )

        # カメラ座標 -> キーボード正規化座標 への変換行列
        self.inv_homography_matrix = cv2.getPerspectiveTransform(
            self.camera_corners, self.keyboard_norm_corners
        )
    
    # def transform_point(self, x, y):
    #     """正規化座標をカメラ座標に変換"""
    #     point = np.array([[[x, y]]], dtype=np.float32)
    #     transformed = cv2.perspectiveTransform(point, self.homography_matrix)
    #     return int(transformed[0][0][0]), int(transformed[0][0][1])
    
    def _transform_cam_to_norm(self, px, py):
        """カメラ座標の点をキーボードの正規化座標に変換"""
        point = np.array([[[px, py]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(point, self.inv_homography_matrix)
        return transformed[0][0]
    
    def get_key_for_point(self, px, py):
        """カメラ座標(px, py)上にあるキーオブジェクトを返す"""
        nx, ny = self._transform_cam_to_norm(px, py)
        
        for key in self.keyboard.keys:
            if key.x <= nx < key.x + key.width and key.y <= ny < key.y + key.height:
                return key
        return None
    
    def draw_keyboard_and_finger_info(self, frame, finger_positions=None):
        """キーボードの枠線を描画し、指とキーのマッピング情報を描画・出力する"""
        
        # --- 1. キーボードの枠線を描画 ---
        pts = self.camera_corners.astype(np.int32).reshape((-1, 1, 2))
        cv2.polylines(frame, [pts], True, (255, 255, 0), 1)

        # 各キーを描画
        for key in self.keyboard.keys:
            # キーの4角を変換
            top_left = self._transform_cam_to_norm(key.x, key.y)
            top_right = self._transform_cam_to_norm(key.x + key.width, key.y)
            bottom_right = self._transform_cam_to_norm(key.x + key.width, key.y + key.height)
            bottom_left = self._transform_cam_to_norm(key.x, key.y + key.height)
            
            top_left = (10,10)
            top_right = (20,10)
            bottom_left = (10,20)
            bottom_right = (20,20)
            # キーの枠色を決定
            color = (0, 0, 255)  # デフォルトは赤
            
            # # 人差し指がキー内にあるかチェック
            # for finger_x, finger_y in index_fingers:
            #     if self.is_point_in_key(finger_x, finger_y, key):
            #         color = (0, 255, 0)  # 緑
            #         break
            
            # キーを描画（ポリゴンとして描画）
            pts = np.array([top_left, top_right, bottom_right, bottom_left], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, color, 1)

        if not finger_positions:
            return

        # --- 2. 各指がどのキー上にあるか判定し、描画とコンソール出力 ---
        finger_names = {
            4: "Thumb", 8: "Index", 12: "Middle", 16: "Ring", 20: "Pinky"
        }
        
        # コンソールをクリア (見やすくするため)
        # import os
        # os.system('cls' if os.name == 'nt' else 'clear')

        for hand in finger_positions:
            hand_label = hand['label']
            print(f"--- {hand_label} Hand ---")
            
            for tip_id, x, y in hand['fingers']:
                key = self.get_key_for_point(x, y)
                finger_name = finger_names.get(tip_id, "Unknown")

                if key:
                    # コンソールに出力
                    print(f"  {finger_name.ljust(6)}: {key.keycode}")

                    # 画面に描画
                    text = f"{finger_name}: {key.keycode}"
                    cv2.putText(frame, text, (x, y - 10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
        print("--------------------")
    
    # def is_point_in_key(self, px, py, key):
    #     """点がキー内にあるかチェック"""
    #     # キーの4角を変換
    #     key_corners = [
    #         self.transform_point(key.x, key.y),
    #         self.transform_point(key.x + key.width, key.y),
    #         self.transform_point(key.x + key.width, key.y + key.height),
    #         self.transform_point(key.x, key.y + key.height)
    #     ]
        
    #     # 点がポリゴン内にあるかチェック
    #     contour = np.array(key_corners)
    #     return cv2.pointPolygonTest(contour, (px, py), False) >= 0
    
    # def draw_keyboard(self, frame, finger_positions=None):
    #     """キーボードを描画"""
    #     # 人差し指の座標を取得（複数の手に対応）
    #     index_fingers = []
    #     if finger_positions:
    #         for hand in finger_positions:
    #             for tip_id, x, y in hand['fingers']:
    #                 if tip_id == 8:  # 人差し指
    #                     index_fingers.append((x, y))
        
    #     # 各キーを描画
    #     for key in self.keyboard.keys:
    #         # キーの4角を変換
    #         top_left = self.transform_point(key.x, key.y)
    #         top_right = self.transform_point(key.x + key.width, key.y)
    #         bottom_right = self.transform_point(key.x + key.width, key.y + key.height)
    #         bottom_left = self.transform_point(key.x, key.y + key.height)
            
    #         # キーの枠色を決定
    #         color = (0, 0, 255)  # デフォルトは赤
            
    #         # 人差し指がキー内にあるかチェック
    #         for finger_x, finger_y in index_fingers:
    #             if self.is_point_in_key(finger_x, finger_y, key):
    #                 color = (0, 255, 0)  # 緑
    #                 break
            
    #         # キーを描画（ポリゴンとして描画）
    #         pts = np.array([top_left, top_right, bottom_right, bottom_left], np.int32)
    #         pts = pts.reshape((-1, 1, 2))
    #         cv2.polylines(frame, [pts], True, color, 1)
            
    #         # キーコードを描画
    #         # center_x = (top_left[0] + bottom_right[0]) // 2
    #         # center_y = (top_left[1] + bottom_right[1]) // 2
    #         # cv2.putText(frame, key.keycode, (center_x - 10, center_y + 5),
    #         #            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)