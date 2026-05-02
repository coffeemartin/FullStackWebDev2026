from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Import routes and models after initializing app and db to avoid circular imports
# This was mentioned in tutorial 1 May second half of the session. 


#adding log in manager, just installed flask-login, so need to import it and initialize it here.

login = LoginManager(app)
login.login_view = 'login'  # The login_view should be set to the name of the route that loads the login screen.

from app import routes, models
