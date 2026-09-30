from datetime import datetime

from airflow.sdk import dag, task
from sqlalchemy import select

from chess_coach.database.connection import get_session
from chess_coach.database.models import Position, EngineAnalysis
from chess_coach.engine.stockfish import analyze_position


@dag(
    dag_id="chess_coach_ingest_engine_eval",
    start_date=datetime(2026, 9, 1),
    schedule=None,
    catchup=False,
    tags=["chess-coach", "stockfish"],
)
def chess_coach_ingest_engine_eval():

    @task
    def analyze_positions():

        session = get_session()

        try:
            positions = session.scalars(
                select(Position)
                .order_by(Position.position_id)
            ).all()

            print(f"Found {len(positions)} positions")

            analyzed_count = 0
            skipped_count = 0

            for position in positions:

                # Check whether Stockfish analysis already exists
                existing = session.scalar(
                    select(EngineAnalysis)
                    .where(
                        EngineAnalysis.position_id
                        == position.position_id
                    )
                )

                if existing:
                    skipped_count += 1

                    print(
                        f"Position {position.position_id}: "
                        f"already analyzed, skipping"
                    )

                    continue

                # Run Stockfish
                result = analyze_position(
                    position.fen,
                    depth=15,
                )

                analysis = EngineAnalysis(
                    position_id=position.position_id,
                    evaluation=result["evaluation"],
                    best_move=result["best_move"],
                    depth=result["depth"],
                    principal_variation=" ".join(
                        result["principal_variation"]
                    ),
                )

                session.add(analysis)

                analyzed_count += 1

                print(
                    f"Position {position.position_id}: "
                    f"eval={result['evaluation']}, "
                    f"best={result['best_move']}"
                )

            session.commit()

            print(
                f"Engine analysis complete. "
                f"Analyzed={analyzed_count}, "
                f"Skipped={skipped_count}"
            )

        finally:
            session.close()

    analyze_positions()


chess_coach_ingest_engine_eval()