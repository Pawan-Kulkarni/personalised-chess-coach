from datetime import datetime

from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy.orm import sessionmaker

from chess_coach.chess.pgn import parse_pgn_file
from chess_coach.database.models import Position, EngineAnalysis
from chess_coach.database.queries import save_move_analysis
from chess_coach.analysis.move_analysis import analyze_game_moves


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