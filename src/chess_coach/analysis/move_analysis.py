from chess_coach.analysis.blunders import analyze_move


def analyze_game_moves(game, positions, analyses):
    if len(positions) != len(analyses):
        raise ValueError(
            f"Mismatch: {len(positions)} positions but "
            f"{len(analyses)} engine analyses"
        )

    board = game.board()
    results = []

    for i, move in enumerate(game.mainline_moves()):
        ply = i + 1

        # We cannot calculate evaluation loss for the first move
        # because there is no engine evaluation of the starting position.
        if ply == 1:
            board.push(move)
            continue

        previous_analysis = analyses[i - 1]
        current_analysis = analyses[i]
        current_position = positions[i]

        result = analyze_move(
            board_before=board,
            move=move,
            eval_before=previous_analysis.evaluation,
            eval_after=current_analysis.evaluation,
            ply=ply,
        )

        result["position_id"] = current_position.position_id

        results.append(result)

        board.push(move)

    return results