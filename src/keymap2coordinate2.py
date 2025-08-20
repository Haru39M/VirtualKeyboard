from bs4 import BeautifulSoup as bs

class KeySwitch:
    """個々のキーを表すクラス"""
    def __init__(self, keycode, x, y, width, height):
        self.keycode = keycode
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

    def __repr__(self):
        return f"KeySwitch(keycode='{self.keycode}', x={self.x:.3f}, y={self.y:.3f}, width={self.width:.3f}, height={self.height:.3f})"

class KeyBoard:
    """キーボード全体を表すクラス"""
    def __init__(self, width, height):
        self.width = float(width)
        self.height = float(height)
        self.keys = []
    
    def append_key(self, key: KeySwitch):
        """キーを追加"""
        self.keys.append(key)
    
    # def normalize(self):
    #     """座標を正規化（幅を1.0とする）"""
    #     for key in self.keys:
    #         key.x /= self.width
    #         key.y /= self.width
    #         key.width /= self.width
    #         key.height /= self.width
    def normalize(self):
        """座標を正規化（幅と高さそれぞれを1.0とする）"""
        for key in self.keys:
            key.x /= self.width
            key.y /= self.height
            key.width /= self.width
            key.height /= self.height
    
    def __repr__(self):
        return f"KeyBoard(width={self.width}, height={self.height}, keys={len(self.keys)})"

def loadKeyBoard(filename):
    """XMLファイルからキーボードデータを読み込む"""
    try:
        with open(filename, "r", encoding="utf-8") as keymap:
            soup = bs(keymap, "xml")
            keyboard = None
            
            # FRAMEを検索してキーボードのサイズを取得
            for cell in soup.find_all("mxCell", vertex="1"):
                value = cell.get("value")
                geometry = cell.find("mxGeometry")
                
                if value == "FRAME" and geometry:
                    frame_w = float(geometry.get("width", 0))
                    frame_h = float(geometry.get("height", 0))
                    keyboard = KeyBoard(frame_w, frame_h)
                    print(f"キーボードサイズ: {frame_w} x {frame_h}")
                    break
            
            if keyboard is None:
                raise ValueError("FRAMEが見つかりませんでした")
            
            # キースイッチを抽出してキーボードに追加
            key_count = 0
            for cell in soup.find_all("mxCell", vertex="1"):
                value = cell.get("value")
                geometry = cell.find("mxGeometry")
                
                # FRAMEは除外
                if value == "FRAME" or not value or not geometry:
                    continue
                
                keycode = value.strip()
                if keycode:  # 空文字列は除外
                    x = float(geometry.get("x", 0))
                    y = float(geometry.get("y", 0))
                    w = float(geometry.get("width", 0))
                    h = float(geometry.get("height", 0))
                    
                    key = KeySwitch(keycode, x, y, w, h)
                    keyboard.append_key(key)
                    key_count += 1
            
            print(f"読み込まれたキー数: {key_count}")
            return keyboard
            
    except FileNotFoundError:
        print(f"ファイル '{filename}' が見つかりませんでした")
        raise
    except Exception as e:
        print(f"キーボードデータの読み込み中にエラーが発生しました: {e}")
        raise

if __name__ == "__main__":
    try:
        keyboard = loadKeyBoard("keymap.xml")
        keyboard.normalize()
        
        print(f"\n{keyboard}")
        print("\nキー一覧:")
        for key in keyboard.keys:
            print(f"  {key}")
            
    except Exception as e:
        print(f"エラー: {e}")