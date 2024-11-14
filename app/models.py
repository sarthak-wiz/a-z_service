from datetime import datetime
from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'professional', 'customer'
    is_approved = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    average_rating = db.Column(db.Float, default=0.0)
    
    
    location = db.Column(db.String(100))
    pincode = db.Column(db.String(6))
    professional_id = db.Column(db.String(8), unique=True)  # For format PRO12345
    
    service_requests_made = db.relationship('ServiceRequest', 
                                          foreign_keys='ServiceRequest.customer_id',
                                          backref='customer')
    service_requests_received = db.relationship('ServiceRequest', 
                                              foreign_keys='ServiceRequest.professional_id',
                                              backref='professional')
    reviews_given = db.relationship('Review', 
                                  foreign_keys='Review.customer_id',
                                  backref='reviewer')
    reviews_received = db.relationship('Review', 
                                     foreign_keys='Review.professional_id',
                                     backref='reviewed_professional')

    def __repr__(self):
        return f'<User {self.username}>'


class Service(db.Model):
    __tablename__ = 'service'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    
    service_requests = db.relationship('ServiceRequest', backref='requested_service')

    def __repr__(self):
        return f'<Service {self.name}>'


class ServiceRequest(db.Model):
    __tablename__ = 'service_request'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    status = db.Column(db.String(20), default='requested')  # requested, assigned, in_progress, pending_customer_approval, completed
    date_of_request = db.Column(db.DateTime, nullable=False)
    remarks = db.Column(db.Text)
    
    
    reviews = db.relationship('Review', backref='service_request', lazy=True)

    def __repr__(self):
        return f'<ServiceRequest {self.id}>'


class Review(db.Model):
    __tablename__ = 'review'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id}>'

    def update_professional_rating(self):
        """Update the professional's average rating after a new review"""
        professional = User.query.get(self.professional_id)
        reviews = Review.query.filter_by(professional_id=self.professional_id).all()
        if reviews:
            total_rating = sum(review.rating for review in reviews)
            professional.average_rating = total_rating / len(reviews)
            db.session.commit()



