from app import app, db
from models import Admin, Student, Attendance

# Create the tables
with app.app_context():
    db.create_all()  # This will create all tables defined in your models
    print("Database tables created successfully.")
