'''Purpose:
Analyzes previously ingested chess games at the move level by combining stored Stockfish evaluations with tactical and positional analysis, and stores the results for personalized coaching.

Workflow:

Reads games from the configured raw PGN file.
Identifies the corresponding game in PostgreSQL using the PGN hash.
Determines the user's color (White or Black) using the canonical player_id.
Retrieves the stored positions and Stockfish evaluations for the game.
Analyzes each move to calculate:
Evaluation loss — how much the move worsened the position.
Move classification — good, inaccuracy, mistake, or blunder.
Tactical analysis — newly attacked or vulnerable pieces created by the move.
Positional analysis — pawn-structure changes such as doubled pawns, isolated pawns, and pawn-island changes.
Maintains the user's perspective throughout the game, regardless of which side made the individual move.
Saves the resulting move-level analysis to the move_analysis table.

Output:
The DAG enriches each analyzed position with structured move-level information that can later be aggregated to identify recurring tactical and positional patterns in the user's games.

Important:
This DAG does not run Stockfish itself. It consumes the engine evaluations already stored in the engine_analysis table and combines them with Python-based tactical and positional analysis.'''

from datetime import datetime

from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy.orm import sessionmaker

from chess_coach.database.queries import (
    get_positions_with_analysis,
    save_move_analysis,
)
from chess_coach.analysis.blunders import detect_mistakes


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

        with SessionLocal() as session:

            rows = get_positions_with_analysis(session)

            mistakes = detect_mistakes(rows)

            for mistake in mistakes:
                save_move_analysis(session, mistake)

            session.commit()

            print(f"Processed {len(mistakes)} moves")

    analyze_moves()


chess_coach_move_analysis()