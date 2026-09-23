from datetime import datetime

from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy.orm import sessionmaker

from chess_coach.chess.pgn import parse_pgn_file
from chess_coach.database.queries import load_game


@dag(
    dag_id="chess_coach_ingestion",
    start_date=datetime(2026, 9, 23),
    schedule=None,
    catchup=False,
)
def chess_coach_ingestion():

    @task
    def ingest_games():

        # 1. Get PostgreSQL connection from Airflow
        hook = PostgresHook(
            postgres_conn_id="chess_coach_postgres"
        )

        # 2. Create SQLAlchemy engine from Airflow connection
        engine = hook.get_sqlalchemy_engine()

        # 3. Create SQLAlchemy session
        SessionLocal = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
        )

        # 4. Parse PGN
        pgn_path = "data/raw/test_game.pgn"
        games = parse_pgn_file(pgn_path)

        # 5. Load games into PostgreSQL
        with SessionLocal() as session:

            for game in games:
                load_game(session, game)

            session.commit()

        print(f"Processed {len(games)} game(s)")

    ingest_games()


chess_coach_ingestion()