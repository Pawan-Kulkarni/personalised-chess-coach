'''Purpose:
Ingests chess games from PGN files into PostgreSQL and creates the position-level records required for downstream analysis.

Workflow:

Reads chess games from the configured raw PGN file.
Extracts game metadata such as:
White player
Black player
Result
Date
Event
PGN
Generates a SHA-256 hash of each PGN to uniquely identify games and make the ingestion process idempotent.
Resolves the White and Black players to their canonical player_id values using the configured player accounts.
Creates a record in the games table if the game has not already been ingested.
Replays the game's moves using python-chess.
Creates a positions record for each position after every move, storing:
Ply
Move number
Move in UCI format
Move in SAN format
FEN
Updates existing games with resolved player identities when the game has already been ingested.

Output:
The DAG populates the games and positions tables, providing the structured game and position data required by downstream Stockfish and move-analysis pipelines.

Important:
This DAG does not perform chess-engine evaluation or tactical/positional analysis. Its responsibility is to transform raw PGN games into structured database records that can be consumed by subsequent analysis DAGs.'''


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
        pgn_path = "data/raw/test_game_2.pgn"
        games = parse_pgn_file(pgn_path)

        # 5. Load games into PostgreSQL
        with SessionLocal() as session:

            for game in games:
                load_game(session, game)

            session.commit()

        print(f"Processed {len(games)} game(s)")

    ingest_games()


chess_coach_ingestion()