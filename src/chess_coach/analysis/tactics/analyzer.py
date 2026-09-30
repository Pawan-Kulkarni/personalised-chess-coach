import chess

from chess_coach.analysis.tactics.attacks import (
    find_new_attacked_pieces,
)
from .forks import detect_fork, find_fork_opportunities



def analyze_move_tactics(board_before, move):
    """
    Analyze the tactical consequences of a move from BOTH perspectives.

    Analyzes:
        - newly attacked pieces
        - forks

    The result is divided into:
        player   -> side that made the move
        opponent -> side responding to the move
    """

    # The side whose turn it is before the move is the player
    # who is making this move.
    mover = board_before.turn

    player_color = (
        "white"
        if mover == chess.WHITE
        else "black"
    )

    opponent_color = (
        "black"
        if mover == chess.WHITE
        else "white"
    )

    # ---------------------------------------------------------
    # NEW ATTACKS
    # ---------------------------------------------------------

    new_attacked = find_new_attacked_pieces(
        board_before,
        move
    )

    player_attacked = [
        item
        for item in new_attacked
        if item["color"] == player_color
    ]

    opponent_attacked = [
        item
        for item in new_attacked
        if item["color"] == opponent_color
    ]

    # ---------------------------------------------------------
    # FORKS
    # ---------------------------------------------------------

    # Did the current move itself create a fork?
    fork_result = detect_fork(
        board_before,
        move
    )

    # Did the opponent already have a fork opportunity
    # before the current move?
    opponent_opportunities_before = find_fork_opportunities(
        board_before,
        chess.BLACK if mover == chess.WHITE else chess.WHITE,
    )

    # Create the position after the current move.
    board_after = board_before.copy()
    board_after.push(move)

    # Does the opponent now have a fork opportunity?
    opponent_opportunities_after = find_fork_opportunities(
        board_after,
        chess.BLACK if mover == chess.WHITE else chess.WHITE,
    )

    fork_analysis = {
        "player": {
            "created": fork_result["is_fork"],
            "allowed": False,
        },

        "opponent": {
            "created": False,

            # The current move "allowed" a fork only if:
            #
            #   1. opponent had no fork opportunity before
            #   2. opponent has one after the move
            #
            # Therefore the current move created the opportunity.
            "allowed": (
                len(opponent_opportunities_before) == 0
                and len(opponent_opportunities_after) > 0
            ),
        },
    }

    # ---------------------------------------------------------
    # FINAL RESULT
    # ---------------------------------------------------------

    return {
        "player": {
            "new_attacked_pieces": player_attacked,
        },

        "opponent": {
            "new_attacked_pieces": opponent_attacked,
        },

        "fork": fork_analysis,
    }

def analyze_game_tactics(game):
    """
    Analyze tactical candidates for every move in a game.

    The game is processed sequentially:

        starting position
              ↓
        analyze move 1
              ↓
        make move 1
              ↓
        analyze move 2
              ↓
        make move 2
              ↓
             ...

    For every move we store:

        - ply number
        - move in UCI notation
        - tactical analysis

    The function returns a list containing one result per move.
    """

    # Start from the initial position of the game.
    #
    # game.board() creates a board corresponding to the starting
    # position of the PGN.
    board = game.board()

    # This list will eventually contain the tactical analysis
    # for every move in the game.
    results = []

    # Iterate through every mainline move in the game.
    #
    # enumerate(..., start=1) gives us:
    #
    #     ply = 1 for White's first move
    #     ply = 2 for Black's first move
    #     ply = 3 for White's second move
    #     ...
    for ply, move in enumerate(
        game.mainline_moves(),
        start=1
    ):

        # Analyze the move using the CURRENT board position.
        #
        # This is important:
        #
        #     board = position BEFORE move
        #     move = move being played
        #
        # analyze_move_tactics() itself creates a copy when it
        # needs to examine the position after the move.
        tactical_result = analyze_move_tactics(
            board,
            move,
        )

        # Store the result for this move.
        results.append({
            "ply": ply,

            # UCI notation is convenient for machine processing.
            #
            # Example:
            #     e2e4
            #     g1f3
            #     e7e8q
            "move": move.uci(),

            # Store the complete tactical analysis.
            "tactical_analysis": tactical_result,
        })

        # IMPORTANT:
        # Only NOW do we update the board.
        #
        # This ensures that the next iteration starts from the
        # correct position.
        board.push(move)

    # Return tactical analysis for the entire game.
    return results