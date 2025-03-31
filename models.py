from datetime import datetime, timezone
from extensions import db

class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='active')

class UserInformation(db.Model):
    userInformationId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.userId'), nullable=False)
    nickname = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    status = db.Column(db.String(50))

class InteractionHistory(db.Model):
    interactionHistoryId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userInformationId = db.Column(db.Integer, db.ForeignKey('user_information.userInformationId'), nullable=False)
    mbti = db.Column(db.String(50))
    income = db.Column(db.Float)
    demographic = db.Column(db.String(100))
    familySize = db.Column(db.Integer)
    status = db.Column(db.String(50))

class Property(db.Model):
    propertyId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    propertyUID = db.Column(db.String(100), unique=True)
    postCode = db.Column(db.String(20))
    street = db.Column(db.String(100))
    streetNumber = db.Column(db.String(10))
    price = db.Column(db.Float)
    priceLastTraded = db.Column(db.Float)
    propertySize = db.Column(db.Float)
    propertyType = db.Column(db.String(50))
    status = db.Column(db.String(50), default='available')

class PropertyHistory(db.Model):
    propertyHistoryId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    propertyId = db.Column(db.Integer, db.ForeignKey('property.propertyId'), nullable=False)
    historicalPrice = db.Column(db.Float)
    historicalRent = db.Column(db.Float)
    date = db.Column(db.Date)

class Preferences(db.Model):
    preferenceId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    interactionHistoryId = db.Column(db.Integer, db.ForeignKey('interaction_history.interactionHistoryId'), nullable=False)
    propertyId = db.Column(db.Integer, db.ForeignKey('property.propertyId'), nullable=False)

class Dislikes(db.Model):
    dislikeId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    interactionHistoryId = db.Column(db.Integer, db.ForeignKey('interaction_history.interactionHistoryId'), nullable=False)
    propertyId = db.Column(db.Integer, db.ForeignKey('property.propertyId'), nullable=False)

class PropertyAmenities(db.Model):
    amenityId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    propertyId = db.Column(db.Integer, db.ForeignKey('property.propertyId'), nullable=False)
    parking = db.Column(db.Boolean, default=False)
    garden = db.Column(db.Boolean, default=False)
    energyEfficiencyRating = db.Column(db.String(10))
    numBathrooms = db.Column(db.Integer)

class PropertyPrediction(db.Model):
    predictionId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    propertyId = db.Column(db.Integer, db.ForeignKey('property.propertyId'), nullable=False)
    predictedPrices = db.Column(db.JSON)
    predictionYears = db.Column(db.JSON)
    datePredicted = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))