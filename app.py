from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def init_db():
    with app.app_context():
        db.drop_all()  # Drop all existing tables
        db.create_all()  # Create new tables
        # Create admin user if it doesn't exist
        from models import Admin
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin', password=bcrypt.generate_password_hash('admin123').decode('utf-8'))
            db.session.add(admin)
            db.session.commit()

from routes import *

if __name__ == '__main__':
    init_db()  # Initialize database when running the app
    app.run(debug=True)