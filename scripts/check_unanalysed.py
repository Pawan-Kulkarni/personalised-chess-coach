from chess_coach.database.connection import get_session
from chess_coach.database.queries import get_unanalyzed_positions


with get_session() as session:

    positions = get_unanalyzed_positions(session)

    print(f"Unanalyzed positions: {len(positions)}")

    for position in positions[:5]:
        print(
            position.position_id,
            position.move_number,
            position.move_san,
        )