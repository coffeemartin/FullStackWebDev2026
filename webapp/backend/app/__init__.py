from email.mime import application

from flask import Flask
import os
from dotenv import load_dotenv
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

load_dotenv() # Load environment variables from .env file, if it exists, I have also added .env to .gitignore to prevent it from being committed to version control.

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from app import routes, models
