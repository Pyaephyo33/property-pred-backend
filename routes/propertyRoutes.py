from flask import Blueprint, request, jsonify
from models import Property
from extensions import db
from flask_jwt_extended import jwt_required

property_bp = Blueprint('property_bp', __name__)

@property_bp.route('/', methods=['GET'])
def get_properties():
    properties = Property.query.all()
    return jsonify([{
        'propertyId': p.propertyId, 'PropertyUID': p.propertyUID, 'price': p.price
    } for p in properties])

@property_bp.route('/', methods=['POST'])
@jwt_required()
def add_property():
    data = request.get_json()
    new_property = Property(**data)
    db.session.add(new_property)
    db.session.commit()
    return jsonify({'message': 'Property added successfully'}), 201