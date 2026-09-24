from chess_coach.chess.pgn import parse_pgn_file
from chess_coach.analysis.positional import analyze_pawn_structure_change


def test_pawn_structure_changes_from_real_game():
    games = parse_pgn_file("data/raw/test_game.pgn")
    game = games[0]

    board = game.board()

    for ply, move in enumerate(game.mainline_moves(), start=1):

        changes = analyze_pawn_structure_change(board, move)

        if changes["new_doubled"] or changes["new_isolated"]:
            print(f"\nPly: {ply}")
            print(f"Move: {board.san(move)}")
            print(f"Changes: {changes}")

        board.push(move)