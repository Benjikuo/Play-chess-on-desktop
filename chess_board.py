from PIL import Image, ImageTk
import tkinter as tk
import random
import copy
import time

LIGHT_SQUARE = "#F3E7CF"
DARK_SQUARE = "#E09F3E"
CELL_SIZE = 35
FONT_SIZE = 20

turn = "w"
flipped = False
dragging = False
selected = None
history = []
files = ["a", "b", "c", "d", "e", "f", "g", "h"]
ranks = ["8", "7", "6", "5", "4", "3", "2", "1"]

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


def start_move(event):
    global dragging, drag_x, drag_y, root_x, root_y
    if (
        event.x < CELL_SIZE
        or event.x > CELL_SIZE * 9
        or event.y < CELL_SIZE
        or event.y > CELL_SIZE * 9
    ):
        dragging = True
        drag_x = event.x_root
        drag_y = event.y_root
        root_x = root.winfo_x()
        root_y = root.winfo_y()
    else:
        dragging = False
        on_click(event)


def do_move(event):
    global dragging, drag_x, drag_y, root_x, root_y
    if dragging:
        dx = event.x_root - drag_x
        dy = event.y_root - drag_y
        root.geometry(f"+{root_x + dx}+{root_y + dy}")


def draw_board(clear=False):
    canva.delete("all")
    if not flipped:
        bg_image = Image.open("./image/chessboard_clean.png")
    else:
        bg_image = Image.open("./image/chessboard_clean2.png")
    bg_photo = ImageTk.PhotoImage(bg_image)
    canva.create_image(0, 0, image=bg_photo, anchor="nw")
    canva.bg_photo = bg_photo  # type: ignore

    if clear:
        return

    for r in range(8):
        for c in range(8):
            rr = 7 - r if flipped else r
            cc = 7 - c if flipped else c
            piece = board[rr][cc]
            if piece:
                x = (c + 1.5) * CELL_SIZE - 1
                y = (r + 1.5) * CELL_SIZE - 2
                canva.create_text(
                    x,
                    y,
                    text=SYM[piece],
                    font=("Segoe UI Symbol", FONT_SIZE),
                    fill="#222222" if piece.startswith("w") else "#111111",
                )


def on_click(event):
    global selected, board_state, turn
    c = int(event.x // CELL_SIZE) - 1
    r = int(event.y // CELL_SIZE) - 1
    if not (0 <= r < 8 and 0 <= c < 8):
        return
    rr, cc = (7 - r if flipped else r), (7 - c if flipped else c)
    piece = board[rr][cc]

    if selected:
        r0, c0 = selected  # type: ignore
        piece0 = board[r0][c0]
        if piece0 and piece0[0] == turn:
            history.append(copy.deepcopy(board))
            board[rr][cc], board[r0][c0] = piece0, ""
            turn = "b" if turn == "w" else "w"
        selected = None
    else:
        if piece and piece[0] == turn:
            selected = (rr, cc)
    draw_board()


def engine_move():
    global board, turn
    moves = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p and p[0] == turn:
                for rr in range(8):
                    for cc in range(8):
                        if board[rr][cc] == "" or board[rr][cc][0] != turn:
                            moves.append(((r, c), (rr, cc)))
    if moves:
        move = random.choice(moves)
        (r1, c1), (r2, c2) = move
        history.append(copy.deepcopy(board))
        board[r2][c2], board[r1][c1] = board[r1][c1], ""
        turn = "b" if turn == "w" else "w"
        draw_board()
    draw_board()


def reset_board():
    global board, turn, history
    draw_board(True)
    root.update()
    time.sleep(0.005)
    board = copy.deepcopy(START_BOARD)
    draw_board()
    turn = "w"
    history.clear()


def super_move():
    global board, turn
    moves = []
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p and p[0] == turn:
                for rr in range(8):
                    for cc in range(8):
                        if board[rr][cc] == "" or board[rr][cc][0] != turn:
                            moves.append(((r, c), (rr, cc)))
    if moves:
        move = random.choice(moves)
        (r1, c1), (r2, c2) = move
        history.append(copy.deepcopy(board))
        board[r2][c2], board[r1][c1] = board[r1][c1], ""
        turn = "b" if turn == "w" else "w"
        draw_board()


def undo_move():
    global board, turn
    if history:
        board = history.pop()
        turn = "b" if turn == "w" else "w"
        draw_board()


def flip_board():
    global flipped
    flipped = not flipped
    draw_board()


root = tk.Tk()
root.overrideredirect(True)
board = copy.deepcopy(START_BOARD)
canva = tk.Canvas(
    root,
    width=CELL_SIZE * 10,
    height=CELL_SIZE * 10,
    highlightthickness=0,
)
canva.pack()

root.update_idletasks()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
window_w = root.winfo_width()
window_h = root.winfo_height()
x = (screen_w - window_w) // 2
y = (screen_h - window_h) // 2
root.geometry(f"{window_w}x{window_h}+{x}+{y}")

draw_board()

canva.bind("<Button-1>", start_move)
canva.bind("<B1-Motion>", do_move)

root.bind("<e>", lambda e: engine_move())
root.bind("<r>", lambda e: reset_board())
root.bind("<s>", lambda e: super_move())
root.bind("<d>", lambda e: undo_move())
root.bind("<f>", lambda e: flip_board())

root.mainloop()
