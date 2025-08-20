import numpy as np
import cv2
class KeyboardMapper:
    def __init__(self, keyboard, camera_corners):
        self.keyboard = keyboard
        self.camera_corners = np.array(camera_corners, dtype=np.float32)
        
        # キーボードの正規化座標での4角
        self.keyboard_corners = np.array([
            [0.0, 0.0],      # 左上
            [1.0, 0.0],      # 右上
            [1.0, 1.0],      # 右下
            [0.0, 1.0]       # 左下
        ], dtype=np.float32)
        
        # ホモグラフィ行列を計算
        self.homography_matrix = cv2.getPerspectiveTransform(
            self.keyboard_corners, self.camera_corners
        )
    
    def transform_point(self, x, y):
        """正規化座標をカメラ座標に変換"""
        point = np.array([[[x, y]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(point, self.homography_matrix)
        return int(transformed[0][0][0]), int(transformed[0][0][1])
    
    def is_point_in_key(self, px, py, key):
        """点がキー内にあるかチェック"""
        # キーの4角を変換
        key_corners = [
            self.transform_point(key.x, key.y),
            self.transform_point(key.x + key.width, key.y),
            self.transform_point(key.x + key.width, key.y + key.height),
            self.transform_point(key.x, key.y + key.height)
        ]
        
        # 点がポリゴン内にあるかチェック
        contour = np.array(key_corners)
        return cv2.pointPolygonTest(contour, (px, py), False) >= 0
    
    def draw_keyboard(self, frame, finger_positions=None):
        """キーボードを描画"""
        # 人差し指の座標を取得（複数の手に対応）
        index_fingers = []
        if finger_positions:
            for hand in finger_positions:
                for tip_id, x, y in hand['fingers']:
                    if tip_id == 8:  # 人差し指
                        index_fingers.append((x, y))
        
        # 各キーを描画
        for key in self.keyboard.keys:
            # キーの4角を変換
            top_left = self.transform_point(key.x, key.y)
            top_right = self.transform_point(key.x + key.width, key.y)
            bottom_right = self.transform_point(key.x + key.width, key.y + key.height)
            bottom_left = self.transform_point(key.x, key.y + key.height)
            
            # キーの枠色を決定
            color = (0, 0, 255)  # デフォルトは赤
            
            # 人差し指がキー内にあるかチェック
            for finger_x, finger_y in index_fingers:
                if self.is_point_in_key(finger_x, finger_y, key):
                    color = (0, 255, 0)  # 緑
                    break
            
            # キーを描画（ポリゴンとして描画）
            pts = np.array([top_left, top_right, bottom_right, bottom_left], np.int32)
            pts = pts.reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], True, color, 1)
            
            # キーコードを描画
            # center_x = (top_left[0] + bottom_right[0]) // 2
            # center_y = (top_left[1] + bottom_right[1]) // 2
            # cv2.putText(frame, key.keycode, (center_x - 10, center_y + 5),
            #            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)