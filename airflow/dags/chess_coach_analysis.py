'''Purpose:
Analyzes the moves of previously ingested chess games and stores detailed move-level analysis in the move_analysis table.

Workflow:

Reads PGN games from the configured raw PGN file.
Identifies the corresponding game in PostgreSQL using the PGN hash.
Determines the user's color (White or Black) using the canonical player_id.
Retrieves the stored board positions and Stockfish engine evaluations for the game.
Analyzes each move using:
Engine evaluation loss — measures how much the move worsened the position.
Move classification — good, inaccuracy, mistake, or blunder.
Tactical analysis — identifies newly attacked or vulnerable pieces.
Positional analysis — identifies pawn-structure changes such as doubled pawns, isolated pawns, and pawn-island changes.
Interprets positional changes from the user's perspective, regardless of which side made the move.
Saves the resulting move-level analysis to PostgreSQL.

Output:
The DAG populates the move_analysis table with structured information that can later be used to identify recurring weaknesses and generate personalized chess-coaching insights.

Important:
This DAG does not run Stockfish itself. It consumes the engine evaluations already stored in the engine_analysis table and enriches them with tactical and positional analysis.'''



from datetime import datetime

from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy.orm import sessionmaker

from chess_coach.chess.pgn import parse_pgn_file
from chess_coach.database.models import (
    Position,
    EngineAnalysis,
    Game,
)
from chess_coach.database.queries import save_move_analysis
from chess_coach.analysis.move_analysis import analyze_game_moves
PLAYER_ID = 1

@dag(
    dag_id="chess_coach_move_analysis",
    start_date=datetime(2026, 9, 23),
    schedule=None,
    catchup=False,
)
def chess_coach_move_analysis():

    @task
    def analyze_moves():

        hook = PostgresHook(
            postgres_conn_id="chess_coach_postgres"
        )

        engine = hook.get_sqlalchemy_engine()

        SessionLocal = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
        )

        pgn_path = "data/raw/test_game.pgn"

        games = parse_pgn_file(pgn_path)
        print(f"PGN path: {pgn_path}")
        print(f"Games returned: {games}")
        print(f"Games type: {type(games)}")
        with SessionLocal() as session:

            for game in games:

                # Find the corresponding database game.
                # For now we use the PGN hash to identify it.
                import hashlib

                pgn_text = str(game)

                pgn_hash = hashlib.sha256(
                    pgn_text.encode("utf-8")
                ).hexdigest()

                from chess_coach.database.models import Game

                db_game = (
                    session.query(Game)
                    .filter_by(pgn_hash=pgn_hash)
                    .first()
                )

                if db_game is None:
                    print(
                        f"Game not found in database: {pgn_hash}"
                    )
                    continue

                game_id = db_game.game_id
                # Determine which side belongs to the player
                # whose games we are analyzing.

                if db_game.white_player_id == PLAYER_ID:
                    player_color = "white"

                elif db_game.black_player_id == PLAYER_ID:
                    player_color = "black"

                else:
                    print(
                        f"Player {PLAYER_ID} is not part of game {game_id}"
                    )
                    continue

                positions = (
                    session.query(Position)
                    .filter_by(game_id=game_id)
                    .order_by(Position.ply)
                    .all()
                )

                analyses = (
                    session.query(EngineAnalysis)
                    .join(Position)
                    .filter(Position.game_id == game_id)
                    .order_by(Position.ply)
                    .all()
                )

                print(
                    f"Analyzing game {game_id}: "
                    f"{len(positions)} positions, "
                    f"{len(analyses)} engine analyses"
                )

                results = analyze_game_moves(
                    game=game,
                    positions=positions,
                    analyses=analyses,
                    player_color=player_color,
                )

                for result in results:
                    save_move_analysis(
                        session,
                        result,
                    )

                session.commit()

                print(
                    f"Saved {len(results)} move analyses "
                    f"for game {game_id}"
                )

    analyze_moves()


chess_coach_move_analysis()