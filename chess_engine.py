import random

PIECE_VALUE = {"p": 10, "n": 32, "b": 33, "r": 50, "q": 91, "k": 100}
INF = 10**9
ai_stop = False

PIECE_SQUARE = {
    "k": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [3, 2, -1, -2, -2, -1, 2, 3],
        [4, 3, 2, -1, -1, 1, 3, 4],
        [4, 6, 4, -1, 2, -1, 6, 4],
    ],
    "q": [
        [-5, 0, 1, 1, 1, 1, 0, -5],
        [2, 4, 3, 3, 3, 3, 4, 2],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
        [0, 2, 1, 0, 0, 0, 2, 0],
        [-5, 0, 1, 1, 0, 0, 0, -5],
        [-5, 1, 1, 1, 1, 0, 0, -5],
    ],
    "r": [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [3, 4, 3, 3, 3, 3, 4, 3],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [-2, 0, 1, 1, 1, 1, 0, -2],
        [-1, -1, 1, 6, 6, 1, -1, -1],
    ],
    "b": [
        [-4, -2, -1, -1, -1, -1, -2, -4],
        [-2, 0, -1, 0, 0, -1, 0, -2],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 8, 1, 1, 8, 0, 0],
        [-1, 1, 0, 2, 2, 0, 1, -1],
        [-2, 2, 0, 2, 2, 0, 2, -2],
        [-4, -2, -2, -1, -1, -2, -2, -4],
    ],
    "n": [
        [-4, -2, -2, -2, -2, -2, -2, -4],
        [-2, -2, 6, 5, 5, 6, -2, -2],
        [-2, 2, 3, 4, 4, 3, 2, -2],
        [-2, 2, 2, 4, 4, 2, 2, -2],
        [-2, 0, 2, 3, 3, 2, 0, -2],
        [-2, 1, 6, 2, 2, 6, 1, -2],
        [-2, -2, 0, 0, 0, 0, -2, -2],
        [-4, -2, -2, -2, -2, -2, -2, -4],
    ],
    "p": [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [11, 10, 11, 11, 11, 11, 10, 11],
        [9, 8, 8, 9, 9, 8, 8, 9],
        [1, 2, 5, 6, 7, 5, 0, 1],
        [0, 0, 3, 4, 4, 0, -1, 0],
        [1, 1, -1, 2, 2, -2, -1, 1],
        [1, 2, -8, -8, -8, 3, 3, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
}


def find_best_move(logic, max_depth, callback=None):
    original_turn = logic.turn

    def minimax(depth, maximizing):
        if depth == 0:
            score = 0
            for r in range(8):
                for c in range(8):
                    p = logic.board[r][c]
                    if not p:
                        continue
                    if original_turn == "w":
                        score += (
                            PIECE_VALUE[p[1]] if p[0] == "w" else -PIECE_VALUE[p[1]]
                        )
                        score += (
                            PIECE_SQUARE[p[1]][r][c]
                            if p[0] == "w"
                            else -PIECE_SQUARE[p[1]][r][c]
                        )
                    else:
                        score += (
                            PIECE_VALUE[p[1]] if p[0] == "b" else -PIECE_VALUE[p[1]]
                        )
                        score += (
                            PIECE_SQUARE[p[1]][7 - r][c]
                            if p[0] == "b"
                            else -PIECE_SQUARE[p[1]][7 - r][c]
                        )
            return score

        best = -(10**12) if maximizing else 10**12
        legal = logic.get_legal_moves(logic.turn)
        if not legal:
            if logic.is_in_check(logic.turn):
                return -(10**11) if maximizing else 10**11
            return 0

        for mv in legal:
            snap = logic.snapshot()
            logic.make_move(*mv)
            val = minimax(depth - 1, not maximizing)
            logic.restore(snap)
            if maximizing:
                best = max(best, val)
            else:
                best = min(best, val)
        return best

    best_move = None
    best_score = -(10**12)
    legal = logic.get_legal_moves(logic.turn)
    for mv in legal:
        if callback:
            callback(mv)
        snap = logic.snapshot()
        logic.make_move(*mv)
        score = minimax(max_depth - 1, False)
        logic.restore(snap)
        if score > best_score - random.randint(0, 5):
            best_score = score
            best_move = mv
        elif score == best_score and random.random() < 0.1:
            best_move = mv
    if callback:
        callback(None)
    return best_move


def find_random_move(logic):
    legal_moves = logic.get_legal_moves(logic.turn)
    if not legal_moves:
        return None
    return random.choice(legal_moves)
