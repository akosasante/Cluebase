from flask import Blueprint, request, current_app
from flask_restful import Resource, Api
from sqlalchemy.orm import joinedload
from app import db
from app.api.models import AnsweredClues, AnswerState
from app.api.exceptions import IdNotFoundError
from app.util import str_to_bool

# Create a Blueprint for answered_clues
answered_clues_blueprint = Blueprint('answered_clues', __name__, url_prefix='/answered_clues')
api = Api(answered_clues_blueprint)


class AnsweredCluesResource(Resource):
    def get(self):
        """
        Endpoint to list all answered clues.
        Supports optional filters for `played_game_id`, `answered_correctly`, and `answer_state`.
        """
        played_game_id = request.args.get('played_game_id')
        answered_correctly = request.args.get('answered_correctly')
        answer_state = request.args.get('answer_state')

        try:
            query = AnsweredClues.query.options(joinedload(AnsweredClues.clue))

            if played_game_id:
                query = query.filter_by(played_game_id=played_game_id)

            if answered_correctly is not None:
                query = query.filter_by(answered_correctly=str_to_bool(answered_correctly))

            if answer_state:
                try:
                    answer_state_enum = AnswerState(answer_state)
                    query = query.filter_by(answer_state=answer_state_enum)
                except ValueError:
                    valid_states = [state.value for state in AnswerState]
                    return {
                        'status': 'failure',
                        'error': f'Invalid answer_state filter. Must be one of: {valid_states}'
                    }, 400

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

    def post(self):
        """
        Endpoint to create a new answered clue.
        Validates that the combination of `played_game_id` and `clue_id` is unique.
        
        Optional buzzer metrics:
        - buzz_time_ms: Time taken to buzz in (milliseconds)
        - penalties: Number of early buzz penalty events
        - penalty_time_ms: Total penalty duration (milliseconds)
        """
        data = request.get_json()

        # Validate required input
        played_game_id = data.get('played_game_id')
        clue_id = data.get('clue_id')
        answer_state = data.get('answer_state')
        answered_correctly = data.get('answered_correctly')

        # Optional buzzer metrics (Phase 2 implementation)
        buzz_time_ms = data.get('buzz_time_ms')
        penalties = data.get('penalties', 0)  # Default to 0 if not provided
        penalty_time_ms = data.get('penalty_time_ms', 0)  # Default to 0 if not provided

        if not played_game_id or not clue_id or answer_state is None:
            return {
                'status': 'failure',
                'error': 'played_game_id, clue_id, and answer_state are required.'
            }, 400

        try:
            answer_state_enum = AnswerState(answer_state)
        except ValueError:
            valid_states = [state.value for state in AnswerState]
            return {
                'status': 'failure',
                'error': f'Invalid answer_state. Must be one of: {valid_states}'
            }, 400

        try:
            answered_correctly = str_to_bool(answered_correctly)
            current_app.logger.debug(f"Converted answered_correctly to boolean: {answered_correctly}")
        except ValueError:
            answered_correctly = answer_state_enum == AnswerState.CORRECT

        # Validate buzzer metrics if provided (Phase 2 validation)
        if buzz_time_ms is not None:
            try:
                buzz_time_ms = int(buzz_time_ms)
                if buzz_time_ms < 0:
                    return {
                        'status': 'failure',
                        'error': 'buzz_time_ms must be a non-negative integer.'
                    }, 400
            except (ValueError, TypeError):
                return {
                    'status': 'failure',
                    'error': 'buzz_time_ms must be a valid integer.'
                }, 400

        try:
            penalties = int(penalties)
            if penalties < 0:
                return {
                    'status': 'failure',
                    'error': 'penalties must be a non-negative integer.'
                }, 400
        except (ValueError, TypeError):
            return {
                'status': 'failure',
                'error': 'penalties must be a valid integer.'
            }, 400

        try:
            penalty_time_ms = int(penalty_time_ms)
            if penalty_time_ms < 0:
                return {
                    'status': 'failure',
                    'error': 'penalty_time_ms must be a non-negative integer.'
                }, 400
        except (ValueError, TypeError):
            return {
                'status': 'failure',
                'error': 'penalty_time_ms must be a valid integer.'
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

            # Create a new AnsweredClues entry with buzzer metrics (Phase 2)
            new_clue = AnsweredClues(
                played_game_id=int(played_game_id),
                clue_id=int(clue_id),
                answered_correctly=answered_correctly,
                answer_state=answer_state_enum,
                buzz_time_ms=buzz_time_ms,
                penalties=penalties,
                penalty_time_ms=penalty_time_ms
            )

            # Save to the database
            db.session.add(new_clue)
            db.session.commit()

            return {
                'status': 'success',
                'data': new_clue.to_json()
            }, 201

        except Exception as e:
            current_app.logger.error(f"Error creating answered clue: {repr(e)}")
            return {
                'status': 'failure',
                'error': repr(e)
            }, 500


# Register resources with the API
api.add_resource(AnsweredCluesResource, '/')