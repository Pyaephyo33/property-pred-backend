from flask import Blueprint, jsonify, request
from models import db, PropertyHistory, PropertyPrediction, Property
from datetime import datetime, timezone
import joblib
import pandas as pd
from flask_jwt_extended import jwt_required

property_history_bp = Blueprint('property_history_bp', __name__)

# Fallback: Use a simple linear estimation instead of ML model
# since model is producing flat results

def naive_price_projection(base_price, rent, year_offset):
    growth_rate = 0.03 + (0.005 * year_offset)  # compound growth
    rent_adjustment = rent * (1 + 0.01 * year_offset)
    return base_price * (1 + growth_rate) + rent_adjustment

# Endpoint to add new property history and predict future prices
@property_history_bp.route('/property-history', methods=['POST'])
@jwt_required()
def add_history_and_predict():
    data = request.json

    required_fields = ['propertyId', 'historicalRent', 'date']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields'}), 400

    try:
        property_record = Property.query.get(data['propertyId'])
        if not property_record:
            return jsonify({'message': 'Property not found.'}), 404

        existing_prediction = PropertyPrediction.query.filter_by(propertyId=data['propertyId']).first()
        if existing_prediction:
            return jsonify({'message': 'Predictions already exist for this property.'}), 400

        history_record = PropertyHistory(
            propertyId=data['propertyId'],
            historicalPrice=property_record.price,
            historicalRent=data['historicalRent'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date()
        )
        db.session.add(history_record)
        db.session.commit()

        predicted_prices = []
        prediction_years = []
        current_year = datetime.now(timezone.utc).year

        for i, year in enumerate(range(current_year, current_year + 5)):
            predicted_price = round(naive_price_projection(
                base_price=property_record.price,
                rent=float(data['historicalRent']),
                year_offset=i
            ), 2)

            predicted_prices.append(predicted_price)
            prediction_years.append(year)

        prediction_record = PropertyPrediction(
            propertyId=data['propertyId'],
            predictedPrices=predicted_prices,
            predictionYears=prediction_years,
            datePredicted=datetime.now(timezone.utc)
        )

        db.session.add(prediction_record)
        db.session.commit()

        return jsonify({
            'message': 'History and Predictions saved successfully.',
            'propertyId': data['propertyId'],
            'predictions': [{'year': y, 'predictedPrice': p} for y, p in zip(prediction_years, predicted_prices)]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An error occurred: {str(e)}'}), 500
