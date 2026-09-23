from chess_coach.database.connection import get_session
from chess_coach.database.queries import get_positions_with_analysis
from chess_coach.analysis.blunders import detect_mistakes


with get_session() as session:
    rows = get_positions_with_analysis(session)

    mistakes = detect_mistakes(rows)

    for mistake in mistakes:
        print(
            f"ply={mistake['ply']} "
            f"{mistake['player']} "
            f"move={mistake['move']} "
            f"before={mistake['eval_before']:+.2f} "
            f"after={mistake['eval_after']:+.2f} "
            f"loss={mistake['evaluation_loss']:+.2f} "
            f"→ {mistake['classification']}"
        )