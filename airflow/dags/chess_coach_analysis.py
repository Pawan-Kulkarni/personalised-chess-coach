from datetime import datetime

from airflow.sdk import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy.orm import sessionmaker

from chess_coach.database.models import Position, EngineAnalysis
from chess_coach.database.queries import get_unanalyzed_positions
from chess_coach.engine.stockfish import analyze_position


@dag(
    dag_id="chess_coach_analysis",
    start_date=datetime(2026, 9, 23),
    schedule=None,
    catchup=False,
)
def chess_coach_analysis():

    @task
    def find_unanalyzed_positions():

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

            positions = get_unanalyzed_positions(session)

            position_data = [
                {
                    "position_id": position.position_id,
                    "fen": position.fen,
                }
                for position in positions
            ]

        print(
            f"Found {len(position_data)} "
            "unanalyzed positions"
        )

        return position_data

    @task
    def analyze_position_task(position_data):

        position_id = position_data["position_id"]
        fen = position_data["fen"]

        print(f"Analyzing position {position_id}")

        analysis = analyze_position(
            fen=fen,
            depth=20,
        )

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

            engine_analysis = EngineAnalysis(
                position_id=position_id,
                evaluation=analysis["evaluation"],
                best_move=analysis["best_move"],
                depth=analysis["depth"],
                principal_variation=" ".join(
                    analysis["principal_variation"]
                ),
            )

            session.add(engine_analysis)
            session.commit()

        print(
            f"Finished position {position_id}: "
            f"evaluation={analysis['evaluation']}, "
            f"best_move={analysis['best_move']}"
        )

    positions = find_unanalyzed_positions()

    analyze_position_task.expand(
        position_data=positions
    )


chess_coach_analysis()