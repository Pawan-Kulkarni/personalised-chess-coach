from sqlalchemy import select
from sqlalchemy.orm import Session

from chess_coach.database.connection import engine
from chess_coach.database.models import Position, EngineAnalysis
from chess_coach.engine.stockfish import analyze_position


with Session(engine) as session:

    # Get all positions from game 1
    positions = session.scalars(
        select(Position)
        .where(Position.game_id == 2)
        .order_by(Position.position_id)
    ).all()

    print(f"Found {len(positions)} positions")

    for position in positions:

        result = analyze_position(
            position.fen,
            depth=15
        )

        analysis = EngineAnalysis(
            position_id=position.position_id,
            evaluation=result["evaluation"],
            best_move=result["best_move"],
            depth=result["depth"],
            principal_variation=" ".join(
                result["principal_variation"]
            )
        )

        session.add(analysis)

        print(
            f"Position {position.position_id}: "
            f"eval={result['evaluation']}, "
            f"best={result['best_move']}"
        )

    session.commit()

print("Engine analysis saved successfully.")