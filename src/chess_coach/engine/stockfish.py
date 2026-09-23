import chess
import chess.engine


STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"


def analyze_position(fen: str, depth: int = 20) -> dict:
    board = chess.Board(fen)

    engine = chess.engine.SimpleEngine.popen_uci(
        STOCKFISH_PATH
    )

    result = engine.analyse(
        board,
        chess.engine.Limit(depth=depth)
    )

    engine.quit()

    score = result["score"].pov(chess.WHITE).score(mate_score=100000)

    best_move = result["pv"][0].uci()

    principal_variation = [
        move.uci()
        for move in result["pv"]
    ]

    return {
        "evaluation": score / 100,
        "best_move": best_move,
        "depth": depth,
        "principal_variation": principal_variation,
    }