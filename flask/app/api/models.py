from flask_sqlalchemy import SQLAlchemy

from app import db

class Seasons(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season_name = db.Column(db.String(16))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    total_games = db.Column(db.Integer)
    games = db.relationship('Games', backref='season', lazy=True)

    def __repr__(self):
        return f'Season [id = {self.id}, season_name = {self.season_name}' + \
                f', start_date = {self.start_date}, end_date = {self.end_date}' + \
                f', total_games = {self.total_games}]'

    def to_json(self):
        return {
            'id': self.id,
            'season_name': self.season_name,
            'start_date': str(self.start_date),
            'end_date': str(self.end_date),
            'total_games': self.total_games
        }


class Contestants(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    notes = db.Column(db.String())
    games_played = db.Column(db.Integer, nullable=False)
    total_winnings = db.Column(db.Integer)

    def __repr__(self):
        return f'Contestant [id = {self.id}, name = {self.name}, ' + \
                f'notes = {self.notes}, games_played = {self.games_played}, ' + \
                f'total_winnings = {self.total_winnings}]'

    def to_json(self):
        return {
            'id' : self.id,
            'name' : self.name,
            'notes' : self.notes,
            'games_played' : self.games_played,
            'total_winnings' : self.total_winnings
        }


class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    episode_num = db.Column(db.Integer, unique=True)
    season_id = db.Column(db.Integer, db.ForeignKey('seasons.id'))
    air_date = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.String())
    contestant1 = db.Column(db.Integer, db.ForeignKey('contestants.id'))
    contestant2 = db.Column(db.Integer, db.ForeignKey('contestants.id'))
    contestant3 = db.Column(db.Integer, db.ForeignKey('contestants.id'))
    winner = db.Column(db.Integer, db.ForeignKey('contestants.id'))
    score1 = db.Column(db.Integer)
    score2 = db.Column(db.Integer)
    score3 = db.Column(db.Integer)
    clues = db.relationship('Clues', backref='game', lazy=True)

    def __repr__(self):
        return f'Game [id = {self.id}, episode_num = {self.episode_num}, ' + \
                f'season_id = {self.season_id}, air_date = {self.air_date}, notes = {self.notes}]'

    def to_json(self):
        return {
            'id' : self.id,
            'episode_num' : self.episode_num,
            'season_id' : self.season_id,
            'season_number': self.season.season_name,
            'air_date' : str(self.air_date),
            'notes' : self.notes,
            'contestant1': self.contestant1,
            'contestant2': self.contestant2,
            'contestant3' : self.contestant3,
            'winner' : self.winner,
            'score1' : self.score1,
            'score2' : self.score2,
            'score3' : self.score3
        }


class Clues(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    value = db.Column(db.Integer, nullable=False)
    daily_double = db.Column(db.Boolean, nullable=False)
    round = db.Column(db.String(), nullable=False)
    category = db.Column(db.String(), nullable=False)
    clue = db.Column(db.String(), nullable=False)
    response = db.Column(db.String(), nullable=False)
    has_media = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'Clue [id = {self.id}, game_id = {self.game_id}, ' + \
                f'value = {self.value}, daily_double = {self.daily_double, }' + \
                f'round = {self.round}, category = {self.category}, ' + \
                f'clue = {self.clue}, response = {self.response}]'

    def to_json(self):
        return {
            'id' : self.id,
            'game_id' : self.game_id,
            'value' : self.value,
            'daily_double' : self.daily_double,
            'round' : self.round,
            'category' : self.category,
            'clue' : self.clue,
            'response' : self.response,
            'has_media': self.has_media
        }

class PlayedGames(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    game_date = db.Column(db.DateTime, nullable=False)
    date_played = db.Column(db.DateTime, default=db.func.now())
    round1_correct = db.Column(db.Integer, default=0)
    round1_incorrect = db.Column(db.Integer, default=0)
    round1_skipped = db.Column(db.Integer, default=0)
    round2_correct = db.Column(db.Integer, default=0)
    round2_incorrect = db.Column(db.Integer, default=0)
    round2_skipped = db.Column(db.Integer, default=0)
    final_correct = db.Column(db.Boolean, default=False)
    coryat_score_round1 = db.Column(db.Integer, default=0)
    coryat_score_round2 = db.Column(db.Integer, default=0)
    coryat_score_total = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"PlayedGames [id = {self.id}, game_id = {self.game_id}, " + \
            f"game_date = {self.game_date}, date_played = {self.date_played}, " + \
            f"completed = {self.completed}]"

    def to_json(self):
        return {
            'id': self.id,
            'game_id': self.game_id,
            'game_date': str(self.game_date),
            'date_played': str(self.date_played),
            'round1_correct': self.round1_correct,
            'round1_incorrect': self.round1_incorrect,
            'round1_skipped': self.round1_skipped,
            'round2_correct': self.round2_correct,
            'round2_incorrect': self.round2_incorrect,
            'round2_skipped': self.round2_skipped,
            'final_correct': self.final_correct,
            'coryat_score_round1': self.coryat_score_round1,
            'coryat_score_round2': self.coryat_score_round2,
            'coryat_score_total': self.coryat_score_total,
            'completed': self.completed
        }

class AnsweredClues(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    played_game_id = db.Column(db.Integer, db.ForeignKey('played_games.id'), nullable=False)
    clue_id = db.Column(db.Integer, db.ForeignKey('clues.id'), nullable=False)
    answered_correctly = db.Column(db.Boolean, nullable=False)
    date_answered = db.Column(db.DateTime, default=db.func.now())
    clue = db.relationship('Clues', lazy=True)

    def __repr__(self):
        return f"AnsweredClues [id = {self.id}, played_game_id = {self.played_game_id}, " + \
            f"clue_id = {self.clue_id}, answered_correctly = {self.answered_correctly}, " + \
            f"date_answered = {self.date_answered}]"

    def to_json(self):
        return {
            'id': self.id,
            'played_game_id': self.played_game_id,
            'clue_id': self.clue_id,
            'answered_correctly': self.answered_correctly,
            'date_answered': str(self.date_answered)
        }