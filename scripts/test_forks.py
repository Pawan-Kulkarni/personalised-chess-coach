import chess
from chess_coach.analysis.tactics import analyze_move_tactics
from chess_coach.analysis.tactics.forks import detect_fork


def test_real_fork():
    # White knight on c3 can move to e4.
    # From e4 it attacks:
    # - Black king on d6
    # - Black queen on c5
    board = chess.Board(
        "8/8/3k4/2q5/8/2N5/8/4K3 w - - 0 1"
    )

    move = chess.Move.from_uci("c3e4")

    result = detect_fork(board, move)

    assert result["is_fork"] is True
    assert len(result["targets"]) == 2

    print("Real fork:", result)


def test_single_target():
    # Knight moves to e4 but only attacks one enemy non-pawn piece.
    board = chess.Board(
        "8/8/3k4/8/8/2N5/8/4K3 w - - 0 1"
    )

    move = chess.Move.from_uci("c3e4")

    result = detect_fork(board, move)

    assert result["is_fork"] is False

    print("Single target:", result)


def test_pawns_are_not_targets():
    # Knight on c3 moves to e4 and attacks two black pawns,
    # but pawns are explicitly excluded from our fork definition.
    board = chess.Board(
        "8/8/8/8/3p1p2/2N5/8/4K3 w - - 0 1"
    )

    move = chess.Move.from_uci("c3e4")

    result = detect_fork(board, move)

    assert result["is_fork"] is False

    print("Pawn targets excluded:", result)
    
def test_allowed_fork():
    board = chess.Board(
        "r1bqk2r/ppp1bpp1/3p1n1p/8/4P2P/2Q4R/PPP2PP1/RNB1KB2 w Qkq - 0 9"
    )

    move = chess.Move.from_uci("h3g3")

    result = analyze_move_tactics(board, move)

    assert result["fork"]["player"]["created"] is False
    assert result["fork"]["player"]["allowed"] is False

    assert result["fork"]["opponent"]["created"] is False
    assert result["fork"]["opponent"]["allowed"] is True

    print("Allowed fork:", result)


if __name__ == "__main__":
    test_real_fork()
    test_single_target()
    test_pawns_are_not_targets()
    test_allowed_fork()
    print("\nAll fork tests passed.")