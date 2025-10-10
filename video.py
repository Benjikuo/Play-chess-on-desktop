import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np

TOL = 40  # 容差，可調整去背嚴格度


def remove_black_to_transparent(frame, tol=TOL):
    # 轉 RGBA
    rgba = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

    # 取出 RGB 三個通道
    b, g, r, a = cv2.split(rgba)

    # 找出接近黑色的像素 (容差越大，越容易變透明)
    mask = (b < tol) & (g < tol) & (r < tol)

    # 將黑色像素的透明度設為 0
    rgba[mask, 3] = 0

    return rgba


def play_video():
    ret, frame = cap.read()
    if ret:
        rgba = remove_black_to_transparent(frame)
        img = Image.fromarray(rgba)
        photo = ImageTk.PhotoImage(img)
        lbl.config(image=photo)
        lbl.image = photo
        lbl.after(30, play_video)
    else:
        cap.release()


root = tk.Tk()
root.overrideredirect(True)
root.wm_attributes("-topmost", True)
root.config(bg="black")
root.wm_attributes("-transparentcolor", "black")

lbl = tk.Label(root, bg="black", bd=0)
lbl.pack()

cap = cv2.VideoCapture("PawnPromotion.mp4")
play_video()

root.mainloop()
