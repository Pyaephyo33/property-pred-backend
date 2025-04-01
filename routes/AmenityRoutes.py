from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import db, PropertyAmenities, Property

property_amenities_bp = Blueprint('property_amenities_bp', __name__)

# Create Amenity
@property_amenities_bp.route('/amenities', methods=['POST'])
@jwt_required()
def create_amenity():
    data = request.json()
    required_fields = ['propertyId']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400
    
    # ensure property exists
    if not Property.query.get(data['propertyId']):
        return jsonify({'message': 'Property not found.'}), 404
    
    # prevent duplicate amenity for a property
    if PropertyAmenities.query.filter_by(propertyId=data['propertyId']).first():
        return jsonify({'message': 'Amenities already exist for the property.'}), 400
    
    amenity = PropertyAmenities(
        propertyId = data['propertyId'],
        parking = data.get('parking', False),
        garden = data.get('garden', False),
        energyEfficiencyRating = data.get('energyEfficiencyRating'),
        numBathrooms = data.get('numBathrooms')
    )
    db.session.add(amenity)
    db.session.commit()

    return jsonify({'message': 'Amenity created successfully.'}), 201

# read all amenities
@property_amenities_bp.route('/amenities', methods=['GET'])
@jwt_required()
def get_all_amenities():
    amenities = PropertyAmenities.query.all()
    return jsonify([{
        'amenityId': a.amenityId,
        'propertyId': a.propertyId,
        'parking': a.parking,
        'garden': a.garden,
        'energyEfficiencyRating': a.energyEfficiencyRating,
        'numBathrooms': a.numBathrooms
    } for a in amenities ]), 200

# read single amenity
@property_amenities_bp.route('/amenities/<int:amenityId>', methods=['GET'])
@jwt_required()
def get_amenity(amenityId):
    amenity = PropertyAmenities.query.get(amenityId)
    if not amenity:
        return jsonify({'message': 'Amenity not found'}), 404
    return jsonify({
        'amenityId': amenity.amenityId,
        'propertyId': amenity.propertyId,
        'parking': amenity.parking,
        'garden': amenity.garden,
        'energyEfficiencyRating': amenity.energyEfficiencyRating,
        'numBathrooms': amenity.numBathrooms
    }), 200

# update amenity
@property_amenities_bp.route('/amenities/<int:amenityId>', methods=['PUT'])
@jwt_required()
def update_amenity(amenityId):
    amenity = PropertyAmenities.query.get(amenityId)
    if not amenity:
        return jsonify({'message': 'Amenity not found'}), 404
    
    data = request.json
    amenity.parking = data.get('parking', amenity.parking)
    amenity.garden = data.get('garden', amenity.garden)
    amenity.energyEfficiencyRating = data.get('energyEfficiencyRating', amenity.energyEfficiencyRating)
    amenity.numBathrooms = data.get('numBathrooms', amenity.numBathrooms)

    db.session.commit()
    return jsonify({'message': 'Amenity updated successfully'}), 200

# delete amenity
@property_amenities_bp.route('/amenities/<int:amenityId>', methods=['DELETE'])
@jwt_required()
def delete_amenity(amenityId):
    amenity = PropertyAmenities.query.get(amenityId)
    if not amenity:
        return jsonify({'message': 'Amenity deleted successfully'}), 200
    
    db.session.delete(amenity)
    db.session.commit()
    return jsonify({'message': 'Amenity deleted successfully'}), 200

# basic search by propertyId
@property_amenities_bp.route('/amenities/search0', methods=['GET'])
@jwt_required()
def search_by_property():
    property_id = request.args.get('propertyId')
    if not property_id:
        return jsonify({'message': 'propertyId query param required'}), 400
    
    amenities = PropertyAmenities.query.filter_by(propertyId=property_id).all()
    return jsonify([{
        'amenityId': a.menityId,
        'propertyId': a.propertyId,
        'parking': a.parking,
        'garden': a.garden,
        'energyEfficiencyRating': a.energyEfficiencyRating,
        'numBathrooms': a.numBathrooms
    } for a in amenities]), 200

# advanced search
@property_amenities_bp.route('/amenities/advanced-search', methods=['POST'])
@jwt_required()
def advanced_search():
    filters = request.json or {}
    query = PropertyAmenities.query

    if 'parking' in filters:
        query = query.filter_by(parking = filters['parking'])
    if 'garden' in filters:
        query = query.filter_by(garden = filters['garden'])
    if 'energyEfficiencyRating' in filters:
        query = query.filter_by(energyEfficiencyRating = filters['energyEfficiencyRating'])
    if 'numBathrooms' in filters:
        query = query.filter(PropertyAmenities.numBathrooms >= filters['numBathrooms'])


    results = query.all()
    return jsonify([{
        'amenityId': a.menityId,
        'propertyId': a.propertyId,
        'parking': a.parking,
        'garden': a.garden,
        'energyEfficiencyRating': a.energyEfficiencyRating,
        'numBathrooms': a.numBathrooms
    } for a in results]), 200