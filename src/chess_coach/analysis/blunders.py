from chess_coach.analysis.tactics import analyze_move_tactics

def classify_move(
    eval_before: float,
    eval_after: float,
    player: str,
):
    if player == "White":
        evaluation_loss = eval_before - eval_after
    else:
        evaluation_loss = eval_after - eval_before

    if evaluation_loss >= 2.0:
        classification = "blunder"
    elif evaluation_loss >= 1.0:
        classification = "mistake"
    elif evaluation_loss >= 0.5:
        classification = "inaccuracy"
    else:
        classification = "good"

    return {
        "evaluation_loss": evaluation_loss,
        "classification": classification,
    }
    
def detect_mistakes(rows):
    mistakes = []

    for i in range(1, len(rows)):
        previous_position, previous_analysis = rows[i - 1]
        current_position, current_analysis = rows[i]

        if previous_position.game_id != current_position.game_id:
            continue

        eval_before = previous_analysis.evaluation
        eval_after = current_analysis.evaluation

        player = (
            "White"
            if current_position.ply % 2 == 1
            else "Black"
        )

        result = classify_move(
            eval_before,
            eval_after,
            player,
        )

        mistakes.append({
            "position_id": current_position.position_id,
            "ply": current_position.ply,
            "player": player,
            "move": current_position.move_san,
            "eval_before": eval_before,
            "eval_after": eval_after,
            "evaluation_loss": result["evaluation_loss"],
            "classification": result["classification"],
        })



def analyze_move(
    board_before,
    move,
    eval_before,
    eval_after,
    ply,
):
    player = "White" if ply % 2 == 1 else "Black"

    result = classify_move(
        eval_before,
        eval_after,
        player,
    )

    tactical_analysis = analyze_move_tactics(
        board_before,
        move,
    )

    return {
        "ply": ply,
        "player": player,
        "move": move.uci(),
        "eval_before": eval_before,
        "eval_after": eval_after,
        "evaluation_loss": result["evaluation_loss"],
        "classification": result["classification"],
        "tactical_analysis": tactical_analysis,
    }
    
    
def analyze_game_moves(game, positions, analyses):
    board = game.board()
    results = []

    for i, move in enumerate(game.mainline_moves()):
        ply = i + 1

        # We don't have an evaluation for the initial position,
        # so move 1 cannot be compared.
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