from flask import Blueprint, request, jsonify
from models import Property
from extensions import db
from flask_jwt_extended import jwt_required
from sqlalchemy import or_, and_

property_bp = Blueprint('property_bp', __name__)

# advanced search api
@property_bp.route('/', methods=['GET'])
def get_properties():
    # Retrieve query parameters
    propertyType = request.args.get('propertyType')
    status = request.args.get('status')
    price_min = request.args.get('price_min')  # Minimum price
    price_max = request.args.get('price_max')  # Maximum price
    postCode = request.args.get('postCode')  # Partial match
    street = request.args.get('street')  # Partial match

    # Build the query dynamically based on provided parameters
    filters = []
    if propertyType:
        filters.append(Property.propertyType == propertyType)
    if status:
        filters.append(Property.status == status)
    if price_min and price_max:
        filters.append(and_(Property.price >= float(price_min), Property.price <= float(price_max)))  # Price range
    elif price_min:  # Minimum price only
        filters.append(Property.price >= float(price_min))
    elif price_max:  # Maximum price only
        filters.append(Property.price <= float(price_max))
    if postCode:
        filters.append(Property.postCode.ilike(f"{postCode}%"))  # Match postCode starting with input
    if street:
        filters.append(Property.street.ilike(f"%{street}%"))  # Match street containing input

    # Only apply filters if at least one parameter is provided
    if filters:
        properties = Property.query.filter(and_(*filters)).all()
    else:
        return jsonify({'message': 'No search parameters provided'}), 400

    # Handle no matching properties
    if not properties:
        return jsonify({'message': 'No properties found'}), 404

    # Return all matching properties
    result = [
        {
            'propertyUID': p.propertyUID,
            'postCode': p.postCode,
            'street': p.street,
            'streetNumber': p.streetNumber,
            'price': p.price,
            'priceLastTraded': p.priceLastTraded,
            'propertySize': p.propertySize,
            'propertyType': p.propertyType,
            'status': p.status
        }
        for p in properties
    ]

    return jsonify(result), 200



# search api with property id (individually)
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

# create api
@property_bp.route('/', methods=['POST'])
@jwt_required()
def add_property():
    # add a new property
    data = request.get_json()
    new_property = Property(**data)

    db.session.add(new_property)
    db.session.commit()
    return jsonify({'message': 'Property added successfully'}), 201


# update api
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


# @property_bp.route('/search', methods=['GET'])
# def search_property():
#     # search property by postcode or type.
#     postcode = request.args.get('postcode')
#     property_type = request.args.get('type')

#     query = Property.query
#     if postcode:
#         query = query.filter_by(propertyPostCode = postcode)
#     if property_type:
#         query = query.filter_by(propertyType = property_type)

#     properties = query.all()
#     if not properties:
#         return jsonify({'message': 'No properties found'}), 404
    
    
#     return jsonify([{
#         'propertyId': p.propertyId,
#         'propertyUID': p.propertyUID,
#         'postCode': p.postCode,
#         'street': p.street,
#         'streetNumber': p.streetNumber,
#         'price': p.price,
#         'priceLastTraded': p.priceLastTraded,
#         'propertySize': p.propertySize,
#         'propertyType': p.propertyType,
#         'status': p.status
#     } for p in properties]), 200


# toggle property status
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


# delete property api
@property_bp.route('/<int:propertyId>', methods=['DELETE'])
@jwt_required()
def delete_property(propertyId):
    # Find the property by propertyId
    property_to_delete = Property.query.get(propertyId)

    # If the property is not found, return a 404 error
    if not property_to_delete:
        return jsonify({'message': 'Property not found'}), 404

    # Delete the property
    db.session.delete(property_to_delete)
    db.session.commit()
    return jsonify({'message': 'Property deleted successfully'}), 200
