from PIL import Image, ImageTk
import tkinter as tk
import time
import json
from chess_logic import ChessLogic, SYM, START_BOARD
from chess_engine import find_best_move, find_random_move, ai_stop

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
selected = None
ai_from = None
ai_to = None
ai_continue = False
ai_doing = False
do_progression = False
promotion_frame = None
promotion_buttons = []
highlight = []
wrong_hint_squares = []
logic = ChessLogic()


def save_game(filename="chess_save.json"):
    def compress_board(board):
        # 把空格("")改成"__"
        return [" ".join(cell if cell else "__" for cell in row) for row in board]

    compact_history = []
    for state in logic.history:
        compact_history.append(
            {
                "board": compress_board(state["board"]),
                "turn": state["turn"],
                "has_moved": state["has_moved"],
                "en_passant": state["en_passant"],
            }
        )

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(compact_history, f, ensure_ascii=False, indent=2)
    print("✅ 棋局已儲存至", filename)


def load_game(filename="chess_save.json"):
    global logic
    try:
        with open(filename, "r", encoding="utf-8") as f:
            history = json.load(f)

        def expand_board(board_lines):
            # 把 "__" 還原成 ""
            return [
                [cell if cell != "__" else "" for cell in row.split(" ")]
                for row in board_lines
            ]

        expanded_history = []
        for state in history:
            expanded_history.append(
                {
                    "board": expand_board(state["board"]),
                    "turn": state["turn"],
                    "has_moved": state["has_moved"],
                    "en_passant": state["en_passant"],
                }
            )

        logic.history = expanded_history
        logic.history_index = len(expanded_history) - 1
        print(logic.history_index)
        logic.restore(expanded_history[-1])
        print("♻️ 棋局已載入")
    except Exception as e:
        print("⚠️ 載入失敗：", e)
        logic.board = START_BOARD
    draw_board()


def draw_board(clear=False):
    canva.delete("all")
    bg_image = Image.open(
        "./image/chessboard_clean2.png" if flipped else "./image/chessboard_clean.png"
    )
    bg_photo = ImageTk.PhotoImage(bg_image)
    canva.create_image(0, 0, image=bg_photo, anchor="nw")
    canva.bg_photo = bg_photo  # type: ignore

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

            # 🟥 將軍提示
            if (
                piece
                and piece[1] == "k"
                and logic.is_in_check(piece[0])
                and not (white_r, white_c) == selected
                and not (white_r, white_c) in wrong_hint_squares
            ):
                canva.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill=CHECK,
                    outline="",
                )

            # 🟩 單一選取棋子
            if selected and (white_r, white_c) == selected:
                canva.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill=PICK_HIGHLIGHT,
                    stipple="gray50",
                    outline="",
                )

            # 🟦 合法移動位置
            elif (white_r, white_c) in highlight:
                canva.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill=LEGAL_HIGHLIGHT,
                    stipple="gray50",
                    outline="",
                )

            # 🟪 錯誤點擊提示：顯示有合法移動的己方棋子
            elif (white_r, white_c) in wrong_hint_squares:
                canva.create_rectangle(
                    x0,
                    y0,
                    x1,
                    y1,
                    fill=WRONG_HIGHLIGHT,
                    stipple="gray50",
                    outline="",
                )

            # 棋子文字
            if piece:
                canva.create_text(
                    (c + 1.5) * CELL_SIZE - 1,
                    (r + 1.5) * CELL_SIZE - 2,
                    text=SYM[piece],
                    font=("Segoe UI Symbol", FONT_SIZE),
                    fill="#222222" if piece.startswith("w") else "#111111",
                )


def on_click(event):
    if do_progression:
        return

    global dragging, selected, highlight, wrong_hint_squares
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

    # ✅ 成功移動
    hide_promotion_buttons()
    if selected and ((selected, pos) in legal_moves):

        def promotion_callback(color):
            # 暫停顯示按鈕直到使用者選完
            show_promotion_buttons()
            root.wait_variable(selected_piece)
            return selected_piece.get()

        logic.do_move(selected, pos, promotion_callback)
        save_game()

        selected = None
        highlight = []
        wrong_hint_squares = []

    # ✅ 點己方棋子 → 顯示合法移動
    elif piece and piece[0] == logic.turn:
        selected = pos
        highlight = [dst for (src, dst) in legal_moves if src == pos]
        wrong_hint_squares = []

    # ✅ 點空格 → 清除所有高亮
    elif piece == "":
        selected = None
        highlight = []
        wrong_hint_squares = []
        start_move(event)

    # ✅ 點敵方棋 → 顯示己方「有合法移動」的棋子
    else:
        selected = None
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


def draw_ai_think(move):
    if move is None:
        return

    global ai_from, ai_to, ai_doing
    if ai_to:
        canva.delete(ai_to)
        ai_to = None
    if ai_from:
        canva.delete(ai_from)
        ai_from = None

    (r0, c0), (r1, c1) = move
    if flipped:
        r0, c0 = 7 - r0, 7 - c0
        r1, c1 = 7 - r1, 7 - c1

    # from
    fx0 = (c0 + 1) * CELL_SIZE
    fy0 = (r0 + 1) * CELL_SIZE
    fx1 = (c0 + 2) * CELL_SIZE
    fy1 = (r0 + 2) * CELL_SIZE

    # to
    tx0 = (c1 + 1) * CELL_SIZE
    ty0 = (r1 + 1) * CELL_SIZE
    tx1 = (c1 + 2) * CELL_SIZE
    ty1 = (r1 + 2) * CELL_SIZE

    if ai_continue:
        canva.create_rectangle(
            CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE * 9,
            CELL_SIZE * 9,
            outline="#EBEB26",
            width=4,
        )

    ai_to = canva.create_rectangle(
        tx0, ty0, tx1, ty1, outline="#3371E5", width=4  # 藍色
    )
    ai_from = canva.create_rectangle(
        fx0, fy0, fx1, fy1, outline="#74E533", width=4  # 綠色
    )

    root.update()


def ai_move_continue():
    global ai_continue, ai_stop, ai_doing
    ai_continue = not ai_continue
    if ai_continue:
        ai_move()
    else:
        ai_stop = True  # 設定中斷旗標為 True，讓正在思考的 AI 停止


def ai_move():
    global logic, selected, highlight, wrong_hint_squares, ai_continue, do_progression, ai_doing, ai_stop
    if ai_doing:
        return

    ai_doing = True
    do_progression = False
    selected = None
    highlight = []
    wrong_hint_squares = []
    mv = find_best_move(logic, 3, callback=draw_ai_think)
    if mv:
        logic.do_move(*mv)
        save_game()
        draw_board()
        if ai_continue:
            root.after(0, ai_move)
    else:
        ai_continue = False

    ai_doing = False


def reset_board():
    global logic, selected, highlight, wrong_hint_squares, ai_stop, do_progression
    if ai_doing:
        return

    if logic.board == START_BOARD:
        draw_board(True)
        root.update()
        time.sleep(0.001)
    logic = ChessLogic()
    ai_stop = True
    do_progression = False
    selected = None
    highlight = []
    wrong_hint_squares = []
    save_game()
    draw_board()


def flip_board():
    global flipped, ai_doing
    if ai_doing:
        return

    flipped = not flipped
    draw_board()


def random_move():
    global logic, selected, highlight, wrong_hint_squares, do_progression, ai_doing
    if ai_doing:
        return

    do_progression = False
    selected = None
    highlight = []
    wrong_hint_squares = []
    mv = find_random_move(logic)
    if mv:
        logic.do_move(*mv)
        save_game()
        draw_board()


def undo_move():
    global selected, highlight, wrong_hint_squares, do_progression, ai_doing
    if ai_doing:
        return

    do_progression = False
    logic.undo()
    selected = None
    highlight = []
    wrong_hint_squares = []
    draw_board()


def forward_move():
    global selected, highlight, wrong_hint_squares, do_progression, ai_doing
    if ai_doing:
        return

    do_progression = False
    logic.forward()
    selected = None
    highlight = []
    wrong_hint_squares = []
    draw_board()


def progression():
    global selected, highlight, wrong_hint_squares, do_progression, ai_doing
    if do_progression or ai_doing:
        do_progression = False
        return

    if len(logic.history) <= 1:
        draw_board(True)
        root.update()
        time.sleep(0.001)

    do_progression = True  # 標記為正在播放
    selected = None
    highlight = []
    wrong_hint_squares = []
    print(logic.history_index, len(logic.history))
    if logic.history_index >= len(logic.history) - 1:
        logic.history_index = 0

    while logic.history_index < len(logic.history):
        logic.restore(logic.history[logic.history_index])  # ✅ 修正這一行
        draw_board()
        root.update()
        time.sleep(0.1)
        logic.history_index += 1
        if not do_progression:
            break
    logic.history_index -= 1
    do_progression = False  # 播放完畢後重置狀態


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

        btn.place(
            x=i * (size + 5) + 5,  # 四顆並排，中間留點距離
            y=5,
            width=size,
            height=size,
        )
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
    selected_piece.set(p)  # 通知主程式選好了
    hide_promotion_buttons()


# === Tk 初始化 ===
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
canva = tk.Canvas(
    root, width=CELL_SIZE * 10, height=CELL_SIZE * 10, highlightthickness=0
)
canva.pack()

selected_piece = tk.StringVar()
load_game()

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
root.bind("<w>", lambda e: ai_move_continue())
root.bind("<e>", lambda e: ai_move())
root.bind("<r>", lambda e: reset_board())
root.bind("<t>", lambda e: flip_board())
root.bind("<s>", lambda e: random_move())
root.bind("<d>", lambda e: undo_move())
root.bind("<f>", lambda e: forward_move())
root.bind("<g>", lambda e: progression())

root.mainloop()
