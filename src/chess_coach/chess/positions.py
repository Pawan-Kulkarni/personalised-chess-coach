import chess


def get_board_before_move(game, target_ply: int) -> chess.Board:
    """
    Reconstruct the board immediately before the move
    at target_ply.
    """

    board = game.board()

    for ply, move in enumerate(game.mainline_moves(), start=1):
        if ply == target_ply:
            return board

        board.push(move)

    raise ValueError(
        f"Could not find ply {target_ply} in game"
    )