import chess

from chess_coach.analysis.positional import (
    get_pawn_structure,
    analyze_pawn_structure_change,
)


# ---------------------------------------------------------
# PLAYER CONFIGURATION
# ---------------------------------------------------------
#
# This represents the user whose game we are analyzing.
#
# IMPORTANT:
# This is NOT necessarily the side making the current move.
#
# For this test game, we are assuming:
#
#     User = White
#
# Therefore:
#
#     player_color = "white"
#
# Even when Black makes a move, "player" will still
# refer to White.
#
player_color = "white"


# ---------------------------------------------------------
# TEST 1: Check the pawn structure of the starting position
# ---------------------------------------------------------

board = chess.Board()

print("\n=== Starting Position ===")

structure = get_pawn_structure(board)

print(structure)


# ---------------------------------------------------------
# TEST 2: Test a pawn-structure change after a move
# ---------------------------------------------------------

print("\n=== Pawn Structure Change ===")

# Starting position.
board = chess.Board()

# White plays e4.
move = chess.Move.from_uci("e2e4")

changes = analyze_pawn_structure_change(
    board,
    move,
    player_color,
)

print("Move:", board.san(move))
print("Changes:")
print(changes)


# ---------------------------------------------------------
# TEST 3: Run through the actual game
# ---------------------------------------------------------

print("\n=== Real Game Pawn Structure Changes ===")

from chess_coach.chess.pgn import parse_pgn_file

games = parse_pgn_file("data/raw/test_game.pgn")
game = games[0]

board = game.board()

for ply, move in enumerate(game.mainline_moves(), start=1):

    changes = analyze_pawn_structure_change(
        board,
        move,
        player_color,
    )

    # Get pawn-island changes for both sides.
    player_island_change = (
        changes["player"]["pawn_island_change"]["change"]
    )

    opponent_island_change = (
        changes["opponent"]["pawn_island_change"]["change"]
    )

    # Only print moves where something changed.
    if (
        changes["player"]["new_doubled"]
        or changes["player"]["new_isolated"]
        or changes["opponent"]["new_doubled"]
        or changes["opponent"]["new_isolated"]
        or player_island_change != 0
        or opponent_island_change != 0
    ):
        print("\nPly:", ply)
        print("Move:", board.san(move))
        print("Changes:")
        print(changes)

    board.push(move)


# ---------------------------------------------------------
# TEST 4: Passed pawn
# ---------------------------------------------------------

print("\n=== Passed Pawn Test ===")

# White has a pawn on d5.
#
# There are no black pawns on:
#
#     c-file
#     d-file
#     e-file
#
# ahead of d5.
#
# Therefore d5 should be a passed pawn.

board = chess.Board(
    "8/8/8/3P4/8/8/8/4K3 w - - 0 1"
)

structure = get_pawn_structure(board)

print("White passed pawns:")
print(structure["white"]["passed"])


# ---------------------------------------------------------
# TEST 5: Pawn is NOT passed because of enemy pawn
# ---------------------------------------------------------

print("\n=== Non-Passed Pawn Test ===")

# White pawn is on d5.
# Black pawn is on d6.
#
# Black's pawn is:
#
#     - on the same file
#     - ahead of the White pawn
#
# Therefore d5 is NOT a passed pawn.

board = chess.Board(
    "8/8/3p4/3P4/8/8/8/4K3 w - - 0 1"
)

structure = get_pawn_structure(board)

print("White passed pawns:")
print(structure["white"]["passed"])


# ---------------------------------------------------------
# TEST 6: Pawn is NOT passed because of adjacent
# enemy pawn
# ---------------------------------------------------------

print("\n=== Adjacent Enemy Pawn Test ===")

# White pawn is on d5.
# Black pawn is on c6.
#
# The enemy pawn does not have to be on the same file.
# An enemy pawn on an adjacent file ahead of the pawn
# also prevents it from being passed.

board = chess.Board(
    "8/8/2p5/3P4/8/8/8/4K3 w - - 0 1"
)

structure = get_pawn_structure(board)

print("White passed pawns:")
print(structure["white"]["passed"])


# ---------------------------------------------------------
# TEST 7: Black passed pawn
# ---------------------------------------------------------

print("\n=== Black Passed Pawn Test ===")

# Black has a pawn on d4.
#
# There are no White pawns on:
#
#     c-file
#     d-file
#     e-file
#
# ahead of the Black pawn.
#
# Therefore d4 should be a passed pawn for Black.

# =========================================================
# Backward Pawn Test
# =========================================================

print("\n=== Backward Pawn Test ===")

# White:
#   c5 = advanced friendly pawn
#   d4 = candidate backward pawn
#
# Black:
#   e6 = controls d5
#
# Therefore d4 should be detected as backward.

board = chess.Board(
    "4k3/8/4p3/2P5/3P4/8/8/4K3 w - - 0 1"
)

structure = get_pawn_structure(board)

print("White backward pawns:")
print(structure["white"]["backward"])

board = chess.Board(
    "4k3/8/8/8/3p4/8/8/8 b - - 0 1"
)

# =========================================================
# Non-Backward Pawn Test
# =========================================================

print("\n=== Non-Backward Pawn Test ===")

# White:
#   c5 = advanced friendly pawn
#   d4 = candidate pawn
#
# But Black does NOT control d5 with a pawn.
#
# Therefore d4 should NOT be backward.

board = chess.Board(
    "4k3/8/8/2P5/3P4/8/8/4K3 w - - 0 1"
)

structure = get_pawn_structure(board)

print("White backward pawns:")
print(structure["white"]["backward"])


print("\n=== Current Backward Pawn Test ===")

# Position after 39.Qxh6+
board = chess.Board(
    "2rq1r2/1b1nbpk1/p3p2Q/1pp1P2P/6N1/3P1BP1/PPP2P2/R3R1K1 b - - 0 1"
)

structure = get_pawn_structure(board)

print("Black backward pawns:")
print(structure["black"]["backward"])

structure = get_pawn_structure(board)

print("Black passed pawns:")
print(structure["black"]["passed"])