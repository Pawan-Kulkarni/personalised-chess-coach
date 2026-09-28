
import chess


def get_pawn_structure(board: chess.Board):
    """
    Analyze the pawn structure for both sides.

    Currently detects:
        - doubled pawns
        - isolated pawns

    We will add backward pawns separately once we define
    the chess condition more precisely.
    """

    # This is the structure that we will return.
    #
    # Example:
    #
    # {
    #     "white": {
    #         "doubled": [...],
    #         "isolated": [...],
    #         "pawn_islands": [...],
    #     },
    #     "black": {
    #         "doubled": [...],
    #         "isolated": [...],
    #         "pawn_islands": [...],
    #     }
    # }

    structure = {
    "white": {
        "doubled": [],
        "isolated": [],
        "pawn_islands": [],
        "passed": [],
    },
    "black": {
        "doubled": [],
        "isolated": [],
        "pawn_islands": [],
        "passed": [],
        
    },
}

    # Analyze White and Black separately.
    for color in [chess.WHITE, chess.BLACK]:

        # Convert True/False into something easier to read.
        color_name = (
            "white"
            if color == chess.WHITE
            else "black"
        )

        # Get all pawns belonging to this color.
        #
        # Example:
        # White pawns might be:
        # a2, b3, b4, e4, f2, g2, h2
        
        pawn_squares = list(
            board.pieces(chess.PAWN, color)
        )
        

        # -------------------------------------------------
        # Group pawns by file
        # -------------------------------------------------
        #
        # A chess file is:
        #
        # a b c d e f g h
        #
        # Internally python-chess represents them as:
        #
        # 0 1 2 3 4 5 6 7
        #
        # So something like:
        #
        # b3 -> file 1
        # b4 -> file 1
        #
        # This is useful because two pawns on the same
        # file are doubled pawns.

        pawns_by_file = {}

        for square in pawn_squares:

            # Get the file number of this pawn.
            file = chess.square_file(square)

            # If we haven't seen this file before,
            # create an empty list for it.
            pawns_by_file.setdefault(
                file,
                [],
            )

            # Add the pawn's square to that file.
            pawns_by_file[file].append(square)

        # -------------------------------------------------
        # Detect doubled pawns
        # -------------------------------------------------
        #
        # Example:
        #
        #     b4
        #     b3
        #
        # Two friendly pawns on the same file.
        #
        # That is a doubled pawn structure.

        for file, pawns in pawns_by_file.items():

            # More than one pawn on the same file
            # means doubled pawns.
            if len(pawns) > 1:

                structure[color_name]["doubled"].append({
                    # Convert file number back to:
                    # 0 -> a
                    # 1 -> b
                    # etc.
                    "file": chess.FILE_NAMES[file],

                    # Store the actual squares.
                    "squares": [
                        chess.square_name(square)
                        for square in pawns
                    ],
                })

        # -------------------------------------------------
        # Detect isolated pawns
        # -------------------------------------------------
        #
        # A pawn is isolated if it has:
        #
        # NO friendly pawn
        # on the adjacent file.
        #
        # Example:
        #
        # White pawn on e4
        #
        # If White has no pawn on:
        #
        # d-file
        # f-file
        #
        # then e4 is isolated.

        for file, pawns in pawns_by_file.items():

            # Find the files immediately next to
            # the current file.
            neighboring_files = []

            # File to the left.
            if file > 0:
                neighboring_files.append(file - 1)

            # File to the right.
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
        #
        # A pawn island is a group of pawns on
        # consecutive files.
        #
        # Example:
        #
        #     a b c     f g h
        #
        #     █ █ █     █ █ █
        #
        # This gives us two pawn islands:
        #
        #     [a,b,c]
        #     [f,g,h]
        #
        # We only care about which files contain
        # pawns, not how many pawns are on each file.

        # Get all files that contain at least one pawn.
        #
        # Example:
        #
        #     pawns on a2, b2, b3, c2, f2
        #
        # gives:
        #
        #     pawn_files = [a, b, c, f]
        #
        pawn_files = sorted(pawns_by_file.keys())

        # This will temporarily hold the files
        # belonging to the current island.
        current_island = []

        for file in pawn_files:

            # If this is the first file we are looking at,
            # start a new island.
            if not current_island:
                current_island.append(file)
                continue

            # If this file is immediately next to the
            # previous file, it belongs to the same island.
            #
            # Example:
            #
            #     b = 1
            #     c = 2
            #
            # 2 == 1 + 1
            #
            if file == current_island[-1] + 1:
                current_island.append(file)

            else:
                # There is a gap between the current file
                # and the previous file.
                #
                # Therefore the current island is finished.
                structure[color_name]["pawn_islands"].append({
                    "files": [
                        chess.FILE_NAMES[f]
                        for f in current_island
                    ],
                })

                # Start a new island.
                current_island = [file]

        # After the loop finishes, we still have one
        # unfinished island.
        #
        # Add it to the structure.
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
        #
        # A pawn is passed if there are NO enemy pawns
        # ahead of it on:
        #
        #     1. the same file
        #     2. the file immediately to the left
        #     3. the file immediately to the right
        #
        # We only care about enemy PAWNS here.
        #
        # Enemy pieces such as rooks, bishops, knights,
        # queens, or kings do NOT prevent a pawn from
        # being a passed pawn.
        #
        # Example for White:
        #
        #             Black pawns
        #             ↓
        #
        #        c6  d6  e6
        #
        #             ↑
        #        White pawn d5
        #
        # d5 is NOT passed because there is an enemy pawn
        # on one of the relevant files ahead of it.
        #
        # If those black pawns are absent, d5 is passed.
        
        # Get all enemy pawn squares.
        enemy_pawn_squares = board.pieces(
            chess.PAWN,
            not color,
        )

        # Check every pawn belonging to the current side.
        for pawn_square in pawn_squares:

            pawn_file = chess.square_file(pawn_square)
            pawn_rank = chess.square_rank(pawn_square)

            # The pawn can be blocked by the board edge.
            #
            # White moves toward increasing ranks:
            #
            #     rank 1 → rank 8
            #
            # Black moves toward decreasing ranks:
            #
            #     rank 8 → rank 1
            #
            # Therefore we only consider enemy pawns
            # that are AHEAD of the current pawn.

            is_passed = True

            for enemy_square in enemy_pawn_squares:

                enemy_file = chess.square_file(enemy_square)
                enemy_rank = chess.square_rank(enemy_square)

                # Relevant files are:
                #
                #     same file
                #     left adjacent file
                #     right adjacent file
                #
                file_difference = abs(
                    enemy_file - pawn_file
                )

                if file_difference > 1:
                    continue

                # Check whether the enemy pawn is ahead.
                #
                # White pawn:
                #     enemy pawn must be on a HIGHER rank.
                #
                # Black pawn:
                #     enemy pawn must be on a LOWER rank.

                if color == chess.WHITE:
                    enemy_is_ahead = enemy_rank > pawn_rank
                else:
                    enemy_is_ahead = enemy_rank < pawn_rank

                if enemy_is_ahead:
                    is_passed = False
                    break

            # If we found no enemy pawn ahead on the
            # same or adjacent file, this pawn is passed.
            if is_passed:

                structure[color_name]["passed"].append({
                    "file": chess.FILE_NAMES[pawn_file],
                    "square": chess.square_name(pawn_square),
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

    return changes