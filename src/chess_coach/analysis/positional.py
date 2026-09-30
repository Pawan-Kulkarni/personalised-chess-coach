
import chess


def get_pawn_structure(board: chess.Board):
    """
    Analyze the pawn structure for both sides.

    Detects:
        - doubled pawns
        - isolated pawns
        - pawn islands
        - passed pawns
        - backward pawns
    """

    # This is the structure that we will return.
    structure = {
        "white": {
            "doubled": [],
            "isolated": [],
            "pawn_islands": [],
            "passed": [],
            "backward": [],
        },
        "black": {
            "doubled": [],
            "isolated": [],
            "pawn_islands": [],
            "passed": [],
            "backward": [],
        },
    }

    # Analyze White and Black separately.
    for color in [chess.WHITE, chess.BLACK]:

        # Convert True/False into "white" / "black".
        color_name = (
            "white"
            if color == chess.WHITE
            else "black"
        )

        # Get all pawns belonging to this color.
        pawn_squares = list(
            board.pieces(chess.PAWN, color)
        )

        # -------------------------------------------------
        # Group pawns by file
        # -------------------------------------------------

        pawns_by_file = {}

        for square in pawn_squares:

            # Get the file number of this pawn.
            file = chess.square_file(square)

            # Create an empty list if this is the first
            # pawn we have seen on this file.
            pawns_by_file.setdefault(
                file,
                [],
            )

            # Add the pawn to its file.
            pawns_by_file[file].append(square)

        # -------------------------------------------------
        # Detect doubled pawns
        # -------------------------------------------------

        for file, pawns in pawns_by_file.items():

            # More than one pawn on the same file
            # means doubled pawns.
            if len(pawns) > 1:

                structure[color_name]["doubled"].append({
                    "file": chess.FILE_NAMES[file],
                    "squares": [
                        chess.square_name(square)
                        for square in pawns
                    ],
                })

        # -------------------------------------------------
        # Detect isolated pawns
        # -------------------------------------------------

        for file, pawns in pawns_by_file.items():

            # Find the files immediately next to
            # the current file.
            neighboring_files = []

            if file > 0:
                neighboring_files.append(file - 1)

            if file < 7:
                neighboring_files.append(file + 1)

            # Check whether there is at least one
            # friendly pawn on either neighboring file.
            has_neighboring_pawn = any(
                neighboring_file in pawns_by_file
                for neighboring_file in neighboring_files
            )

            # If there is NO friendly pawn on either
            # adjacent file, every pawn on this file
            # is isolated.
            if not has_neighboring_pawn:

                structure[color_name]["isolated"].append({
                    "file": chess.FILE_NAMES[file],
                    "squares": [
                        chess.square_name(square)
                        for square in pawns
                    ],
                })

        # -------------------------------------------------
        # Detect pawn islands
        # -------------------------------------------------

        # Get all files containing at least one pawn.
        pawn_files = sorted(pawns_by_file.keys())

        # Temporarily hold the current island.
        current_island = []

        for file in pawn_files:

            # Start the first island.
            if not current_island:
                current_island.append(file)
                continue

            # Consecutive files belong to the same island.
            if file == current_island[-1] + 1:
                current_island.append(file)

            else:
                # We found a gap, so the current island
                # is finished.
                structure[color_name]["pawn_islands"].append({
                    "files": [
                        chess.FILE_NAMES[f]
                        for f in current_island
                    ],
                })

                # Start a new island.
                current_island = [file]

        # Add the final island.
        if current_island:

            structure[color_name]["pawn_islands"].append({
                "files": [
                    chess.FILE_NAMES[f]
                    for f in current_island
                ],
            })

        # -------------------------------------------------
        # Detect passed pawns
        # -------------------------------------------------

        # Get all enemy pawn squares.
        enemy_pawn_squares = board.pieces(
            chess.PAWN,
            not color,
        )

        # Check every pawn belonging to the current side.
        for pawn_square in pawn_squares:

            pawn_file = chess.square_file(pawn_square)
            pawn_rank = chess.square_rank(pawn_square)

            # Assume the pawn is passed until we find
            # an enemy pawn that prevents it from being passed.
            is_passed = True

            for enemy_square in enemy_pawn_squares:

                enemy_file = chess.square_file(enemy_square)
                enemy_rank = chess.square_rank(enemy_square)

                # Only same or adjacent files matter.
                file_difference = abs(
                    enemy_file - pawn_file
                )

                if file_difference > 1:
                    continue

                # Determine whether the enemy pawn is ahead.
                if color == chess.WHITE:
                    enemy_is_ahead = enemy_rank > pawn_rank
                else:
                    enemy_is_ahead = enemy_rank < pawn_rank

                if enemy_is_ahead:
                    is_passed = False
                    break

            # No enemy pawn ahead on the same or adjacent
            # file means this is a passed pawn.
            if is_passed:

                structure[color_name]["passed"].append({
                    "file": chess.FILE_NAMES[pawn_file],
                    "square": chess.square_name(pawn_square),
                })

        # -------------------------------------------------
        # Detect backward pawns
        # -------------------------------------------------
        #
        # Our definition:
        #
        # A pawn can be backward when:
        #
        # 1. It has at least one friendly pawn on an
        #    adjacent file.
        #
        # 2. ALL of those adjacent friendly pawns are
        #    more advanced than the candidate pawn.
        #
        # 3. The square directly in front of the candidate
        #    pawn is controlled by an enemy pawn.
        #
        # The "ALL" condition is important.
        #
        # Example:
        #
        #     e6  f7  g7
        #
        # f7 is NOT backward because:
        #
        #     e6 -> more advanced
        #     g7 -> NOT more advanced
        #
        # Therefore, g7 prevents f7 from satisfying our
        # backward-pawn definition.
        # -------------------------------------------------

        opponent_color = not color

        for square in pawn_squares:

            # These MUST be calculated inside this loop
            # because they belong to the current candidate pawn.
            file_index = chess.square_file(square)
            rank_index = chess.square_rank(square)

            # -------------------------------------------------
            # Find ALL friendly pawns on adjacent files.
            # -------------------------------------------------

            neighboring_pawns = []

            for adjacent_file in [
                file_index - 1,
                file_index + 1,
            ]:

                # Ignore files outside the board.
                if adjacent_file < 0 or adjacent_file > 7:
                    continue

                # Find friendly pawns on this adjacent file.
                for neighboring_square in board.pieces(
                    chess.PAWN,
                    color,
                ):

                    if (
                        chess.square_file(neighboring_square)
                        != adjacent_file
                    ):
                        continue

                    neighboring_pawns.append(
                        neighboring_square
                    )

            # A candidate pawn must have at least one
            # friendly pawn on an adjacent file.
            if not neighboring_pawns:
                continue

            # -------------------------------------------------
            # Check whether ALL adjacent friendly pawns are
            # more advanced than the candidate pawn.
            # -------------------------------------------------

            all_neighbors_more_advanced = True

            for neighboring_square in neighboring_pawns:

                neighboring_rank = chess.square_rank(
                    neighboring_square
                )

                # White moves toward higher ranks.
                if color == chess.WHITE:

                    is_more_advanced = (
                        neighboring_rank > rank_index
                    )

                # Black moves toward lower ranks.
                else:

                    is_more_advanced = (
                        neighboring_rank < rank_index
                    )

                # If even ONE adjacent friendly pawn is
                # not more advanced, this pawn is not backward.
                if not is_more_advanced:

                    all_neighbors_more_advanced = False
                    break

            if not all_neighbors_more_advanced:
                continue

            # -------------------------------------------------
            # Find the square directly in front of the pawn.
            # -------------------------------------------------

            if color == chess.WHITE:

                front_square = chess.square(
                    file_index,
                    rank_index + 1,
                )

            else:

                front_square = chess.square(
                    file_index,
                    rank_index - 1,
                )

            # Make sure the front square is on the board.
            if front_square not in chess.SQUARES:
                continue

            # -------------------------------------------------
            # Check whether an enemy pawn controls the square
            # directly in front of our candidate pawn.
            # -------------------------------------------------

            enemy_pawn_attackers = board.attackers(
                opponent_color,
                front_square,
            )

            has_enemy_pawn_control = any(
                board.piece_at(attacker) is not None
                and board.piece_at(attacker).piece_type == chess.PAWN
                for attacker in enemy_pawn_attackers
            )

            if not has_enemy_pawn_control:
                continue

            # -------------------------------------------------
            # We have found a backward pawn.
            # -------------------------------------------------

            structure[color_name]["backward"].append({
                "file": chess.FILE_NAMES[file_index],
                "square": chess.square_name(square),
            })

    return structure

def analyze_pawn_structure_change(board_before, move, player_color):
    """
    Analyze pawn-structure consequences of a move.

    We examine both sides:

        player:
            The side making the move.

        opponent:
            The other side.

    This gives us two kinds of information:

        1. Did my move create a pawn weakness for me?
        2. Did my move induce a pawn weakness for my opponent?

    These are only structural signals.
    They are NOT automatically good or bad.
    """

    # Get pawn structure before the move.
    structure_before = get_pawn_structure(board_before)

    # Create a copy so we don't modify the original board.
    board_after = board_before.copy()

    # Play the move on the copied board.
    board_after.push(move)

    # Get pawn structure after the move.
    structure_after = get_pawn_structure(board_after)

    # Identify the player making the move.
    # player_color tells us which side belongs to
    # the user whose game we are analyzing.
    #
    # It is NOT necessarily the side making the move.
    #
    # Example:
    #     User = White
    #     Move = ...Rxg3
    #
    # Black is the mover, but White is still the player.

    opponent_color = (
        "black"
        if player_color == "white"
        else "white"
    )

    changes = {
    "player": {
        "new_doubled": [],
        "new_isolated": [],
        "new_passed": [],
        "pawn_island_change": {
            "before": 0,
            "after": 0,
            "change": 0,
        },
    },
    "opponent": {
        "new_doubled": [],
        "new_isolated": [],
        "new_passed": [],
        "pawn_island_change": {
            "before": 0,
            "after": 0,
            "change": 0,
        },
    },
    }

    # Analyze both sides separately.
    for perspective, color in [
        ("player", player_color),
        ("opponent", opponent_color),
    ]:

        # ----------------------------------------
        # DOUBLED PAWNS
        # ----------------------------------------

        # Record files that already had doubled pawns
        # before the move.
        doubled_before = {
            item["file"]
            for item in structure_before[color]["doubled"]
        }

        # Look for files that become doubled after the move.
        for item in structure_after[color]["doubled"]:

            if item["file"] not in doubled_before:

                changes[perspective]["new_doubled"].append({
                    "file": item["file"],
                    "squares": item["squares"],
                })

        # ----------------------------------------
        # ISOLATED PAWNS
        # ----------------------------------------

        # Compare isolated pawns by FILE rather than square.
        #
        # This is important because an isolated pawn can move:
        #
        #     e4 → e5
        #
        # without actually becoming a new isolated pawn.
        isolated_before = {
            item["file"]
            for item in structure_before[color]["isolated"]
        }

        # Find files that have newly become isolated.
        for item in structure_after[color]["isolated"]:

            if item["file"] not in isolated_before:

                changes[perspective]["new_isolated"].append({
                    "file": item["file"],
                    "squares": item["squares"],
                })
        # ---------------------------------------------------------
        # NEW PASSED PAWNS
        # ---------------------------------------------------------
        #
        # A pawn is "newly passed" if:
        #
        #   1. It is NOT a passed pawn before the move
        #   2. It IS a passed pawn after the move
        #
        # We compare the pawn's square so that we can identify
        # exactly which pawn became passed.
        # ---------------------------------------------------------

        for color in ["white", "black"]:

            # Get passed pawns before the move.
            passed_before = structure_before[color]["passed"]

            # Get passed pawns after the move.
            passed_after = structure_after[color]["passed"]

            # Convert the squares into sets so we can compare them easily.
            before_squares = {
                pawn["square"]
                for pawn in passed_before
            }

            # A pawn is newly passed if its square appears after the move
            # but was not present before the move.
            new_passed = [
                pawn
                for pawn in passed_after
                if pawn["square"] not in before_squares
            ]

            # Store the result under either player or opponent.
            if color == player_color:
                changes["player"]["new_passed"] = new_passed
            else:
                changes["opponent"]["new_passed"] = new_passed
        # ----------------------------------------
        # PAWN ISLANDS
        # ----------------------------------------
        #
        # Unlike doubled and isolated pawns, where
        # we are interested in newly created structures,
        # pawn islands are best represented by their count.
        #
        # Example:
        #
        # Before:
        #     a b c     f g
        #
        #     2 islands
        #
        # After:
        #     a b c     e f g
        #
        #     2 islands
        #
        # The actual pawn structure changed, but the
        # number of islands did not.
        #
        # Another example:
        #
        # Before:
        #     a b c d e
        #
        #     1 island
        #
        # After:
        #     a b     d e
        #
        #     2 islands
        #
        # Now the number of islands increased by 1.

        # Get the number of pawn islands before the move.
        pawn_islands_before = len(
            structure_before[color]["pawn_islands"]
        )

        # Get the number of pawn islands after the move.
        pawn_islands_after = len(
            structure_after[color]["pawn_islands"]
        )

        # Store the before/after counts and the difference.
        changes[perspective]["pawn_island_change"] = {
            "before": pawn_islands_before,
            "after": pawn_islands_after,
            "change": (
                pawn_islands_after
                - pawn_islands_before
            ),
        }
        # ---------------------------------------------------------
        # NEW BACKWARD PAWNS
        # ---------------------------------------------------------
        #
        # We only want pawns that became backward because of this move.
        #
        # Example:
        #
        # Before:
        #     d4 is NOT backward
        #
        # Move happens
        #
        # After:
        #     d4 IS backward
        #
        # Therefore:
        #     d4 -> new_backward
        #
        # We compare the pawn's square before and after the move.
        # ---------------------------------------------------------

        for color in ["white", "black"]:

            backward_before = structure_before[color]["backward"]
            backward_after = structure_after[color]["backward"]

            before_squares = {
                pawn["square"]
                for pawn in backward_before
            }

            new_backward = [
                pawn
                for pawn in backward_after
                if pawn["square"] not in before_squares
            ]

            if color == player_color:
                changes["player"]["new_backward"] = new_backward
            else:
                changes["opponent"]["new_backward"] = new_backward

    return changes