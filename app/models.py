from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')
    is_approved = db.Column(db.Boolean, default=False)
    
    # Relationships with different backref names
    customer_requests = db.relationship('ServiceRequest', 
                                      backref='requesting_customer', 
                                      lazy=True,
                                      foreign_keys='ServiceRequest.customer_id')
    
    professional_requests = db.relationship('ServiceRequest', 
                                          backref='assigned_professional', 
                                          lazy=True,
                                          foreign_keys='ServiceRequest.professional_id')

    def __repr__(self):
        return f'<User {self.username}>'


class Service(db.Model):
    __tablename__ = 'service'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    base_price = db.Column(db.Float, nullable=False)
    
    # Relationship
    requests = db.relationship('ServiceRequest', backref='service', lazy=True)

    def __repr__(self):
        return f'<Service {self.name}>'


class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    status = db.Column(db.String(20), default='requested')
    date_of_request = db.Column(db.DateTime, nullable=False)
    remarks = db.Column(db.Text)

    def __repr__(self):
        return f'<ServiceRequest {self.id}>'
