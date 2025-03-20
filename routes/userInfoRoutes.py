from flask import Blueprint, request, jsonify
from models import UserInformation
from extensions import db, bcrypt, jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, JWTManager, jwt_manager
from datetime import datetime, timedelta
from sqlalchemy import or_, and_

userInfo_bp = Blueprint('userInfo_bp', __name__)

# create api route
@userInfo_bp.route('/', methods=['POST'])
@jwt_required()
def add_userInfo():
    # Extract the authenticated user's ID from the JWT token
    userId = get_jwt_identity()

    # Check if a UserInformation record already exists for this userId
    existing_user_info = UserInformation.query.filter_by(userId=userId).first()
    if existing_user_info:
        return jsonify({'message': 'UserInformation already exists for this user'}), 400

    # Ensure the request body is properly provided
    data = request.get_json()

    # Add the authenticated user's userId to the data dictionary
    if 'userId' in data:
        return jsonify({'message': 'You cannot manually provide userId'}), 400
    data['userId'] = userId

    # Create a new UserInformation object
    new_user_info = UserInformation(**data)
    
    # Save the new record to the database
    db.session.add(new_user_info)
    db.session.commit()
    return jsonify({'message': 'UserInformation added successfully!', 'userInformationId': new_user_info.userInformationId}), 201



# get api with singular userInfo id
@userInfo_bp.route('/<int:userInformationId>', methods=['GET'])
@jwt_required()
def get_userInfo(userInformationId):
    user_info = UserInformation.query.get(userInformationId)

    if not user_info:
        return jsonify({'message': 'UserInformation not found'}), 404
    
    return jsonify({
        'userInformationId': user_info.userInformationId,
        'userId': user_info.userId,
        'nickname': user_info.nickname,
        'lastname': user_info.lastname,
        'status': user_info.status
    }), 200

# update api 
@userInfo_bp.route('/update/<int:userInformationId>', methods=['PUT'])
def update_userInfo(userInformationId):
    data = request.get_json()
    user_info = UserInformation.query.get(userInformationId)

    if not user_info:
        return jsonify({'message': 'UserInformation not found'}), 404

    user_info.nickname = data.get('nickname', user_info.nickname)
    user_info.lastname = data.get('lastname', user_info.lastname)
    user_info.status = data.get('status', user_info.status)

    db.session.commit()
    return jsonify({'message': 'UserInformation updated successfully!'}), 200


# delete api
@userInfo_bp.route('/delete/<int:userInformationId>', methods=['DELETE'])
@jwt_required()
def delete_userInfo(userInformationId):
    # Retrieve the authenticated user's ID from the JWT token
    auth_user_id = get_jwt_identity()
    print(f"Authenticated User ID: {auth_user_id}")

    # Find the UserInformation record by its ID
    user_info = UserInformation.query.get(userInformationId)

    # If the UserInformation record does not exist, return 404
    if not user_info:
        return jsonify({'message': 'UserInformation not found'}), 404

    print(f"UserInformation ID: {user_info.userInformationId}, User ID: {user_info.userId}")

    # Ensure the authenticated user owns this UserInformation record
    if int(auth_user_id) != user_info.userId:
        return jsonify({'message': 'You do not have permission to delete this UserInformation'}), 403

    # Delete the UserInformation record
    db.session.delete(user_info)
    db.session.commit()
    return jsonify({'message': 'UserInformation deleted successfully!'}), 200



# advanced search api
@userInfo_bp.route('/search', methods=['GET'])
def search_userInfo():
    nickname = request.args.get('nickname')
    lastname = request.args.get('lastname')
    status = request.args.get('status')

    filters = []
    if nickname:
        filters.append(UserInformation.nickname.ilike(f"%{nickname}%"))
    if lastname:
        filters.append(UserInformation.lastname.ilike(f"%{lastname}%"))
    if status:
        filters.append(UserInformation.status == status)

    if filters:
        results = UserInformation.query.filter(or_(*filters)).all()
    else:
        return jsonify({'message': 'No search parameters provided'}), 400

    if not results:
        return jsonify({'message': 'No UserInformation records found'}), 404

    return jsonify([
        {
            'userInformationId': u.userInformationId,
            'userId': u.userId,
            'nickname': u.nickname,
            'lastname': u.lastname,
            'status': u.status
        }
        for u in results
    ]), 200

# toggle api
@userInfo_bp.route('/toggle-status/<int:userInformationId>', methods=['PUT'])
def toggle_status(userInformationId):
    user_info = UserInformation.query.get(userInformationId)

    if not user_info:
        return jsonify({'message': 'UserInformation not found'}), 404

    # Toggle the status
    user_info.status = 'inactive' if user_info.status == 'active' else 'active'

    db.session.commit()
    return jsonify({'message': f"Status toggled to {user_info.status} successfully!"}), 200
