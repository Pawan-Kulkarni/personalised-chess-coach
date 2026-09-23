from chess_coach.engine.stockfish import analyze_position


fen = "rnbqkbnr/pppp1ppp/8/4p3/4P3/2N5/PPPP1PPP/R1BQKBNR b KQkq - 1 2"

result = analyze_position(fen, depth=15)

print("Evaluation:", result["evaluation"])
print("Best move:", result["best_move"])
print("Depth:", result["depth"])
print("PV:", result["principal_variation"])