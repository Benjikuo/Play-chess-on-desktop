from PIL import Image, ImageTk
import tkinter as tk
import time
from chess_logic import ChessLogic, SYM, START_BOARD

LIGHT_SQUARE = "#F3E7CF"
DARK_SQUARE = "#E09F3E"
LEGAL_HIGHLIGHT = "#1B71FB"
PICK_HIGHLIGHT = "#29FB33"
WRONG_HIGHLIGHT = "#CC00FF"
CHECK = "#FF545A"
CELL_SIZE = 35
FONT_SIZE = 20

flipped = False
dragging = False
pick_square = None
selected = None
promotion_frame = None
promotion_buttons = []
highlight = []
wrong_hint_squares = []
logic = ChessLogic()


def draw_board(clear=False):
    canva.delete("all")
    bg_image = Image.open(
        "./image/chessboard_clean2.png" if flipped else "./image/chessboard_clean.png"
    )
    bg_photo = ImageTk.PhotoImage(bg_image)
    canva.create_image(0, 0, image=bg_photo, anchor="nw")
    canva.bg_photo = bg_photo
    if clear:
        return
    for r in range(8):
        for c in range(8):
            white_r = 7 - r if flipped else r
            white_c = 7 - c if flipped else c
            piece = logic.board[white_r][white_c]
            x0 = (c + 1) * CELL_SIZE
            y0 = (r + 1) * CELL_SIZE
            x1 = (c + 2) * CELL_SIZE
            y1 = (r + 2) * CELL_SIZE
            if (
                piece
                and piece[1] == "k"
                and logic.is_in_check(piece[0])
                and not (white_r, white_c) == pick_square
                and not (white_r, white_c) in wrong_hint_squares
            ):
                canva.create_rectangle(x0, y0, x1, y1, fill=CHECK, outline="")
            if pick_square and (white_r, white_c) == pick_square:
                canva.create_rectangle(
                    x0, y0, x1, y1, fill=PICK_HIGHLIGHT, stipple="gray50", outline=""
                )
            elif (white_r, white_c) in highlight:
                canva.create_rectangle(
                    x0, y0, x1, y1, fill=LEGAL_HIGHLIGHT, stipple="gray50", outline=""
                )
            elif (white_r, white_c) in wrong_hint_squares:
                canva.create_rectangle(
                    x0, y0, x1, y1, fill=WRONG_HIGHLIGHT, stipple="gray50", outline=""
                )
            if piece:
                canva.create_text(
                    (c + 1.5) * CELL_SIZE - 1,
                    (r + 1.5) * CELL_SIZE - 2,
                    text=SYM[piece],
                    font=("Segoe UI Symbol", FONT_SIZE),
                    fill="#222222" if piece.startswith("w") else "#111111",
                )


def on_click(event):
    global dragging, selected, highlight, pick_square, wrong_hint_squares
    dragging = False
    wrong_hint_squares = []
    grid_r = int(event.y // CELL_SIZE)
    grid_c = int(event.x // CELL_SIZE)
    r, c = grid_r - 1, grid_c - 1
    if not (0 <= r < 8 and 0 <= c < 8):
        start_move(event)
        return
    white_r = 7 - r if flipped else r
    white_c = 7 - c if flipped else c
    piece = logic.board[white_r][white_c]
    pos = (white_r, white_c)
    legal_moves = logic.get_legal_moves(logic.turn)
    if selected and ((selected, pos) in legal_moves):
        logic.history.append(logic.snapshot())

        def promotion_callback(color):
            show_promotion_buttons()
            root.wait_variable(selected_piece)
            return selected_piece.get()

        logic.make_move(selected, pos, promotion_callback)
        selected = None
        pick_square = None
        highlight = []
        wrong_hint_squares = []
    elif piece and piece[0] == logic.turn:
        selected = pos
        pick_square = pos
        highlight = [dst for (src, dst) in legal_moves if src == pos]
        wrong_hint_squares = []
    elif piece == "":
        selected = None
        pick_square = None
        highlight = []
        wrong_hint_squares = []
        start_move(event)
    else:
        selected = None
        pick_square = None
        highlight = []
        wrong_hint_squares = list({src for (src, dst) in legal_moves})
    draw_board()


def start_move(event):
    global dragging, drag_x, drag_y, root_x, root_y
    drag_x, drag_y = event.x_root, event.y_root
    root_x, root_y = root.winfo_x(), root.winfo_y()
    dragging = True


def do_move(event):
    global dragging, drag_x, drag_y, root_x, root_y
    if dragging:
        dx, dy = event.x_root - drag_x, event.y_root - drag_y
        root.geometry(f"+{root_x + dx}+{root_y + dy}")


def reset_board():
    global logic, selected, highlight, pick_square, wrong_hint_squares
    if logic.board == START_BOARD:
        draw_board(True)
        root.update()
        time.sleep(0.001)
    logic = ChessLogic()
    pick_square = None
    selected = None
    highlight = []
    wrong_hint_squares = []
    draw_board()


def undo_move():
    global selected, highlight, pick_square, wrong_hint_squares
    if logic.board == START_BOARD:
        draw_board(True)
        root.update()
        time.sleep(0.001)
    logic.undo()
    pick_square = None
    selected = None
    highlight = []
    wrong_hint_squares = []
    draw_board()


def flip_board():
    global flipped
    flipped = not flipped
    draw_board()


def show_promotion_buttons():
    hide_promotion_buttons()
    global promotion_buttons, promotion_frame
    if logic.turn == "w":
        choices = (("♕", "q"), ("♖", "r"), ("♗", "b"), ("♘", "n"))
    else:
        choices = (("♛", "q"), ("♜", "r"), ("♝", "b"), ("♞", "n"))
    size = CELL_SIZE * 1.2
    promotion_frame = tk.Frame(root, bg="#333333")
    promotion_frame.config(width=(size + 5) * 4 + 5, height=size + 10)
    promotion_frame.place(x=175 - (4 * size + 25) / 2, y=175 - (size + 10) / 2)
    for i, (label, piece) in enumerate(choices):
        btn = tk.Button(
            promotion_frame,
            text=label,
            font=("Segoe UI Symbol", 20),
            bg="#E7E7E7",
            activebackground="#DDDDDD",
            relief="raised",
            width=3,
            bd=3,
            command=lambda p=piece: choose_promotion(p),
        )
        btn.place(x=i * (size + 5) + 5, y=5, width=size, height=size)
        promotion_buttons.append(btn)


def hide_promotion_buttons():
    global promotion_buttons, promotion_frame
    for btn in promotion_buttons:
        btn.destroy()
    promotion_buttons.clear()
    if promotion_frame:
        promotion_frame.destroy()
        promotion_frame = None


def choose_promotion(p):
    selected_piece.set(p)
    hide_promotion_buttons()


root = tk.Tk()
root.overrideredirect(True)
canva = tk.Canvas(
    root, width=CELL_SIZE * 10, height=CELL_SIZE * 10, highlightthickness=0
)
canva.pack()

selected_piece = tk.StringVar()

root.update_idletasks()
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
window_w = root.winfo_width()
window_h = root.winfo_height()
x = (screen_w - window_w) // 2
y = (screen_h - window_h) // 2
root.geometry(f"{window_w}x{window_h}+{x}+{y}")

canva.bind("<Button-1>", on_click)
canva.bind("<B1-Motion>", do_move)
canva.bind("<Button-2>", lambda e: root.destroy())
root.bind("<r>", lambda e: reset_board())
root.bind("<d>", lambda e: undo_move())
root.bind("<f>", lambda e: flip_board())

draw_board()
root.mainloop()
