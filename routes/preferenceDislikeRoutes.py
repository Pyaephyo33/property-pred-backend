from flask import Blueprint, request, jsonify
from models import db, Preferences, Dislikes, InteractionHistory, UserInformation, Property
from flask_jwt_extended import jwt_required, get_jwt_identity

preference_bp = Blueprint('preference_bp', __name__)
dislike_bp = Blueprint('dislike_bp', __name__)

# helper Function: Get the current user's interactionHistoryId
def get_user_interaction_history():
    ## get the interactionHistoryId for the authenticated user
    
    # get the userId from the JWT token
    current_user_id = get_jwt_identity()

    # retrieve the userInformationId linked to the authenticated user
    user_info = UserInformation.query.filter_by(userId=current_user_id).first()

    if not user_info:
        return None, jsonify({'message': 'UserInformation not found for the authenticated user'}), 404

    # retrieve the interaction history linked to the userInformationId
    interaction = InteractionHistory.query.filter_by(userInformationId=user_info.userInformationId).first()

    if not interaction:
        return None, jsonify({'message': 'Interaction history not found'}), 404

    return interaction.interactionHistoryId, None



# create Preference (POST)
@preference_bp.route('/', methods=['POST'])
@jwt_required()
def add_preference():
    ## add a new property to preferences
    interaction_id, error = get_user_interaction_history()
    if error:
        return error

    data = request.get_json()
    property_id = data.get('propertyId')

    # Validate property existence
    if not Property.query.get(property_id):
        return jsonify({'message': 'Property not found'}), 404

    # Prevent duplicates
    existing_preference = Preferences.query.filter_by(
        interactionHistoryId=interaction_id, propertyId=property_id
    ).first()

    if existing_preference:
        return jsonify({'message': 'Preference already exists'}), 409

    # add preference
    new_preference = Preferences(
        interactionHistoryId=interaction_id,
        propertyId=property_id
    )
    db.session.add(new_preference)
    db.session.commit()

    return jsonify({'message': 'Preference added successfully'}), 201



# create Dislike (POST)
@dislike_bp.route('/', methods=['POST'])
@jwt_required()
def add_dislike():
    ## add a new property to dislikes
    interaction_id, error = get_user_interaction_history()
    if error:
        return error

    data = request.get_json()
    property_id = data.get('propertyId')

    # validate property existence
    if not Property.query.get(property_id):
        return jsonify({'message': 'Property not found'}), 404

    # prevent duplicates
    existing_dislike = Dislikes.query.filter_by(
        interactionHistoryId=interaction_id, propertyId=property_id
    ).first()

    if existing_dislike:
        return jsonify({'message': 'Dislike already exists'}), 409

    # add dislike
    new_dislike = Dislikes(
        interactionHistoryId=interaction_id,
        propertyId=property_id
    )
    db.session.add(new_dislike)
    db.session.commit()

    return jsonify({'message': 'Dislike added successfully'}), 201


# Remove Preference (DELETE)
@preference_bp.route('/<int:preference_id>', methods=['DELETE'])
@jwt_required()
def delete_preference(preference_id):
    ## remove a preference
    interaction_id, error = get_user_interaction_history()
    if error:
        return error

    preference = Preferences.query.get(preference_id)

    if not preference or preference.interactionHistoryId != interaction_id:
        return jsonify({'message': 'Preference not found or unauthorized'}), 404

    db.session.delete(preference)
    db.session.commit()

    return jsonify({'message': 'Preference removed successfully'}), 200


# remove dislike (DELETE)
@dislike_bp.route('/<int:dislike_id>', methods=['DELETE'])
@jwt_required()
def delete_dislike(dislike_id):
    ## remove a dislike
    interaction_id, error = get_user_interaction_history()
    if error:
        return error
    
    dislike = Dislikes.query.get(dislike_id)

    if not dislike or dislike.interactionHistoryId != interaction_id:
        return jsonify({'message': 'Dislike not found or unauthorized'}), 404
    
    db.session.delete(dislike)
    db.session.commit()

    return jsonify({'message': 'Dislike removed successfully'}), 200


# list preferences (GET)
@preference_bp.route('/', methods=['GET'])
@jwt_required()
def list_preferences():
    ## list preferences for the authenticated user
    interaction_id, error = get_user_interaction_history()
    if error:
        return error
    
    preferences = Preferences.query.filter_by(interactionHistoryId = interaction_id).all()

    result = [
        {
            'preferenceId': p.preferenceId,
            'propertyId': p.propertyId
        } for p in preferences
    ]

    return jsonify(result), 200


# list dislikes (GET)
@dislike_bp.route('/', methods=['GET'])
@jwt_required()
def list_dislikes():
    ## list dislikes for the auth user
    interaction_id, error = get_user_interaction_history()
    if error:
        return error
    
    dislikes = Dislikes.query.filter_by(interactionHistoryId = interaction_id).all()

    result = [
        {
            'dislikeId': d.dislikeId,
            'propertyId': d.propertyId
        } for d in dislikes
    ]

    return jsonify(result), 200