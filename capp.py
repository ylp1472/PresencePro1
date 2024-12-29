# First install required packages
!pip install flask flask-sqlalchemy flask-login flask-bcrypt pyngrok

# Import necessary libraries
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from pyngrok import ngrok

# Save your Flask app code to a file
%%writefile app.py
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

from routes import *

if __name__ == '__main__':
    app.run()

# Create a new cell and run this to start the server with ngrok
# Make sure all your route files are uploaded to Colab first
!ngrok authtoken YOUR_NGROK_AUTH_TOKEN  # Replace with your ngrok auth token
from pyngrok import ngrok

# Start ngrok
public_url = ngrok.connect(5000)
print(f' * Public URL: {public_url}')

# Run the Flask app
!python app.py