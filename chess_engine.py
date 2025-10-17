import random
import time

PIECE_VALUE = {"p": 11, "n": 35, "b": 40, "r": 55, "q": 95, "k": 100}
INF = 10**9
ai_stop = False

PIECE_SQUARE = {
    "k": [  # King
        [-3, -2, -1, 0, 0, -1, -2, -3],
        [-2, 1, 1, 1, 1, 1, -1, -2],
        [-1, 1, 1, 1, 1, 1, 1, -1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 0, -1, -1, 0, 0, 0],
        [3, 2, -1, -2, -2, -1, 2, 3],
        [4, 3, 2, -1, -1, 1, 3, 4],
        [4, 8, 6, -1, 0, -1, 8, 4],
    ],
    "q": [  # Queen
        [-5, 0, 1, 1, 1, 1, 0, -5],
        [2, 3, 3, 3, 3, 3, 3, 2],
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 3, 1, 1, 1, 1, 3, 0],
        [0, 3, 0, 1, 1, 0, 3, 0],
        [0, 2, 1, 0, 0, 0, 2, 0],
        [-5, 0, 3, 3, -1, 0, 0, -5],
        [-5, 3, 3, 3, 3, 0, 0, -5],
    ],
    "r": [  # Rook
        [1, 1, 1, 1, 1, 1, 1, 1],
        [3, 7, 7, 7, 7, 7, 7, 3],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [-2, 0, 1, 1, 1, 1, 0, -2],
        [-1, -1, 1, 6, 6, 1, -1, -1],
    ],
    "b": [  # Bishop
        [-4, -2, -1, -1, -1, -1, -2, -4],
        [-2, 0, -1, 0, 0, -1, 0, -2],
        [1, 0, 1, 1, 1, 1, 0, 1],
        [0, 1, 1, 1, 1, 1, 1, 0],
        [0, 0, 8, 1, 1, 8, 0, 0],
        [-1, 1, 0, 2, 2, 0, 1, -1],
        [-2, 2, 0, 2, 2, 0, 2, -2],
        [-4, -2, -2, -1, -1, -2, -2, -4],
    ],
    "n": [  # Knight
        [-4, -2, -2, -2, -2, -2, -2, -4],
        [-2, -2, 6, 5, 5, 6, -2, -2],
        [-2, 2, 3, 4, 4, 3, 2, -2],
        [-2, 2, 2, 4, 4, 2, 2, -2],
        [-2, 0, 2, 3, 3, 2, 0, -2],
        [-2, 1, 6, 2, 2, 6, 1, -2],
        [-2, -2, 0, 0, 0, 0, -2, -2],
        [-4, -2, -2, -2, -2, -2, -2, -4],
    ],
    "p": [  # Pawn
        [0, 0, 0, 0, 0, 0, 0, 0],
        [11, 10, 11, 11, 11, 11, 10, 11],
        [9, 8, 8, 9, 9, 8, 8, 9],
        [1, 2, 5, 6, 7, 5, 0, 1],
        [0, 0, 3, 4, 4, 0, -1, 0],
        [3, 3, -1, 2, 2, -2, -1, 3],
        [1, 2, -8, -8, -8, 3, 3, 1],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ],
}


def find_best_move(logic, max_depth, callback=None):
    original_turn = logic.turn  # ✅ 記住最初是誰在走

    def minimax(depth, alpha, beta, maximizing):

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

            enemy_color = "b" if original_turn == "w" else "w"
            for r in range(8):
                for c in range(8):
                    if logic.board[r][c] == enemy_color + "k":
                        mobility = len(logic.potential_moves(r, c))
                        score += (10 - mobility) * 3  # 國王越被限制，分數越高
                        break

            enemy_king = logic.locate_king(enemy_color)
            my_king = logic.locate_king(original_turn)
            if enemy_king and my_king:
                dist = abs(my_king[0] - enemy_king[0]) + abs(my_king[1] - enemy_king[1])
                score += max(0, 100 - dist ^ 2) * 3  # 自家王越靠近敵王加分（幫助收官）

            return score

        legal = logic.get_legal_moves(logic.turn)
        if not legal:
            if logic.is_in_check(logic.turn):
                # 🟥 被將死（對方贏）
                return -100000 if maximizing else 100000
            else:
                # 🟨 平局
                return 0

        if maximizing:
            best = -INF
            for mv in legal:
                snap = logic.snapshot()
                logic.make_move(*mv)

                if not legal:
                    if logic.is_in_check(logic.turn):
                        return -(10**11) if maximizing else 10**11
                    return 0

                val = minimax(depth - 1, alpha, beta, False)
                logic.restore(snap)

                best = max(best, val)
                alpha = max(alpha, best)
                if beta <= alpha:  # 🚀 剪枝：提前結束
                    break
            return best
        else:
            best = INF
            for mv in legal:
                snap = logic.snapshot()
                logic.make_move(*mv)

                if not legal:
                    if logic.is_in_check(logic.turn):
                        return -(10**11) if maximizing else 10**11
                    return 0

                val = minimax(depth - 1, alpha, beta, True)
                logic.restore(snap)

                best = min(best, val)
                beta = min(beta, best)
                if beta <= alpha:
                    break
            return best

    # === 主函式 ===
    best_move = None
    best_score = -INF
    legal = logic.get_legal_moves(logic.turn)
    for mv in legal:
        if callback:
            callback(mv)
        snap = logic.snapshot()
        logic.make_move(*mv)
        score = minimax(max_depth - 1, -INF, INF, False)
        logic.restore(snap)

        if score > best_score + 5 - random.random() * 10:
            best_score = score
            best_move = mv
        elif score == best_score and random.random() < 0.1:
            best_move = mv  # 增加隨機性

    if callback:
        callback(None)
    return best_move


def find_random_move(logic):
    legal_moves = logic.get_legal_moves(logic.turn)
    if not legal_moves:
        return None
    return random.choice(legal_moves)
