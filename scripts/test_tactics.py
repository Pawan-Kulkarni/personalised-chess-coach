from chess_coach.chess.pgn import parse_pgn_file
from chess_coach.database.connection import get_session
from chess_coach.database.models import Position, EngineAnalysis
from chess_coach.analysis.blunders import analyze_move


games = parse_pgn_file("data/raw/test_game.pgn")
game = games[0]

moves = list(game.mainline_moves())

with get_session() as session:

    positions = (
        session.query(Position)
        .filter_by(game_id=3)
        .order_by(Position.ply)
        .all()
    )

    analyses = (
        session.query(EngineAnalysis)
        .join(Position)
        .filter(Position.game_id == 3)
        .order_by(Position.ply)
        .all()
    )

    board = game.board()

for i, move in enumerate(moves):

    ply = i + 1

    if ply == 1:
        # No "before" engine evaluation exists in our DB
        board.push(move)
        continue

    current_position = positions[i]

    previous_analysis = analyses[i - 1]
    current_analysis = analyses[i]

    result = analyze_move(
        board_before=board,
        move=move,
        eval_before=previous_analysis.evaluation,
        eval_after=current_analysis.evaluation,
        ply=ply,
    )

    print(
        f"\nMove {ply}: {current_position.move_san}"
    )

    print(f"Player: {result['player']}")

    print(
        f"Evaluation: "
        f"{result['eval_before']:+.2f} → "
        f"{result['eval_after']:+.2f}"
    )

    print(
        f"Loss: {result['evaluation_loss']:+.2f}"
    )

    print(
        f"Classification: {result['classification']}"
    )

    hanging = (
        result["tactical_analysis"]
        ["new_hanging_pieces"]
    )

    if hanging:
        print("New hanging pieces:")

        for piece in hanging:
            print(
            f"  {piece['piece']} on {piece['square']} "
            f"attackers={piece['attacker_count']} "
            f"defenders={piece['defender_count']} "
            f"outnumbered={piece['is_outnumbered']}"
        )

    board.push(move)