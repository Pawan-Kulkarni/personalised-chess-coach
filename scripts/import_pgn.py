import chess.pgn

from chess_coach.database.connection import engine
from chess_coach.database.models import Game, Position
from sqlalchemy.orm import Session


PGN_FILE = "data/raw/test_game.pgn"


# Read PGN
with open(PGN_FILE) as file:
    game = chess.pgn.read_game(file)


# Create our Game database object
db_game = Game(
    white_player=game.headers.get("White", "Unknown"),
    black_player=game.headers.get("Black", "Unknown"),
    result=game.headers.get("Result", "*"),
    event=game.headers.get("Event"),
    pgn=str(game),
)


with Session(engine) as session:

    # Save the game
    session.add(db_game)
    session.flush()

    print("Game ID:", db_game.game_id)

    # Start from initial chess position
    board = game.board()

    # Replay every move
    for move_number, move in enumerate(game.mainline_moves(), start=1):

        board.push(move)

        position = Position(
            game_id=db_game.game_id,
            move_number=move_number,
            fen=board.fen(),
        )

        session.add(position)

    # Save everything
    session.commit()

    print("Game and positions saved successfully.")