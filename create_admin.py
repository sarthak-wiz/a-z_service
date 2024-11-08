from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    admin = User(
        username='admin',
        password='admin123',  # Change this to a secure password
        role='admin',
        is_approved=True
    )
    db.session.add(admin)
    db.session.commit()
    print("Admin user created successfully!") 