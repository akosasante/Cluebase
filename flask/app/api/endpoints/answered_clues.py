from flask import Blueprint, request
from flask_restful import Resource, Api
from app import db
from app.api.models import AnsweredClues
from app.api.exceptions import IdNotFoundError
from app.util import str_to_bool

# Create a Blueprint for answered_clues
answered_clues_blueprint = Blueprint('answered_clues', __name__, url_prefix='/answered_clues')
api = Api(answered_clues_blueprint)


class AnsweredCluesList(Resource):
    def get(self):
        """
        Endpoint to list all answered clues.
        Supports optional filters for `played_game_id` and `answered_correctly`.
        """
        played_game_id = request.args.get('played_game_id')
        answered_correctly = request.args.get('answered_correctly')

        try:
            query = AnsweredClues.query

            if played_game_id:
                query = query.filter_by(played_game_id=played_game_id)

            if answered_correctly is not None:
                query = query.filter_by(answered_correctly=str_to_bool(answered_correctly))

            answered_clues = query.all()

            return {
                'status': 'success',
                'data': [clue.to_json() for clue in answered_clues]
            }, 200

        except Exception as e:
            return {
                'status': 'failure',
                'error': repr(e)
            }, 500


class CreateAnsweredClue(Resource):
    def post(self):
        """
        Endpoint to create a new answered clue.
        Validates that the combination of `played_game_id` and `clue_id` is unique.
        """
        data = request.get_json()

        # Validate input
        played_game_id = data.get('played_game_id')
        clue_id = data.get('clue_id')
        answered_correctly = data.get('answered_correctly')

        if not played_game_id or not clue_id or answered_correctly is None:
            return {
                'status': 'failure',
                'error': 'played_game_id, clue_id, and answered_correctly are required.'
            }, 400

        try:
            # Check for uniqueness
            existing_clue = AnsweredClues.query.filter_by(
                played_game_id=played_game_id,
                clue_id=clue_id
            ).first()

            if existing_clue:
                return {
                    'status': 'failure',
                    'error': f'An answered clue already exists for played_game_id {played_game_id} and clue_id {clue_id}.'
                }, 400

            # Create a new AnsweredClues entry
            new_clue = AnsweredClues(
                played_game_id=int(played_game_id),
                clue_id=int(clue_id),
                answered_correctly=str_to_bool(answered_correctly)
            )

            # Save to the database
            db.session.add(new_clue)
            db.session.commit()

            return {
                'status': 'success',
                'data': new_clue.to_json()
            }, 201

        except Exception as e:
            return {
                'status': 'failure',
                'error': repr(e)
            }, 500


# Register resources with the API
api.add_resource(AnsweredCluesList, '/')
api.add_resource(CreateAnsweredClue, '/')