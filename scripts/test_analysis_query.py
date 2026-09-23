from chess_coach.database.connection import get_session
from chess_coach.database.queries import get_positions_with_analysis

with get_session() as session:
    rows = get_positions_with_analysis(session)

    print(f"Found {len(rows)} positions")

    for position, analysis in rows[:10]:
        print(
            f"ply={position.ply} "
            f"move={position.move_san} "
            f"eval={analysis.evaluation:+.2f}"
        )