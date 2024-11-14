
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    
    login_manager.login_view = 'main.login'
    
    
    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    
    from .views.admin import admin_bp
    from .views.customer import customer_bp
    from .views.professional import professional_bp
    from .routes import main_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(professional_bp, url_prefix='/professional')
    app.register_blueprint(main_bp)
    
    
    with app.app_context():
        db.create_all()
    
    return app
