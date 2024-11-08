from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    # Initialize the app
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    # Specify the login view
    login_manager.login_view = 'auth.login'  # Adjust 'auth.login' to your actual login route
    login_manager.login_message_category = 'info'

    # Register blueprints
    from app.views.admin import admin_bp
    from app.views.customer import customer_bp
    from app.views.professional import professional_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(professional_bp, url_prefix='/professional')

    # Load user callback for Flask-Login
    from app.models import User  # Assuming User model is in models/user.py

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Create tables in the database
        db.create_all()
    app.run(debug=True)