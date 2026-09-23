from chess_coach.chess.pgn import parse_pgn_file
from chess_coach.database.connection import SessionLocal
from chess_coach.database.queries import load_game


PGN_PATH = "data/raw/test_game.pgn"


def main():
    games = parse_pgn_file(PGN_PATH)

    print(f"Found {len(games)} game(s)")

    with SessionLocal() as session:
        for game in games:
            load_game(session, game)

        session.commit()

    print("Games loaded successfully")


if __name__ == "__main__":
    main()