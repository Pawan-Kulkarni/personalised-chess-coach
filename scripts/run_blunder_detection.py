from chess_coach.database.connection import get_session
from chess_coach.database.queries import (
    get_positions_with_analysis,
    save_move_analysis,
)
from chess_coach.analysis.blunders import detect_mistakes


with get_session() as session:
    rows = get_positions_with_analysis(session)

    mistakes = detect_mistakes(rows)

    for mistake in mistakes:
        save_move_analysis(session, mistake)

    session.commit()

    print(f"Processed {len(mistakes)} moves")