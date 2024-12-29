# Install required packages
!pip install flask flask-sqlalchemy flask-login flask-bcrypt pyngrok

# Import necessary libraries
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from pyngrok import ngrok
import subprocess
import sys

# Configure ngrok with your auth token
!ngrok config add-authtoken 2Z5fw3woEzIAWAIzv1sfH6yisxU_85ULXXEvrQbDuGPvQ421C

# Kill any existing processes on port 5000
!kill -9 $(lsof -t -i:5000) 2>/dev/null || true

# Create a Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import routes after initializing app
from routes import *

# Initialize ngrok
public_url = ngrok.connect(5000)
print(f'\n * Public URL: {public_url}')

# Function to run the Flask app
def run_flask():
    try:
        app.run(port=5000)
    except Exception as e:
        print(f"Error running Flask app: {e}")
        sys.exit(1)

# Run the Flask app in the main thread
if __name__ == '__main__':
    print(' * Starting Flask application...')
    print(f' * Environment: {app.env}')
    print(f' * Debug mode: {app.debug}')
    run_flask()
