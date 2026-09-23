import chess


def find_attacked_pieces(board: chess.Board):
    """
    Find non-king pieces that are attacked and undefended.

    This is a tactical candidate, not a blunder verdict.
    """

    hanging_pieces = []

    for square, piece in board.piece_map().items():

        if piece.piece_type == chess.KING:
            continue

        attackers = board.attackers(
            not piece.color,
            square
        )

        defenders = board.attackers(
            piece.color,
            square
        )

        if attackers:

            attacker_details = [
                {
                    "piece": board.piece_at(attacker).symbol(),
                    "square": chess.square_name(attacker),
                }
                for attacker in attackers
            ]

            defender_details = [
                {
                    "piece": board.piece_at(defender).symbol(),
                    "square": chess.square_name(defender),
                }
                for defender in defenders
            ]

            hanging_pieces.append({
                "square": chess.square_name(square),
                "piece": piece.symbol(),
                "color": "white" if piece.color == chess.WHITE else "black",

                "attackers": attacker_details,
                "defenders": defender_details,

                "attacker_count": len(attackers),
                "defender_count": len(defenders),
                })

    return hanging_pieces


def find_new_attacked_pieces(
    board_before: chess.Board,
    move: chess.Move,
):
    mover = board_before.turn

    mover_color = (
        "white"
        if mover == chess.WHITE
        else "black"
    )

    attacked_before = find_attacked_pieces(board_before)

    board_after = board_before.copy()
    board_after.push(move)

    attacked_after = find_attacked_pieces(board_after)

    before_squares = {
        item["square"]
        for item in attacked_before
        if item["color"] == mover_color
    }

    new_attacked = [
        item
        for item in attacked_after
        if item["color"] == mover_color
        and item["square"] not in before_squares
    ]

    # ADD THE LOOP HERE
    for item in new_attacked:
        item["is_outnumbered"] = (
            item["attacker_count"] > item["defender_count"]
        )

    return new_attacked


def analyze_move_tactics(board_before, move):
    new_attacked = find_new_attacked_pieces(board_before, move)

    return {
        "new_attacked_pieces": new_attacked,
    }
    
def analyze_game_tactics(game):
    """
    Analyze tactical candidates for every move in a game.
    """

    board = game.board()
    results = []

    for ply, move in enumerate(game.mainline_moves(), start=1):

        tactical_result = analyze_move_tactics(
            board,
            move,
        )

        results.append({
            "ply": ply,
            "move": move.uci(),
            "tactical_analysis": tactical_result,
        })

        board.push(move)

    return results