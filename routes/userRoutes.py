from flask import Blueprint, request, jsonify
from models import User
from extensions import db, bcrypt, jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt, JWTManager, jwt_manager
from datetime import datetime, timedelta
from sqlalchemy import or_

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    # register a new user.
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already registered'}), 400
    
    hased_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(email=data['email'], password=hased_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201



@user_bp.route('/login', methods=['POST'])
def login():
    # user login and return jwt token
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    # if user and bcrypt.check_password_hash(user.password, data['password']):
    #     access_token = create_access_token(identity=user.userId)
    #     return jsonify({'access_token': access_token})
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=str(user.userId))
        return jsonify({'access_token': access_token})

    
    return jsonify({'messsage': 'Invalid credentials'}), 401

@user_bp.route('/update/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    # update user details
    data = request.get_json()
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = bcrypt.generate_password_hash(data['password']).decode('utf-8')

    db.session.commit()
    return jsonify({'message': 'User updated successfully'}), 200

@user_bp.route('/delete/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    # delete user
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200

@user_bp.route('/search', methods=['GET'])
def search_user():
    email = request.args.get('email')
    status = request.args.get('status')

    # Query to find users where either email matches or status matches
    users = User.query.filter(
        or_(
            User.email == email if email else False,  # Match email if provided
            User.status == status if status else False  # Match status if provided
        )
    ).all()

    if not users:
        return jsonify({'message': 'No users found'}), 404

    # Return all matching users
    result = [
        {'userId': user.userId, 'email': user.email, 'status': user.status}
        for user in users
    ]

    return jsonify(result), 200



@user_bp.route('/toggle-status/<int:user_id>', methods=['PATCH'])
@jwt_required()
def toggle_status(user_id):
    # toggle user status
    user = User.query.get(user_id)

    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    user.status = 'inactive' if user.status == 'active' else 'active'
    db.session.commit()

    return jsonify({'message': f'User status updated to {user.status}'}), 200



# Blacklist storage (for production, use a persistent store like Redis)
blacklist = set()

# Logout route to blacklist the token
@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # Retrieve the token's unique identifier
    blacklist.add(jti)      # Add the token to the blacklist
    return jsonify({'message': 'Logout successful'}), 200

# Function to check if a token is in the blocklist
@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in blacklist