import tkinter as tk
import random
import copy

LIGHT_SQUARE = "#F3E7CF"
DARK_SQUARE = "#E09F3E"
cell_size = 35
font_size = 18

SYM = {
    "wp": "♙",
    "wr": "♖",
    "wn": "♘",
    "wb": "♗",
    "wq": "♕",
    "wk": "♔",
    "bp": "♟",
    "br": "♜",
    "bn": "♞",
    "bb": "♝",
    "bq": "♛",
    "bk": "♚",
    "": "",
}

START_BOARD = [
    ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
    ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["", "", "", "", "", "", "", ""],
    ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
    ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"],
]

files = ["a", "b", "c", "d", "e", "f", "g", "h"]
ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]

board_state = copy.deepcopy(START_BOARD)
turn = "w"
history = []
flipped = False

root = tk.Tk()
W = cell_size * 10
H = cell_size * 10
canvas = tk.Canvas(root, width=W, height=H, highlightthickness=0)
canvas.pack()


def draw_board():
    canvas.delete("all")
    canvas.create_rectangle(0, 0, W, H, fill="#232323", outline="")
    for c in range(8):
        x = (c + 1.5) * cell_size
        canvas.create_text(
            x,
            0.5 * cell_size,
            text=files[c],
            fill="white",
            font=("Segoe UI Symbol", int(font_size * 0.8)),
        )
        canvas.create_text(
            x,
            9.5 * cell_size,
            text=files[c],
            fill="white",
            font=("Segoe UI Symbol", int(font_size * 0.8)),
        )
    for r in range(8):
        y = (r + 1.5) * cell_size
        canvas.create_text(
            0.5 * cell_size,
            y,
            text=ranks[r],
            fill="white",
            font=("Segoe UI Symbol", int(font_size * 0.8)),
        )
        canvas.create_text(
            9.5 * cell_size,
            y,
            text=ranks[r],
            fill="white",
            font=("Segoe UI Symbol", int(font_size * 0.8)),
        )

    for r in range(8):
        for c in range(8):
            rr = 7 - r if flipped else r
            cc = 7 - c if flipped else c
            x1, y1 = (c + 1) * cell_size, (r + 1) * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
            piece = board_state[rr][cc]
            if piece:
                canvas.create_text(
                    x1 + cell_size / 2,
                    y1 + cell_size / 2,
                    text=SYM[piece],
                    font=("Segoe UI Symbol", font_size + 2),
                    fill="#1a1a1a" if piece.startswith("w") else "#0a0a0a",
                )


# === 點擊 ===
selected = None


def on_click(event):
    global selected, board_state, turn
    c = int(event.x // cell_size) - 1
    r = int(event.y // cell_size) - 1
    if not (0 <= r < 8 and 0 <= c < 8):
        return
    rr, cc = (7 - r if flipped else r), (7 - c if flipped else c)
    piece = board_state[rr][cc]

    if selected:
        r0, c0 = selected
        piece0 = board_state[r0][c0]
        if piece0 and piece0[0] == turn:
            history.append(copy.deepcopy(board_state))
            board_state[rr][cc], board_state[r0][c0] = piece0, ""
            turn = "b" if turn == "w" else "w"
        selected = None
    else:
        if piece and piece[0] == turn:
            selected = (rr, cc)
    draw_board()


# === 按鈕功能 ===
def flip_board():
    global flipped
    flipped = not flipped
    draw_board()


def undo_move():
    global board_state, turn
    if history:
        board_state = history.pop()
        turn = "b" if turn == "w" else "w"
        draw_board()


def reset_board():
    global board_state, turn, history
    board_state = copy.deepcopy(START_BOARD)
    turn = "w"
    history.clear()
    draw_board()


def ai_move():
    global board_state, turn
    moves = []
    for r in range(8):
        for c in range(8):
            p = board_state[r][c]
            if p and p[0] == turn:
                for rr in range(8):
                    for cc in range(8):
                        if board_state[rr][cc] == "" or board_state[rr][cc][0] != turn:
                            moves.append(((r, c), (rr, cc)))
    if moves:
        move = random.choice(moves)
        (r1, c1), (r2, c2) = move
        history.append(copy.deepcopy(board_state))
        board_state[r2][c2], board_state[r1][c1] = board_state[r1][c1], ""
        turn = "b" if turn == "w" else "w"
        draw_board()


canvas.bind("<Button-1>", on_click)
draw_board()

# === 按鈕列 ===
frame = tk.Frame(root, bg="#232323")
frame.pack(fill="x")


def create_button(frame, text, cmd, color="#E09F3E"):
    return tk.Button(
        frame,
        text=text,
        command=cmd,
        bg=color,  # 背景色
        fg="white",  # 字體顏色
        activebackground="#FFB347",  # 點擊時顏色
        activeforeground="black",
        relief="flat",  # 扁平風格
        font=("Segoe UI", 11, "bold"),
        width=6,
        height=1,
        cursor="hand2",  # 滑鼠游標變手型
        bd=0,  # 無邊框
    )


create_button(frame, "🔃換邊", flip_board).pack(side="left", padx=6, pady=6)
create_button(frame, "◀毀棋", undo_move).pack(side="left", padx=6, pady=6)
create_button(frame, "↩重新", reset_board).pack(side="left", padx=6, pady=6)
create_button(frame, "💡電腦", ai_move).pack(side="left", padx=6, pady=6)
# ↩


def start_move(event):
    global drag_x, drag_y
    drag_x = event.x
    drag_y = event.y


def do_move(event):
    x = event.x_root - drag_x
    y = event.y_root - drag_y
    root.geometry(f"+{x}+{y}")


canvas.bind("<Button-1>", start_move)
canvas.bind("<B1-Motion>", do_move)
root.overrideredirect(True)

root.mainloop()
