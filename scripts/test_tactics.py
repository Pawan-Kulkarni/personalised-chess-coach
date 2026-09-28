import chess

from src.chess_coach.analysis.tactics import analyze_move_tactics


board = chess.Board()

move = chess.Move.from_uci("e2e4")

result = analyze_move_tactics(board, move)

print(result)