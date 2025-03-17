from extensions import db

class User(db.Model):
    userId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='active')

class Property(db.Model):
    propertyId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    propertyUID = db.Column(db.String(100), unique=True)
    propertyPostCode = db.Column(db.String(20))
    propertyStreet = db.Column(db.String(100))
    propertyStreetNumber = db.Column(db.String(10))
    price = db.Column(db.Float)
    priceLastTraded = db.Column(db.Float)
    propertySize = db.Column(db.Float)
    propertyType = db.Column(db.String(50))
    status = db.Column(db.String(50), default='available')
