import chess


def find_attacked_pieces(board: chess.Board):
    """
    Find all non-king pieces that are currently being attacked.

    IMPORTANT:
    This function does NOT decide whether a piece is hanging,
    losing material, or whether the position contains a blunder.

    It only collects tactical information that can be useful later.

    For every attacked piece, we record:

        - which square the piece is on
        - which piece it is
        - which side owns the piece
        - which enemy pieces are attacking it
        - which friendly pieces are defending it
        - number of attackers
        - number of defenders

    Example:

        Suppose Black has a knight on d5 and White has:
            - a bishop attacking d5
            - a queen attacking d5

        Then the knight might produce:

            {
                "square": "d5",
                "piece": "n",
                "color": "black",

                "attackers": [
                    {"piece": "B", "square": "c4"},
                    {"piece": "Q", "square": "d1"}
                ],

                "defenders": [...],

                "attacker_count": 2,
                "defender_count": 1
            }

    Later, other parts of the system can use this information to
    reason about tactical situations.

    But we should NOT conclude from attacker_count > defender_count
    alone that the piece is lost.

    For example:
        - the piece might be tactically protected
        - capturing it might be bad
        - the piece might be intentionally sacrificed
        - there might be a stronger tactical continuation

    Stockfish remains responsible for objective evaluation.
    """

    # This list will contain information about every attacked piece.
    attacked_pieces = []

    # board.piece_map() gives us every occupied square and the piece
    # sitting on that square.
    #
    # Example:
    #
    # {
    #     0: <Piece ...>,    # a1
    #     1: <Piece ...>,    # b1
    #     ...
    # }
    #
    # "square" is an integer representation of the square.
    # "piece" is a python-chess Piece object.
    for square, piece in board.piece_map().items():

        # We don't want to treat the king like an ordinary attacked piece.
        #
        # A king being attacked means CHECK, which is a different
        # tactical concept and should eventually be handled separately.
        if piece.piece_type == chess.KING:
            continue

        # Find pieces belonging to the OPPONENT that attack this square.
        #
        # piece.color:
        #     True  -> White
        #     False -> Black
        #
        # "not piece.color" therefore gives us the opposite side.
        #
        # Example:
        #     If this is a White knight,
        #     board.attackers(False, square)
        #     finds Black pieces attacking it.
        attackers = board.attackers(
            not piece.color,
            square
        )

        # Find pieces belonging to the SAME side that defend this piece.
        #
        # Example:
        #     If this is a White knight on d5,
        #     board.attackers(chess.WHITE, d5)
        #     finds White pieces defending that knight.
        defenders = board.attackers(
            piece.color,
            square
        )

        # If there is at least one attacker, this piece is tactically
        # relevant for our current analysis.
        #
        # Notice that we are NOT checking whether it is undefended.
        #
        # A piece can be attacked AND defended.
        #
        # Example:
        #     White knight on d5
        #     Black bishop attacks it
        #     White queen defends it
        #
        # It is still an attacked piece, so we record it.
        if attackers:

            # Convert the python-chess attacker squares into information
            # that is easier for the rest of our system to consume.
            #
            # For every attacking piece we store:
            #
            #     piece -> its symbol
            #     square -> human-readable square name
            #
            # Example:
            #
            #     {"piece": "B", "square": "c4"}
            attacker_details = [
                {
                    "piece": board.piece_at(attacker).symbol(),
                    "square": chess.square_name(attacker),
                }
                for attacker in attackers
            ]

            # Do the same thing for friendly pieces defending
            # the attacked piece.
            defender_details = [
                {
                    "piece": board.piece_at(defender).symbol(),
                    "square": chess.square_name(defender),
                }
                for defender in defenders
            ]

            # Store everything we know about this attacked piece.
            attacked_pieces.append({

                # Convert python-chess's square number into something
                # human-readable such as "e4", "d5", etc.
                "square": chess.square_name(square),

                # python-chess piece symbols:
                #
                # White:
                #     P N B R Q K
                #
                # Black:
                #     p n b r q k
                #
                # The king has already been excluded above.
                "piece": piece.symbol(),

                # Store the owner as a simple string because this is
                # easier to use later in JSON/database/LLM processing.
                "color": (
                    "white"
                    if piece.color == chess.WHITE
                    else "black"
                ),

                # Detailed attacker information.
                "attackers": attacker_details,

                # Detailed defender information.
                "defenders": defender_details,

                # Number of enemy pieces attacking this piece.
                "attacker_count": len(attackers),

                # Number of friendly pieces defending this piece.
                "defender_count": len(defenders),
            })

    # Return the complete list of attacked pieces.
    return attacked_pieces


def find_new_attacked_pieces(board_before, move):
    """
    Find pieces that become newly attacked after a move.

    We compare two positions:

        1. Position BEFORE the move
        2. Position AFTER the move

    If a piece was already attacked before the move,
    it is not considered "newly attacked".

    If a piece is not attacked before the move but becomes
    attacked after the move, we record it.

    IMPORTANT:
    We deliberately return newly attacked pieces belonging to
    BOTH sides.

    Why?

    Because a move can have consequences for both players.

    Example:

        White plays Bxc6.

        The move might:
            - leave one of White's pieces newly attacked
            - create a new attack against a Black piece
            - create both situations simultaneously

    The higher-level function, analyze_move_tactics(), will separate
    these into:

        player
        opponent

    We therefore keep this lower-level function neutral.
    """

    # Analyze the position before the move.
    attacked_before = find_attacked_pieces(board_before)

    # Create a copy of the board.
    #
    # We don't want to modify the caller's board because the caller
    # may still need the original position.
    board_after = board_before.copy()

    # Apply the move to our copied board.
    board_after.push(move)

    # Analyze the position after the move.
    attacked_after = find_attacked_pieces(board_after)

    # Create a set containing all squares that contained attacked
    # pieces BEFORE the move.
    #
    # Example:
    #
    #     {
    #         "d5",
    #         "f7",
    #         "h4"
    #     }
    #
    # We only need the square here because we're asking:
    #
    #     "Was the piece on this square already attacked?"
    before_squares = {
        item["square"]
        for item in attacked_before
    }

    # Find attacked pieces after the move whose squares were NOT
    # present in before_squares.
    #
    # These are our "newly attacked" pieces.
    new_attacked = [
        item
        for item in attacked_after
        if item["square"] not in before_squares
    ]

    # For every newly attacked piece, compare the number of attackers
    # with the number of defenders.
    #
    # Example:
    #
    #     attackers = 2
    #     defenders = 1
    #
    # Then:
    #
    #     is_outnumbered = True
    #
    # Again, this is only a SIGNAL.
    #
    # It does NOT mean the piece is necessarily lost.
    for item in new_attacked:
        item["is_outnumbered"] = (
            item["attacker_count"] > item["defender_count"]
        )

    return new_attacked
