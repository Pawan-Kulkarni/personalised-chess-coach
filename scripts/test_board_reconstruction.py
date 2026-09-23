from chess_coach.chess.pgn import parse_pgn_file
from chess_coach.chess.positions import get_board_before_move


games = parse_pgn_file("data/raw/test_game.pgn")

game = games[0]

target_ply = 37

board = get_board_before_move(
    game,
    target_ply
)

print("Board BEFORE move:")
print(board)

move = list(game.mainline_moves())[target_ply - 1]

print("\nMove:")
print(move)

print("\nBoard AFTER move:")
board.push(move)
print(board)