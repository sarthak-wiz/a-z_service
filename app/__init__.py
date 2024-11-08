# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    Bootstrap(app)
    login_manager.init_app(app)
    
    # Set login view
    login_manager.login_view = 'main.login'
    
    # Setup Flask-Login user_loader
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Import and register blueprints
    from .views.admin import admin_bp
    from .views.customer import customer_bp
    from .views.professional import professional_bp
    from .routes import main_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(professional_bp, url_prefix='/professional')
    app.register_blueprint(main_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app