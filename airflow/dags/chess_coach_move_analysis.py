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