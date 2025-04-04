from flask import Flask
from config import Config
from extensions import db, bcrypt, jwt

# api routes
from routes.userRoutes import user_bp
from routes.propertyRoutes import property_bp
from routes.userInfoRoutes import userInfo_bp
from routes.interactionHistoryRoutes import interaction_bp
from routes.preferenceDislikeRoutes import dislike_bp, preference_bp
from routes.propertyHistoryPredictionRoutes import property_history_bp

def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(property_bp, url_prefix='/api/properties')
    app.register_blueprint(userInfo_bp, url_prefix='/api/user-info')
    app.register_blueprint(interaction_bp, url_prefix='/api/inter-history')
    app.register_blueprint(preference_bp, url_prefix='/api/preference')
    app.register_blueprint(dislike_bp, url_prefix='/api/dislike')
    app.register_blueprint(property_history_bp, url_prefix='/api/history-prediction')

    # Create database tables if they don’t exist
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
