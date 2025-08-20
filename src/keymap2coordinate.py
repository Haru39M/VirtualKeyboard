from bs4 import BeautifulSoup as bs

class KeySwitch:
    def __init__(self, keycode, x, y, width, height):
        self.keycode = keycode
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

    def __repr__(self):
        return f"KeyClass(keycode='{self.keycode}', x={self.x}, y={self.y}, width={self.width}, height={self.height})"

class KeyBoard:
    def __init__(self,width,height):
        self.width = float(width)
        self.height = float(height)
        self.keys = []
    
    def appendKey(self,key:KeySwitch):
        self.keys.append(key)

    def normalize(self):
        for key in self.keys:
            key.x /= self.width
            key.y /= self.width
            key.width /= self.width
            key.height /= self.width

def loadKeyBoard(filename):
    # XMLファイルを読み込む
    with open(filename, "r", encoding="utf-8") as keymap:
        soup = bs(keymap, "xml")
        # keys = []

        #search frame
        for cell in soup.find_all("mxCell", vertex="1"):
            value = cell.get("value")
            geometry = cell.find("mxGeometry")
            if value == "FRAME":
                print("Find!")
                frame_w = geometry.get("width",0)
                frame_h = geometry.get("height",0)
                keyboard = KeyBoard(frame_w,frame_h)

        # extract keyswitch and append to keyboard
        for cell in soup.find_all("mxCell", vertex="1"):
            value = cell.get("value")
            geometry = cell.find("mxGeometry")

            if value == "FRAME":
                continue
            else:
                keycode = value
            if geometry and keycode:  # 念のため空のvalueは除外
                x = geometry.get("x", 0)
                y = geometry.get("y", 0)
                w = geometry.get("width", 0)
                h = geometry.get("height", 0)
                key = KeySwitch(keycode, x, y, w, h)
                # keys.append(key)
                keyboard.appendKey(key)
    return keyboard



if __name__ == "__main__":
    keyboard = loadKeyBoard("keymap.xml")
    # 出力確認
    for key in keyboard.keys:
        print(key)