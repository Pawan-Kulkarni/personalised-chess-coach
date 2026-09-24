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
    #     },
    #     "black": {
    #         "doubled": [...],
    #         "isolated": [...],
    #     }
    # }

    structure = {
        "white": {
            "doubled": [],
            "isolated": [],
        },
        "black": {
            "doubled": [],
            "isolated": [],
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

                for square in pawns:

                    structure[color_name]["isolated"].append(
                        chess.square_name(square)
                    )

    return structure


def analyze_pawn_structure_change(
    board_before: chess.Board,
    move: chess.Move,
):
    """
    Compare pawn structures before and after a move.

    We only report NEW doubled/isolated pawns created by
    the move. Existing pawn-structure features are ignored.
    """

    # ----------------------------------------
    # Pawn structure BEFORE the move
    # ----------------------------------------

    structure_before = get_pawn_structure(
        board_before
    )

    # ----------------------------------------
    # Create the board AFTER the move
    # ----------------------------------------

    board_after = board_before.copy()
    board_after.push(move)

    structure_after = get_pawn_structure(
        board_after
    )

    changes = {
        "new_doubled": [],
        "new_isolated": [],
    }

    # ----------------------------------------
    # Compare each color separately
    # ----------------------------------------

    for color in ["white", "black"]:

        # ------------------------------------
        # New doubled pawns
        # ------------------------------------

        doubled_before = {
            item["file"]
            for item in structure_before[color]["doubled"]
        }

        for item in structure_after[color]["doubled"]:

            # If this file wasn't doubled before,
            # the move created a new doubled structure.
            if item["file"] not in doubled_before:

                changes["new_doubled"].append({
                    "color": color,
                    "file": item["file"],
                    "squares": item["squares"],
                })

        # ------------------------------------
        # New isolated pawns
        # ------------------------------------

        isolated_before = set(
            structure_before[color]["isolated"]
        )

        for square in structure_after[color]["isolated"]:

            # If the pawn was not isolated before,
            # but is isolated after the move,
            # this move created a new isolated pawn.
            if square not in isolated_before:

                changes["new_isolated"].append({
                    "color": color,
                    "square": square,
                })

    return changes