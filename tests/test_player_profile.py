from chess_coach.database.connection import get_session

from chess_coach.database.queries import (
    get_player_move_summary,
    get_player_tactical_summary,
    get_player_tactical_mistakes,
    get_player_tactical_patterns,
)
PLAYER_ID = 1


with get_session() as session:

    # -------------------------
    # Overall player profile
    # -------------------------

    summary = get_player_move_summary(
        session,
        PLAYER_ID,
    )

    print("\nPLAYER PROFILE")
    print("=" * 40)

    for key, value in summary.items():

        # Don't print the full games dictionary here
        if key != "games":
            print(f"{key}: {value}")

    # -------------------------
    # Game-level information
    # -------------------------

    print("\nGAMES")
    print("=" * 40)

    for game_id, game in summary["games"].items():

        print(
            f"\nGame {game_id}"
        )

        print(
            f"Date: {game['date']}"
        )

        print(
            f"White: {game['white_player']}"
        )

        print(
            f"Black: {game['black_player']}"
        )

        print(
            f"Moves: {game['total_moves']}"
        )

        print(
            f"Good: {game['good']}"
        )

        print(
            f"Inaccuracies: {game['inaccuracy']}"
        )

        print(
            f"Mistakes: {game['mistake']}"
        )

        print(
            f"Blunders: {game['blunder']}"
        )

        print(
            f"Average loss: "
            f"{game['average_evaluation_loss']:.2f}"
        )

    # -------------------------
    # Tactical profile
    # -------------------------

    tactical = get_player_tactical_summary(
        session,
        PLAYER_ID,
    )

    print("\nTACTICAL PROFILE")
    print("=" * 40)

    print(
        f"Newly attacked pieces: "
        f"{tactical['newly_attacked_pieces']}"
    )

    print(
        f"Outnumbered pieces: "
        f"{tactical['outnumbered_pieces']}"
    )

    print("\nBy piece:")

    for piece, count in tactical["by_piece"].items():
        print(
            f"  {piece}: {count}"
        )
        
    tactical_mistakes = get_player_tactical_mistakes(
        session,
        PLAYER_ID,
    )

    print("\nTACTICAL MISTAKES")
    print("=" * 40)

    for mistake in tactical_mistakes:

        print(
            f"\nGame: {mistake['game_id']}"
        )

        print(
            f"Move: {mistake['move']} "
            f"(ply {mistake['ply']})"
        )

        print(
            f"Classification: "
            f"{mistake['classification']}"
        )

        print(
            f"Evaluation loss: "
            f"{mistake['evaluation_loss']:+.2f}"
        )

        print("Newly attacked pieces:")

        for piece in mistake["new_attacked_pieces"]:

            print(
                f"  {piece['piece']} "
                f"on {piece['square']} | "
                f"attackers={piece['attacker_count']} | "
                f"defenders={piece['defender_count']} | "
                f"outnumbered={piece['is_outnumbered']}"
            )
    patterns = get_player_tactical_patterns(
        session,
        PLAYER_ID,
    )

    print("\nTACTICAL PATTERNS")
    print("=" * 40)

    for pattern in patterns:

        print(
            f"\nGame {pattern['game_id']} | "
            f"Piece: {pattern['piece']}"
        )

        print(
            f"Occurrences: {pattern['count']}"
        )

        print(
            f"Outnumbered: "
            f"{pattern['outnumbered_count']}"
        )

        for move in pattern["moves"]:
            print(
                f"  {move['move']} "
                f"→ {move['classification']} "
                f"| loss={move['evaluation_loss']:+.2f} "
                f"| square={move['square']}"
            )