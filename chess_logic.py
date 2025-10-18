from copy import deepcopy

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


def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8


def find_color(p):
    return p[0] if p else ""


def find_type(p):
    return p[1] if p else ""


def enemy(turn):
    return "b" if turn == "w" else "w"


class ChessLogic:
    def __init__(self):
        self.board = deepcopy(START_BOARD)
        self.turn = "w"
        self.en_passant = None
        self.defined_castling = {
            "wR0": False,
            "wR7": False,
            "bR0": False,
            "bR7": False,
        }
        self.history_index = 0
        self.history = [self.snapshot()]

    def locate_king(self, color_k):
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == color_k + "k":
                    return (r, c)
        return None

    def is_square_attacked(self, target_r, target_c, attack_color):
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if not p or find_color(p) != attack_color:
                    continue
                for tr, tc in self.potential_moves(r, c, ignore_castle=True):
                    if (tr, tc) == (target_r, target_c):
                        return True
        return False

    def is_in_check(self, color):
        king_pos = self.locate_king(color)
        if not king_pos:
            return True
        return self.is_square_attacked(king_pos[0], king_pos[1], enemy(color))

    def potential_moves(self, pr, pc, ignore_castle=False):
        p = self.board[pr][pc]
        if not p:
            return []

        color, type = p[0], p[1]
        moves = []

        if type == "p":
            step = -1 if color == "w" else 1
            start = 6 if color == "w" else 1
            if self.board[pr + step][pc] == "":
                moves.append((pr + step, pc))
                if pr == start and self.board[pr + 2 * step][pc] == "":
                    moves.append((pr + 2 * step, pc))
            for dc in (-1, 1):
                mr, mc = pr + step, pc + dc
                if in_bounds(mr, mc) and find_color(self.board[mr][mc]) == enemy(color):
                    moves.append((mr, mc))
            if self.en_passant:
                er, ec = self.en_passant
                if pr + step == er and abs(ec - pc) == 1:
                    moves.append((er, ec))

        elif type == "n":
            for dr, dc in [
                (-2, -1),
                (-2, 1),
                (-1, -2),
                (-1, 2),
                (1, -2),
                (1, 2),
                (2, -1),
                (2, 1),
            ]:
                mr, mc = pr + dr, pc + dc
                if in_bounds(mr, mc) and find_color(self.board[mr][mc]) != color:
                    moves.append((mr, mc))

        elif type in ["b", "r", "q"]:
            dirs = []
            if type in ["b", "q"]:
                dirs += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            if type in ["r", "q"]:
                dirs += [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in dirs:
                mr, mc = pr + dr, pc + dc
                while in_bounds(mr, mc):
                    if self.board[mr][mc] == "":
                        moves.append((mr, mc))
                        mr += dr
                        mc += dc
                    else:
                        if find_color(self.board[mr][mc]) != color:
                            moves.append((mr, mc))
                        break

        elif type == "k":
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    mr, mc = pr + dr, pc + dc
                    if in_bounds(mr, mc) and find_color(self.board[mr][mc]) != color:
                        moves.append((mr, mc))
            if not ignore_castle:
                if self.is_in_check(color):
                    return moves
                row_home = 7 if color == "w" else 0
                if (
                    not self.defined_castling[f"{color}R7"]
                    and self.board[row_home][5] == ""
                    and self.board[row_home][6] == ""
                    and not self.is_square_attacked(row_home, 5, enemy(color))
                ):
                    moves.append((row_home, 6))
                if (
                    not self.defined_castling[f"{color}R0"]
                    and self.board[row_home][3] == ""
                    and self.board[row_home][2] == ""
                    and self.board[row_home][1] == ""
                    and not self.is_square_attacked(row_home, 3, enemy(color))
                ):
                    moves.append((row_home, 2))
        return moves

    def make_move(self, src, dst, promotion_callback=None):
        r0, c0 = src
        r1, c1 = dst
        piece = self.board[r0][c0]
        color = find_color(piece)

        if piece == color + "k":
            self.defined_castling[f"{color}R0"] = True
            self.defined_castling[f"{color}R7"] = True
        if piece == color + "r":
            if c0 == 0:
                self.defined_castling[f"{color}R0"] = True
            elif c0 == 7:
                self.defined_castling[f"{color}R7"] = True

        self.en_passant = None
        if find_type(piece) == "p" and (r0 != r1 and self.board[r1][c1] == ""):
            if color == "w":
                self.board[r1 + 1][c1] = ""
            else:
                self.board[r1 - 1][c1] = ""

        if find_type(piece) == "p" and abs(r1 - r0) == 2:
            self.en_passant = ((r0 + r1) // 2, c0)

        if find_type(piece) == "k" and abs(c1 - c0) == 2:
            if c1 > c0:
                self.board[r1][5] = self.board[r1][7]
                self.board[r1][7] = ""
                self.defined_castling[f"{color}R7"] = True
            else:
                self.board[r1][3] = self.board[r1][0]
                self.board[r1][0] = ""
                self.defined_castling[f"{color}R0"] = True

        if find_type(piece) == "p" and (r1 == 0 or r1 == 7):
            promote = None
            if promotion_callback:
                promote = promotion_callback(color)
            if not promote:
                promote = "q"
            self.board[r1][c1] = color + promote
        else:
            self.board[r1][c1] = piece

        self.board[r0][c0] = ""
        self.turn = enemy(self.turn)

    def get_legal_moves(self, color):
        legal = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if not p or find_color(p) != color:
                    continue
                for go_r, go_c in self.potential_moves(r, c):
                    snap = self.snapshot()
                    self.make_move((r, c), (go_r, go_c))
                    if not self.is_in_check(color):
                        legal.append(((r, c), (go_r, go_c)))
                    self.restore(snap)
        return legal

    def do_move(self, src, dst, promotion_callback=None):
        if self.history_index < len(self.history) - 1:
            self.history = self.history[: self.history_index + 1]
        self.make_move(src, dst, promotion_callback)
        self.history_index += 1
        self.history.append(self.snapshot((src, dst)))

    def undo(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.restore(self.history[self.history_index])

    def forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.restore(self.history[self.history_index])

    def snapshot(self, last_move=None):
        return {
            "board": deepcopy(self.board),
            "turn": self.turn,
            "has_moved": deepcopy(self.defined_castling),
            "en_passant": self.en_passant,
            "last_move": deepcopy(last_move),
        }

    def restore(self, snap):
        self.board = deepcopy(snap["board"])
        self.turn = snap["turn"]
        self.defined_castling = deepcopy(snap["has_moved"])
        self.en_passant = snap["en_passant"]
        return snap.get("last_move", None)
