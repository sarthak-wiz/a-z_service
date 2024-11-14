from app import create_app, db
from app.models import User, Service, ServiceRequest, Review
from datetime import datetime

app = create_app()

with app.app_context():
    # Drop all tables
    db.drop_all()
    # Create all tables
    db.create_all()

    
    admin = User(
        username='admin',
        password='admin123',  
        role='admin',
        is_approved=True
    )
    db.session.add(admin)

    # creating sample professional
    professional = User(
        username='pro1',
        password='password123',
        role='professional',
        is_approved=True,
        location='New York',
        pincode='100001',
        professional_id='PRO12345'
    )
    db.session.add(professional)

    # creating sample customer
    customer = User(
        username='customer1',
        password='password123',
        role='customer',
        is_approved=True
    )
    db.session.add(customer)

    # creating initial services
    services = [
        Service(
            name='House Cleaning',
            description='Complete house cleaning service',
            base_price=100.0,
            time_required='4 hours',
            created_at=datetime.utcnow()
        ),
        Service(
            name='Plumbing',
            description='Professional plumbing services',
            base_price=150.0,
            time_required='2 hours',
            created_at=datetime.utcnow()
        ),
        Service(
            name='Electrical Work',
            description='Electrical repair and installation',
            base_price=200.0,
            time_required='3 hours',
            created_at=datetime.utcnow()
        ),
        Service(
            name='Gardening',
            description='Garden maintenance and landscaping',
            base_price=120.0,
            time_required='6 hours',
            created_at=datetime.utcnow()
        ),
        Service(
            name='Painting',
            description='Interior and exterior painting',
            base_price=180.0,
            time_required='8 hours',
            created_at=datetime.utcnow()
        ),
        Service(
            name='Carpentry',
            description='Custom carpentry and repairs',
            base_price=160.0,
            time_required='4 hours',
            created_at=datetime.utcnow()
        )
    ]

    
    db.session.add(admin)
    for service in services:
        db.session.add(service)

    try:
        db.session.commit()
        print("Database recreated successfully!")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {str(e)}")



        