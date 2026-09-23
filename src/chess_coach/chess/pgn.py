import chess.pgn


def parse_pgn_file(file_path: str):
    """
    Parse a PGN file and return a list of python-chess Game objects.
    """

    games = []

    with open(file_path, "r", encoding="utf-8") as pgn_file:
        while True:
            game = chess.pgn.read_game(pgn_file)

            if game is None:
                break

            games.append(game)

    return games