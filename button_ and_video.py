import tkinter as tk
import ctypes
from PIL import Image, ImageTk
import cv2
import numpy as np
import subprocess

# === 參數設定 ===
TOL_VIDEO = 40  # 去黑底容差
SCALE = 0.8  # 放大倍率
VIDEO_PATH = "PawnPromotion.mp4"
BG_COLOR = "black"  # 背景與透明色

# === 視窗設定 ===
root = tk.Tk()
root.overrideredirect(True)
root.config(bg=BG_COLOR)
root.wm_attributes("-transparentcolor", BG_COLOR)


# === 去黑底函式 ===
def remove_black_to_transparent(frame, tol=TOL_VIDEO):
    rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    b, g, r, a = cv2.split(rgba)
    mask = (b < tol) & (g < tol) & (r < tol)
    rgba[mask, 3] = 0
    return rgba


# === 讀取影片、取得基本資料 ===
cap = cv2.VideoCapture(VIDEO_PATH)
ret, frame = cap.read()
if not ret:
    raise RuntimeError("❌ 無法讀取 PawnPromotion.mp4，請確認檔案存在。")

h, w = frame.shape[:2]
new_w, new_h = int(w * SCALE), int(h * SCALE)

# === 取出影片所有幀（一次讀完，方便倒放） ===
frames = []
cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (new_w, new_h))
    rgba = remove_black_to_transparent(frame)
    frames.append(rgba)
cap.release()

# === 顯示第一幀（兵） ===
photo_first = ImageTk.PhotoImage(Image.fromarray(frames[0]))
label = tk.Label(root, image=photo_first, bg=BG_COLOR, bd=0)
label.pack()

# === 播放控制 ===
is_pawn = True  # 當前狀態（兵 or 皇后）
playing = False


def play(frames_seq, speed=30):
    """播放指定序列（正向或反向），可調整速度"""
    global playing
    if not frames_seq:
        return
    playing = True

    def _next(i):
        global playing
        if i < len(frames_seq):
            img = ImageTk.PhotoImage(Image.fromarray(frames_seq[i]))
            label.config(image=img)
            label.image = img
            label.after(speed, lambda: _next(i + 1))
        else:
            playing = False

    _next(0)


chess_process = None


def toggle_state(event=None):
    """點擊切換兵/皇后動畫"""
    global is_pawn, chess_process
    if playing:
        return
    if is_pawn:
        # 兵 → 皇后（正向播放）
        play(frames, speed=10)
        chess_process = subprocess.Popen(["python", "chess_board.py"])
        is_pawn = False
    else:
        # 皇后 → 兵（倒放）
        play(frames[::-1], speed=5)
        # 若程式仍在執行，結束它
        if chess_process and chess_process.poll() is None:
            chess_process.terminate()  # 結束程式
            chess_process = None
        is_pawn = True


# 左鍵切換動畫 / 右鍵關閉
label.bind("<Button-1>", toggle_state)
label.bind("<Button-3>", lambda e: root.destroy())

root.geometry("683x384+-303+502")

root.mainloop()
