from flask import Blueprint


from .admin import admin_bp
from .customer import customer_bp
from .professional import professional_bp



def register_blueprints(app):
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(professional_bp, url_prefix='/professional')
