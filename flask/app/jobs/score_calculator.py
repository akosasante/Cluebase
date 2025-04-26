from app import db
from app.api.models import PlayedGames, AnsweredClues, Clues
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

        round1_correct = filter_clues('J!', lambda clue: clue.answered_correctly)
        round1_incorrect = filter_clues('J!', lambda clue: not clue.answered_correctly)
        round1_skipped = filter_clues('J!', lambda clue: clue.answered_correctly is None)
        round2_correct = filter_clues('DJ!', lambda clue: clue.answered_correctly)
        round2_incorrect = filter_clues('DJ!', lambda clue: not clue.answered_correctly)
        round2_skipped = filter_clues('DJ!', lambda clue: clue.answered_correctly is None)

        def calculate_coryat_score(correct_clues, incorrect_clues):
            return sum(clue.clue.value for clue in correct_clues) - sum(clue.clue.value for clue in incorrect_clues if not clue.clue.daily_double)

        game.coryat_score_round1 = calculate_coryat_score(round1_correct, round1_incorrect)
        game.coryat_score_round2 = calculate_coryat_score(round2_correct, round2_incorrect)
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