from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Import routes and models after initializing app and db to avoid circular imports
# This was mentioned in tutorial 1 May second half of the session. 
from app import routes, models
