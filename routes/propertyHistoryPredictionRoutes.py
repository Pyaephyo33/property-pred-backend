from flask import Blueprint, jsonify, request
from models import db, PropertyHistory, PropertyPrediction, Property
from datetime import datetime, timezone
import joblib
import pandas as pd
import xgboost as xgb
from flask_jwt_extended import jwt_required

property_history_bp = Blueprint('property_history_bp', __name__)

# Load model and scaler
model = xgb.XGBRegressor()
model.load_model('ml_model.json')
scaler = joblib.load('ml_model_scaler.pkl')
with open('ml_model_features.txt') as f:
    model_features = [line.strip() for line in f.readlines()]

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

        # Generate predictions for 5 future years
        predicted_prices = []
        prediction_years = []
        current_year = datetime.now(timezone.utc).year

        for i, year in enumerate(range(current_year, current_year + 5)):
            growth_factor = 1 + (0.02 * i)

            input_dict = {
                'historicalPrice': property_record.price * growth_factor,
                'historicalRent': float(data['historicalRent']) * (1 + 0.01 * i),
                'year': year,
                'month': datetime.now().month,
                'propertySize': property_record.propertySize,
                'siteArea': getattr(property_record, 'siteArea', 0.01),
                'councilTax': getattr(property_record, 'councilTax', 1000),
                'pricePerSqMeter': property_record.price / (property_record.propertySize or 1),
                'historyCount': 5
            }

            row = pd.DataFrame([input_dict])
            row = row.reindex(columns=model_features, fill_value=0)
            row_scaled = scaler.transform(row)
            predicted_price = float(model.predict(row_scaled)[0]) * (1 + 0.02 * i)

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
