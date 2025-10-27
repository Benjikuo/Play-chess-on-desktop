import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
import subprocess

VIDEO_PATH = "./video/PawnPromotion.mp4"
BG_COLOR = "black"
SCALE = 1.2
TOL = 40


def remove_black_to_transparent(frame, tol=TOL):
    rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    b, g, r, a = cv2.split(rgba)
    mask = (b < tol) & (g < tol) & (r < tol)
    rgba[mask, 3] = 0
    return rgba


def play(frames_seq, speed=15):
    if not frames_seq:
        return

    global playing_video
    playing_video = True

    def _next(i):
        global playing_video
        if i < len(frames_seq):
            img = ImageTk.PhotoImage(Image.fromarray(frames_seq[i]))
            label.config(image=img)
            label.image = img  # type: ignore
            label.after(speed, lambda: _next(i + 1))
        else:
            playing_video = False

    _next(0)


def toggle_state(event=None):
    global pawn, chess_program
    if playing_video:
        return
    if pawn:
        chess_program = subprocess.Popen(["pythonw", "chess_board.py"])
        play(frames, speed=10)
        pawn = False
    else:
        play(frames[::-1], speed=5)
        if chess_program and chess_program.poll() is None:
            chess_program.terminate()
            chess_program = None
        pawn = True


def watch_child():
    global chess_program, playing_video
    if chess_program and chess_program.poll() is not None:
        if not pawn and not playing_video:
            toggle_state(event=None)
        chess_program = None
    root.after(100, watch_child)


cap = cv2.VideoCapture(VIDEO_PATH)
ret, frame = cap.read()
if not ret:
    raise RuntimeError(
        "❌ Unable to read PawnPromotion.mp4. Please check the file path."
    )


h, w = frame.shape[:2]
new_w, new_h = int(w * SCALE), int(h * SCALE)

cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
frames = []
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (new_w, new_h))
    clear = remove_black_to_transparent(frame)
    frames.append(clear)
cap.release()

root = tk.Tk()
root.overrideredirect(True)
root.config(bg=BG_COLOR)
root.wm_attributes("-transparentcolor", BG_COLOR)

root.update_idletasks()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
window_w = root.winfo_width()
window_h = root.winfo_height()
x = (screen_w - window_w) // 2
y = (screen_h - window_h) - 5
root.geometry(f"{window_w}x{window_h}+{x}+{y}")

pawn = True
playing_video = False
chess_program = None

watch_child()

photo_first = ImageTk.PhotoImage(Image.fromarray(frames[0]))
label = tk.Label(root, image=photo_first, bg=BG_COLOR, bd=0)
label.pack()
label.bind("<Button-1>", toggle_state)

root.mainloop()
