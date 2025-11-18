from app import db
from app.api.models import PlayedGames, AnsweredClues, Clues, AnswerState
from app import rq, create_app

@rq.job
def calculate_scores(played_game_id):
    """
    Task to calculate scores for a completed game.
    """
    app = create_app()
    with app.app_context():
        game = PlayedGames.query.get(played_game_id)
        if not game:
            raise ValueError(f"PlayedGame with id {played_game_id} does not exist.")

        # Get all answered clues, join to the clues table to get more info
        answered_clues = db.session.query(AnsweredClues).join(Clues).filter(AnsweredClues.played_game_id == played_game_id).all()

        def filter_clues(round_name, condition):
            return [clue for clue in answered_clues if clue.clue.round == round_name and condition(clue)]

        # Use answer_state enum for accurate categorization
        # CORRECT answers
        round1_correct = filter_clues('J!', lambda clue: clue.answer_state == AnswerState.CORRECT)
        round2_correct = filter_clues('DJ!', lambda clue: clue.answer_state == AnswerState.CORRECT)
        
        # INCORRECT for Coryat: only INCORRECT and TIMEOUT_AFTER_BUZZ (not TIMEOUT_BEFORE_BUZZ)
        # But for counting stats, only count INCORRECT (timeouts are separate)
        round1_incorrect = filter_clues('J!', lambda clue: clue.answer_state == AnswerState.INCORRECT)
        round2_incorrect = filter_clues('DJ!', lambda clue: clue.answer_state == AnswerState.INCORRECT)
        
        # For Coryat calculation, we need both INCORRECT and TIMEOUT_AFTER_BUZZ
        round1_incorrect_for_coryat = filter_clues('J!', lambda clue: clue.answer_state in [AnswerState.INCORRECT, AnswerState.TIMEOUT_AFTER_BUZZ])
        round2_incorrect_for_coryat = filter_clues('DJ!', lambda clue: clue.answer_state in [AnswerState.INCORRECT, AnswerState.TIMEOUT_AFTER_BUZZ])
        
        # SKIPPED: TIMEOUT_BEFORE_BUZZ and SKIPPED (do not affect Coryat score)
        round1_skipped = filter_clues('J!', lambda clue: clue.answer_state in [AnswerState.TIMEOUT_BEFORE_BUZZ, AnswerState.SKIPPED])
        round2_skipped = filter_clues('DJ!', lambda clue: clue.answer_state in [AnswerState.TIMEOUT_BEFORE_BUZZ, AnswerState.SKIPPED])

        def calculate_coryat_score(correct_clues, incorrect_clues):
            return sum(clue.clue.value for clue in correct_clues) - sum(clue.clue.value for clue in incorrect_clues if not clue.clue.daily_double)

        game.coryat_score_round1 = calculate_coryat_score(round1_correct, round1_incorrect_for_coryat)
        game.coryat_score_round2 = calculate_coryat_score(round2_correct, round2_incorrect_for_coryat)
        game.coryat_score_total = game.coryat_score_round1 + game.coryat_score_round2

        game.round1_correct = len(round1_correct)
        game.round1_incorrect = len(round1_incorrect)
        game.round1_skipped = len(round1_skipped)
        game.round2_correct = len(round2_correct)
        game.round2_incorrect = len(round2_incorrect)
        game.round2_skipped = len(round2_skipped)

        game.final_correct = next((clue.answered_correctly for clue in answered_clues if clue.clue.round == 'FJ!'), None)

        # Save the updated game to the database
        db.session.commit()

        print(f"Scores calculated for game {played_game_id}")