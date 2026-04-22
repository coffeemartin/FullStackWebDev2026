from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file, if it exists, I have also added .env to .gitignore to prevent it from being committed to version control.

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
from app import routes
