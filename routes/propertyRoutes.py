from flask import Blueprint, request, jsonify
from models import Property
from extensions import db
from flask_jwt_extended import jwt_required

property_bp = Blueprint('property_bp', __name__)

@property_bp.route('/', methods=['GET'])
def get_properties():
    # retrieve all properties 
    properties = Property.query.all()
    return jsonify([{
        'propertyId': p.propertyId,
        'propertyUID': p.propertyUID,
        'postCode': p.postCode,
        'street': p.street,
        'streetNumber': p.streetNumber,
        'price': p.price,
        'priceLastTraded': p.priceLastTraded,
        'propertySize': p.propertySize,
        'propertyType': p.propertyType,
        'status': p.status
    } for p in properties])


@property_bp.route('/<int:property_id>', methods=['GET'])
def get_property(property_id):
    # retrieve a single property by id.
    property_obj = Property.query.get(property_id)
    if not property_obj:
        return jsonify({'message': 'Property not found'}), 404
    
    return jsonify({
        'propertyId': property_obj.propertyId,
        'propertyUID': property_obj.propertyUID,
        'postCode': property_obj.postCode,
        'street': property_obj.street,
        'streetNumber': property_obj.streetNumber,
        'price': property_obj.price,
        'priceLastTraded': property_obj.priceLastTraded,
        'propertySize': property_obj.propertySize,
        'propertyType': property_obj.propertyType,
        'status': property_obj.status
    }), 200


@property_bp.route('/', methods=['POST'])
@jwt_required()
def add_property():
    # add a new property
    data = request.get_json()
    new_property = Property(**data)

    db.session.add(new_property)
    db.session.commit()
    return jsonify({'message': 'Property added successfully'}), 201



@property_bp.route('/<int:property_id>', methods=['PUT'])
@jwt_required()
def update_property(property_id):
    # update property details
    data = request.get_json()
    property_obj = Property.query.get(property_id)

    if not property_obj:
        return jsonify({'message': 'Property not found'}), 404
    
    for key, value in data.items():
        setattr(property_obj, key, value)

    db.session.commit()
    return jsonify({'message': 'Property updated successfully'}), 200


@property_bp.route('/search', methods=['GET'])
def search_property():
    # search property by postcode or type.
    postcode = request.args.get('postcode')
    property_type = request.args.get('type')

    query = Property.query
    if postcode:
        query = query.filter_by(propertyPostCode = postcode)
    if property_type:
        query = query.filter_by(propertyType = property_type)

    properties = query.all()
    if not properties:
        return jsonify({'message': 'No properties found'}), 404
    
    
    return jsonify([{
        'propertyId': p.propertyId,
        'propertyUID': p.propertyUID,
        'postCode': p.postCode,
        'street': p.street,
        'streetNumber': p.streetNumber,
        'price': p.price,
        'priceLastTraded': p.priceLastTraded,
        'propertySize': p.propertySize,
        'propertyType': p.propertyType,
        'status': p.status
    } for p in properties]), 200



@property_bp.route('/toggle-status/<int:property_id>', methods=['PATCH'])
@jwt_required()
def toggle_property_status(property_id):
    # toggle property status between 'available' and 'unavailable'.
    property_obj = Property.query.get(property_id)
    if not property_obj:
        return jsonify({'message': 'Property not found'}), 404
    
    property_obj.status = 'unavailable' if property_obj.status == 'available' else 'available'
    db.session.commit()

    return jsonify({'message': f'Property status updated to {property_obj.status}'}), 200