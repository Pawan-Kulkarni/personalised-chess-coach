from chess_coach.analysis.blunders import classify_move

tests = [
    (2.0, 0.5),
    (1.5, 0.7),
    (0.8, 0.4),
    (1.0, 0.9),
]

for before, after in tests:
    result = classify_move(before, after,"White")

    print(
        f"Before: {before:+.1f} | "
        f"After: {after:+.1f} | "
        f"Loss: {result['evaluation_loss']:+.1f} | "
        f"{result['classification']}"
    )