import io
import chess.pgn

from chess_coach.analysis.blunders import analyze_game_moves


# ---------------------------------------------------------
# Create a small test game
# ---------------------------------------------------------

pgn_text = """
[Event "Move Analysis Test"]
[Site "Local"]
[Date "2026.09.29"]
[Round "1"]
[White "Pawan"]
[Black "Opponent"]
[Result "1-0"]

1. e4 e5
2. Nf3 Nc6
3. Bb5 a6
4. Ba4 Nf6
5. O-O Be7
"""

game = chess.pgn.read_game(
    io.StringIO(pgn_text)
)


# ---------------------------------------------------------
# Create mock Position objects
# ---------------------------------------------------------
#
# We only need the fields that analyze_game_moves()
# actually uses:
#
#   position_id
#   ply
#
# ---------------------------------------------------------

positions = []

for ply, move in enumerate(game.mainline_moves(), start=1):

    positions.append(
        type(
            "Position",
            (),
            {
                "position_id": ply,
                "ply": ply,
            },
        )()
    )


# ---------------------------------------------------------
# Create mock engine-analysis objects
# ---------------------------------------------------------
#
# We need one evaluation for every position.
#
# These are deliberately simple fake values.
# We are NOT testing Stockfish here.
#
# We are testing:
#
#     analyze_game_moves()
#             ↓
#        analyze_move()
#             ↓
#     tactical analysis
#             +
#     positional analysis
#
# ---------------------------------------------------------

evaluations = [
    0.2,
    0.1,
    0.3,
    0.2,
    0.4,
    0.3,
    0.5,
    0.4,
    0.6,
    0.5,
]

analyses = []

for evaluation in evaluations:

    analyses.append(
        type(
            "EngineAnalysis",
            (),
            {
                "evaluation": evaluation,
            },
        )()
    )


# ---------------------------------------------------------
# Run complete move analysis
# ---------------------------------------------------------

results = analyze_game_moves(
    game=game,
    positions=positions,
    analyses=analyses,
    player_color="white",
)


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print("\n========== MOVE ANALYSIS ==========\n")

for result in results:

    print(f"Ply: {result['position_id']}")
    print(f"Player: {result['player']}")
    print(f"Evaluation loss: {result['evaluation_loss']}")
    print(f"Classification: {result['classification']}")

    print("\nTactical analysis:")
    print(result["tactical_analysis"])

    print("\nPositional analysis:")
    print(result["positional_analysis"])

    print("\n" + "=" * 60)