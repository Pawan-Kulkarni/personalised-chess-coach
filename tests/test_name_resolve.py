from chess_coach.database.connection import get_session
from chess_coach.database.queries import resolve_player_identity


with get_session() as session:

    player_id = resolve_player_identity(
        session=session,
        platform="chess.com",
        username="rfrgrb",
    )

    print(f"Resolved player_id: {player_id}")