from datetime import datetime
import chess
import hashlib
from chess_coach.database.models import Game, Position, EngineAnalysis, MoveAnalysis, PlayerAccount
from sqlalchemy import select



def load_game(session, game):
    pgn_text = str(game)
    pgn_hash = hashlib.sha256(
        pgn_text.encode("utf-8")
    ).hexdigest()

    headers = game.headers

    white_username = headers.get("White")
    black_username = headers.get("Black")

    # Resolve external accounts to our internal player IDs.
    white_player_id = resolve_player_identity(
        session=session,
        platform="chess.com",
        username=white_username,
    )

    black_player_id = resolve_player_identity(
        session=session,
        platform="chess.com",
        username=black_username,
    )

    # Check whether this game has already been ingested.
    existing_game = (
        session.query(Game)
        .filter_by(pgn_hash=pgn_hash)
        .first()
    )

    if existing_game:
        # Game already exists, but player identity may have
        # been added after the original ingestion.
        existing_game.white_player_id = white_player_id
        existing_game.black_player_id = black_player_id

        print(f"Game already exists: {pgn_hash}")

        return existing_game

    # Parse game date.
    game_date = None

    if headers.get("Date"):
        try:
            game_date = datetime.strptime(
                headers["Date"],
                "%Y.%m.%d",
            ).date()
        except ValueError:
            pass

    # Create the game.
    db_game = Game(
        white_player=white_username or "Unknown",
        black_player=black_username or "Unknown",
        white_player_id=white_player_id,
        black_player_id=black_player_id,
        result=headers.get("Result", "*"),
        date=game_date,
        event=headers.get("Event"),
        pgn=pgn_text,
        pgn_hash=pgn_hash,
    )

    session.add(db_game)
    session.flush()

    # Store every position after each move.
    board = game.board()

    for ply, move in enumerate(
        game.mainline_moves(),
        start=1,
    ):
        move_san = board.san(move)
        move_uci = move.uci()

        board.push(move)

        position = Position(
            game_id=db_game.game_id,
            ply=ply,
            move_number=(ply + 1) // 2,
            move_uci=move_uci,
            move_san=move_san,
            fen=board.fen(),
        )

        session.add(position)

    return db_game


def get_game_fingerprint(game):
    pgn_text = str(game)
    return hashlib.sha256(pgn_text.encode("utf-8")).hexdigest()






def get_unanalyzed_positions(session):
    """
    Return positions that do not yet have Stockfish analysis.
    """

    statement = (
        select(Position)
        .outerjoin(
            EngineAnalysis,
            Position.position_id == EngineAnalysis.position_id
        )
        .where(
            EngineAnalysis.position_id.is_(None)
        )
    )

    return session.scalars(statement).all()


def get_positions_with_analysis(session):
    statement = (
        select(Position, EngineAnalysis)
        .join(
            EngineAnalysis,
            Position.position_id == EngineAnalysis.position_id
        )
        .order_by(Position.game_id, Position.ply)
    )

    return session.execute(statement).all()

def save_move_analysis(session, analysis):
    existing = (
        session.query(MoveAnalysis)
        .filter_by(position_id=analysis["position_id"])
        .first()
    )

    if existing:
        # Only fill tactical analysis if it hasn't been populated yet
        if not existing.tactical_analysis:
            existing.tactical_analysis = analysis["tactical_analysis"]

        return existing

    move_analysis = MoveAnalysis(
        position_id=analysis["position_id"],
        player=analysis["player"],
        evaluation_loss=analysis["evaluation_loss"],
        classification=analysis["classification"],
        tactical_analysis=analysis["tactical_analysis"],
    )

    session.add(move_analysis)
    return move_analysis


def resolve_player_identity(session, platform, username):
    if not username:
        return None

    account = (
        session.query(PlayerAccount)
        .filter_by(
            platform=platform,
            username=username,
        )
        .first()
    )

    if account:
        return account.player_id

    return None


def get_player_move_analyses(session, player_id):
    statement = (
        select(
            Game.game_id,
            Game.date,
            Game.white_player,
            Game.black_player,
            Game.white_player_id,
            Game.black_player_id,
            Position.position_id,
            Position.ply,
            Position.move_san,
            MoveAnalysis.player,
            MoveAnalysis.evaluation_loss,
            MoveAnalysis.classification,
            MoveAnalysis.tactical_analysis,
        )
        .join(
            Position,
            Position.game_id == Game.game_id,
        )
        .join(
            MoveAnalysis,
            MoveAnalysis.position_id == Position.position_id,
        )
        .where(
            (Game.white_player_id == player_id)
            | (Game.black_player_id == player_id)
        )
        .order_by(
            Game.date,
            Game.game_id,
            Position.ply,
        )
    )

    return session.execute(statement).all()


def get_player_move_summary(session, player_id):
    rows = get_player_move_analyses(
        session,
        player_id,
    )

    summary = {
        "total_moves": 0,
        "good": 0,
        "inaccuracy": 0,
        "mistake": 0,
        "blunder": 0,
        "average_evaluation_loss": 0.0,
        "games": {},
    }

    total_loss = 0.0

    for row in rows:

        if row.player == "White":
            is_player_move = (
                row.white_player_id == player_id
            )
        else:
            is_player_move = (
                row.black_player_id == player_id
            )

        if not is_player_move:
            continue

        # -------------------------
        # Overall player summary
        # -------------------------

        summary["total_moves"] += 1

        classification = row.classification

        if classification in summary:
            summary[classification] += 1

        total_loss += row.evaluation_loss

        # -------------------------
        # Game-level summary
        # -------------------------

        if row.game_id not in summary["games"]:
            summary["games"][row.game_id] = {
                "game_id": row.game_id,
                "date": row.date,
                "white_player": row.white_player,
                "black_player": row.black_player,
                "total_moves": 0,
                "good": 0,
                "inaccuracy": 0,
                "mistake": 0,
                "blunder": 0,
                "average_evaluation_loss": 0.0,
                "moves": [],
            }

        game_summary = summary["games"][row.game_id]

        game_summary["total_moves"] += 1

        if classification in game_summary:
            game_summary[classification] += 1

        game_summary["moves"].append({
            "position_id": row.position_id,
            "ply": row.ply,
            "move": row.move_san,
            "classification": row.classification,
            "evaluation_loss": row.evaluation_loss,
            "tactical_analysis": row.tactical_analysis,
        })

    # Overall average
    if summary["total_moves"] > 0:
        summary["average_evaluation_loss"] = (
            total_loss / summary["total_moves"]
        )

    # Calculate average for each game
    for game_summary in summary["games"].values():

        game_total_loss = sum(
            move["evaluation_loss"]
            for move in game_summary["moves"]
        )

        if game_summary["total_moves"] > 0:
            game_summary["average_evaluation_loss"] = (
                game_total_loss
                / game_summary["total_moves"]
            )

    return summary


def get_player_tactical_summary(session, player_id):
    rows = get_player_move_analyses(
        session,
        player_id,
    )

    summary = {
        "newly_attacked_pieces": 0,
        "outnumbered_pieces": 0,
        "by_piece": {},
        "games": {},
    }

    for row in rows:

        # Only analyze moves made by our player.
        if row.player == "White":
            is_player_move = (
                row.white_player_id == player_id
            )
        else:
            is_player_move = (
                row.black_player_id == player_id
            )

        if not is_player_move:
            continue

        tactical = row.tactical_analysis or {}

        attacked_pieces = tactical.get(
            "new_attacked_pieces",
            [],
        )

        for piece in attacked_pieces:

            summary["newly_attacked_pieces"] += 1

            if piece.get("is_outnumbered"):
                summary["outnumbered_pieces"] += 1

            piece_symbol = piece.get("piece")

            if piece_symbol:
                summary["by_piece"][piece_symbol] = (
                    summary["by_piece"].get(piece_symbol, 0) + 1
                )

    return summary



def get_player_tactical_mistakes(session, player_id):
    rows = get_player_move_analyses(
        session,
        player_id,
    )

    results = []

    for row in rows:

        # Only consider moves made by our player.
        if row.player == "White":
            is_player_move = (
                row.white_player_id == player_id
            )
        else:
            is_player_move = (
                row.black_player_id == player_id
            )

        if not is_player_move:
            continue

        # Only look at moves that actually lost evaluation.
        if row.classification == "good":
            continue

        tactical = row.tactical_analysis or {}

        attacked_pieces = tactical.get(
            "new_attacked_pieces",
            [],
        )

        if not attacked_pieces:
            continue

        results.append({
            "game_id": row.game_id,
            "position_id": row.position_id,
            "ply": row.ply,
            "move": row.move_san,
            "classification": row.classification,
            "evaluation_loss": row.evaluation_loss,
            "new_attacked_pieces": attacked_pieces,
        })

    return results

def get_player_tactical_patterns(session, player_id):
    mistakes = get_player_tactical_mistakes(
        session,
        player_id,
    )

    patterns = {}

    for mistake in mistakes:
        game_id = mistake["game_id"]

        for piece in mistake["new_attacked_pieces"]:
            piece_symbol = piece["piece"]

            key = (game_id, piece_symbol)

            if key not in patterns:
                patterns[key] = {
                    "game_id": game_id,
                    "piece": piece_symbol,
                    "count": 0,
                    "outnumbered_count": 0,
                    "moves": [],
                }

            patterns[key]["count"] += 1

            if piece["is_outnumbered"]:
                patterns[key]["outnumbered_count"] += 1

            patterns[key]["moves"].append({
                "position_id": mistake["position_id"],
                "ply": mistake["ply"],
                "move": mistake["move"],
                "classification": mistake["classification"],
                "evaluation_loss": mistake["evaluation_loss"],
                "square": piece["square"],
            })

    return list(patterns.values())