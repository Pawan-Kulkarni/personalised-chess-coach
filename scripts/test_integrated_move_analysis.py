from chess_coach.chess.pgn import parse_pgn_file
from chess_coach.database.connection import get_session
from chess_coach.database.models import Position, EngineAnalysis
from chess_coach.database.queries import save_move_analysis
from chess_coach.analysis.move_analysis import analyze_game_moves


PGN_PATH = "data/raw/test_game.pgn"
GAME_ID = 3   # use your actual game_id


games = parse_pgn_file(PGN_PATH)
game = games[0]

with get_session() as session:

    positions = (
        session.query(Position)
        .filter_by(game_id=GAME_ID)
        .order_by(Position.ply)
        .all()
    )

    analyses = (
        session.query(EngineAnalysis)
        .join(Position)
        .filter(Position.game_id == GAME_ID)
        .order_by(Position.ply)
        .all()
    )

    print(f"Positions: {len(positions)}")
    print(f"Engine analyses: {len(analyses)}")

    results = analyze_game_moves(
        game=game,
        positions=positions,
        analyses=analyses,
    )

    print(f"Analyzed {len(results)} moves")

    for result in results:
        save_move_analysis(session, result)

    session.commit()

    print("Move analysis saved successfully.")