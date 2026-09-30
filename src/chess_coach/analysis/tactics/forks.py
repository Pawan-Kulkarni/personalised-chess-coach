import chess


VALID_FORK_TARGETS = {
    chess.KING,
    chess.QUEEN,
    chess.ROOK,
    chess.BISHOP,
    chess.KNIGHT,
}


def detect_fork(board_before, move):
    """
    Detect whether the piece that just moved creates a fork.

    A fork is defined here as a move after which the moved piece
    attacks at least two enemy non-pawn pieces.

    Pawns are excluded as fork targets.
    """

    board_after = board_before.copy()
    board_after.push(move)

    attacker = board_after.piece_at(move.to_square)

    if attacker is None:
        return {
            "is_fork": False,
            "attacker": None,
            "attacker_square": None,
            "targets": [],
        }

    targets = []

    for square in board_after.attacks(move.to_square):
        target = board_after.piece_at(square)

        if target is None:
            continue

        # Only enemy pieces count as fork targets.
        if target.color == attacker.color:
            continue

        # Pawns are excluded.
        if target.piece_type not in VALID_FORK_TARGETS:
            continue

        targets.append({
            "square": chess.square_name(square),
            "piece": target.symbol().upper(),
        })

    return {
        "is_fork": len(targets) >= 2,
        "attacker": attacker.symbol().upper(),
        "attacker_square": chess.square_name(move.to_square),
        "targets": targets,
    }
    
    
def find_fork_opportunities(board, color):
    """
    Find all legal moves for the given color that create a fork.
    """

    opportunities = []

    board_copy = board.copy()
    board_copy.turn = color

    for move in board_copy.legal_moves:
        result = detect_fork(board_copy, move)

        if result["is_fork"]:
            opportunities.append(move)

    return opportunities