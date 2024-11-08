from app import create_app, db
from app.models import User, Service, ServiceRequest

app = create_app()

with app.app_context():
    # Drop all existing tables
    db.drop_all()
    
    # Create all tables
    db.create_all()
    
    # Create admin user
    admin = User(
        username='admin',
        password='admin123',
        role='admin',
        is_approved=True
    )
    db.session.add(admin)
    
    # Create some initial services
    services = [
        Service(name='House Cleaning', description='Complete house cleaning service', base_price=100.0),
        Service(name='Gardening', description='Garden maintenance and landscaping', base_price=80.0),
        Service(name='Plumbing', description='General plumbing services', base_price=120.0)
    ]
    for service in services:
        db.session.add(service)
    
    db.session.commit()
    print("Database recreated with admin user and initial services!") 