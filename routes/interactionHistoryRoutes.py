from flask import Blueprint, request, jsonify
from models import InteractionHistory, UserInformation, User
from extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, and_

interaction_bp = Blueprint('interaction_bp', __name__)

# advanced search api
@interaction_bp.route('/', methods=['GET'])
def get_interactions():
    ## Retrieve interaction history with filtering options
    user_info_id = request.args.get('userInformationId')
    mbti = request.args.get('mbti')
    income_min = request.args.get('income_min')
    income_max = request.args.get('income_max')
    demographic = request.args.get('demographic')
    family_size = request.args.get('familySize')
    status = request.args.get('status')

    # Build the query dynamically
    filters = []
    if user_info_id:
        filters.append(InteractionHistory.userInformationId == int(user_info_id))
    if mbti:
        filters.append(InteractionHistory.mbti.ilike(f"%{mbti}%"))
    if income_min and income_max:
        filters.append(and_(
            InteractionHistory.income >= float(income_min),
            InteractionHistory.income <= float(income_max)
        ))
    elif income_min:
        filters.append(InteractionHistory.income >= float(income_min))
    elif income_max:
        filters.append(InteractionHistory.income <= float(income_max))
    if demographic:
        filters.append(InteractionHistory.demographic.ilike(f"%{demographic}%"))
    if family_size:
        filters.append(InteractionHistory.familySize == int(family_size))
    if status:
        filters.append(InteractionHistory.status.ilike(f"%{status}%"))

    # Execute the query
    if filters:
        interactions = InteractionHistory.query.filter(and_(*filters)).all()
    else:
        return jsonify({'message': 'No search parameters provided'}), 400

    # Handle no matching interactions
    if not interactions:
        return jsonify({'message': 'No interactions found'}), 404

    # Return all matching interactions
    result = [
        {
            'interactionHistoryId': i.interactionHistoryId,
            'userInformationId': i.userInformationId,
            'mbti': i.mbti,
            'income': i.income,
            'demographic': i.demographic,
            'familySize': i.familySize,
            'status': i.status
        }
        for i in interactions
    ]

    return jsonify(result), 200


# search by ID (individual interaction)
@interaction_bp.route('/<int:interaction_id>', methods=['GET'])
def get_interaction(interaction_id):
    ## Retrieve a single interaction by ID
    interaction = InteractionHistory.query.get(interaction_id)

    if not interaction:
        return jsonify({'message': 'Interaction not found'}), 404
    
    return jsonify({
        'interactionHistoryId': interaction.interactionHistoryId,
        'userInformationId': interaction.userInformationId,
        'mbti': interaction.mbti,
        'income': interaction.income,
        'demographic': interaction.demographic,
        'familySize': interaction.familySize,
        'status': interaction.status
    }), 200


# Create API (POST) with Auto UserInformation ID
@interaction_bp.route('/', methods=['POST'])
@jwt_required()
def add_interaction():
    ## Add a new interaction with auto userInformationId from authenticated user
    
    # get the userId from the JWT token
    current_user_id = get_jwt_identity()

    # Retrieve the userInformationId linked to the current user
    user_info = UserInformation.query.filter_by(userId=current_user_id).first()

    if not user_info:
        return jsonify({'message': 'UserInformation not found for the authenticated user'}), 404

    # check for duplicate userInformationId
    existing_interaction = InteractionHistory.query.filter_by(userInformationId=user_info.userInformationId).first()
    if existing_interaction:
        return jsonify({'message': 'Interaction with this userInformationId already exists'}), 409

    # Extract interaction details from request (excluding userInformationId)
    data = request.get_json()
    
    # Create new interaction with auto-assigned userInformationId
    new_interaction = InteractionHistory(
        userInformationId=user_info.userInformationId,
        mbti=data.get('mbti'),
        income=data.get('income'),
        demographic=data.get('demographic'),
        familySize=data.get('familySize'),
        status=data.get('status', 'active')
    )

    # Save to DB
    db.session.add(new_interaction)
    db.session.commit()

    return jsonify({'message': 'Interaction added successfully'}), 201


# Update API (PUT) with Auto UserInformation ID
@interaction_bp.route('/<int:interaction_id>', methods=['PUT'])
@jwt_required()
def update_interaction(interaction_id):
    ## Update interaction details with auto userInformationId from auth user
    
    # Get the userId from the JWT token
    current_user_id = get_jwt_identity()

    # Retrieve the userInformationId linked to the current authenticated user
    user_info = UserInformation.query.filter_by(userId=current_user_id).first()

    if not user_info:
        return jsonify({'message': 'UserInformation not found for the authenticated user'}), 404

    # Get the existing interaction
    interaction = InteractionHistory.query.get(interaction_id)

    if not interaction:
        return jsonify({'message': 'Interaction not found'}), 404

    # Ensure the interaction belongs to the current authenticated user
    if interaction.userInformationId != user_info.userInformationId:
        return jsonify({'message': 'Unauthorized: Cannot update this interaction'}), 403

    # Update interaction with the new values (excluding userInformationId)
    data = request.get_json()
    for key, value in data.items():
        setattr(interaction, key, value)

    db.session.commit()
    return jsonify({'message': 'Interaction updated successfully'}), 200


# Toggle Interaction Status (PATCH)
@interaction_bp.route('/toggle-status/<int:interaction_id>', methods=['PATCH'])
@jwt_required()
def toggle_interaction_status(interaction_id):
    ## Toggle interaction status (only for the authenticated user's own interaction)

    # Get the userId from the JWT token
    current_user_id = get_jwt_identity()

    # Retrieve the userInformationId linked to the current authenticated user
    user_info = UserInformation.query.filter_by(userId=current_user_id).first()

    if not user_info:
        return jsonify({'message': 'UserInformation not found for the authenticated user'}), 404

    # Retrieve the interaction by ID
    interaction = InteractionHistory.query.get(interaction_id)

    if not interaction:
        return jsonify({'message': 'Interaction not found'}), 404

    # Ensure the interaction belongs to the current authenticated user
    if interaction.userInformationId != user_info.userInformationId:
        return jsonify({'message': 'Unauthorized: Cannot modify this interaction'}), 403

    # Toggle status between 'active' and 'inactive'
    interaction.status = 'inactive' if interaction.status == 'active' else 'active'
    db.session.commit()

    return jsonify({'message': f'Interaction status updated to {interaction.status}'}), 200


# delete interaction api
@interaction_bp.route('/<int:interaction_id>', methods=['DELETE'])
@jwt_required()
def delete_interaction(interaction_id):
    ## delete an interaction
    interaction = InteractionHistory.query.get(interaction_id)

    if not interaction:
        return jsonify({'message': 'Interaction not found'}), 404
    db.session.delete(interaction)
    db.session.commit()

    return jsonify({'message': 'Interaction deleted successfully'}), 202