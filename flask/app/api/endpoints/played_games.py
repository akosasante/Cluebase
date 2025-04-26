from flask import Blueprint, request, current_app
from flask_restful import Resource, Api
from app import db
from app.api.models import PlayedGames, Games
from app.api.exceptions import IdNotFoundError
from app.util import str_to_bool
from app.jobs.score_calculator import calculate_scores

# Create a Blueprint for played_games
played_games_blueprint = Blueprint('played_games', __name__, url_prefix='/played_games')
api = Api(played_games_blueprint)

class CreatePlayedGame(Resource):
    def post(self):
        """
        Endpoint to create a new PlayedGames entry.
        Request can either be a map with the game date or game id as the key.
        """

        request_data = request.get_json()
        game_id = None
        game_date = None

        if 'game_id' in request_data:
            game_id = int(request_data['game_id'])

        if 'game_date' in request_data:
            game_date = request_data['game_date']

        if not game_id and not game_date:
            return {
                'status': 'failure',
                'error': 'Game_id or game_date is required.'
            }, 400

        try:
            # Check for valid game by either id or date
            game = Games.query.get(game_id) if game_id else Games.query.filter_by(air_date=game_date).first()

            if not game:
                return {
                    'status': 'failure',
                    'error': f'Game with id {game_id} / date {game_date} does not exist.'
                }, 400

            # Check for existing unfinished game
            unfinished_game = PlayedGames.query.filter_by(game_id=game.id, completed=False).first()

            if unfinished_game:
                return {
                    'status': 'failure',
                    'error': f'An unfinished game already exists for game_id {game_id}.'
                }, 400


            # Create a new PlayedGames entry
            new_game = PlayedGames(
                game_id=game.id,
                game_date=game.air_date,
                date_played=db.func.now(),
                round1_correct=0,
                round1_incorrect=0,
                round1_skipped=0,
                round2_correct=0,
                round2_incorrect=0,
                round2_skipped=0,
                final_correct=False,
                coryat_score_round1=0,
                coryat_score_round2=0,
                coryat_score_total=0,
                completed=False
            )

            # Save to the database
            db.session.add(new_game)
            db.session.commit()

            return {
                'status': 'success',
                'data': new_game.to_json()
            }, 201

        except Exception as e:
            return {
                'status': 'failure',
                'error': repr(e)
            }, 500

class UpdatePlayedGame(Resource):
    def put(self, id):
        """
        Endpoint to update a PlayedGames entry by ID.
        """
        request_data = request.get_json()

        try:
            game = PlayedGames.query.get(id)
            if not game:
                raise IdNotFoundError(f'PlayedGame with id {id} does not exist.')

            # Update the game with the request data
            for key, value in request_data.items():
                if hasattr(game, key):
                    setattr(game, key, value)

            if game.completed:
                calculate_scores.queue(game.id)

            db.session.commit()

            return {
                'status': 'success',
                'data': game.to_json()
            }, 200

        except Exception as e:
            return {
                'status': 'failure',
                'error': repr(e)
            }, 500


class ListPlayedGames(Resource):
    def get(self):
        """
        Endpoint to list all played games.
        Supports optional filters for completed and game_id.
        """
        completed = request.args.get('completed')
        game_id = request.args.get('game_id')

        try:
            query = PlayedGames.query

            if completed is not None:
                query = query.filter_by(completed=str_to_bool(completed))

            if game_id:
                query = query.filter_by(game_id=game_id)

            games = query.all()

            return {
                'status': 'success',
                'data': [game.to_json() for game in games]
            }, 200

        except Exception as e:
            return {
                'status': 'failure',
                'error': repr(e)
            }, 500


class PlayedGameById(Resource):
    def get(self, id):
        """
        Endpoint to retrieve a specific PlayedGames entry by ID.
        """
        try:
            game = PlayedGames.query.get(id)
            if not game:
                raise IdNotFoundError(f'PlayedGame with id {id} does not exist.')

            return {
                'status': 'success',
                'data': game.to_json()
            }, 200

        except Exception as e:
            return {
                'status': 'failure',
                'error': repr(e)
            }, 400


# Register resources with the API
api.add_resource(CreatePlayedGame, '/')
api.add_resource(UpdatePlayedGame, '/<int:id>')
api.add_resource(ListPlayedGames, '/')
api.add_resource(PlayedGameById, '/<int:id>')