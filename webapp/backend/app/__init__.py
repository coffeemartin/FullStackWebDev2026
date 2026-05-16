from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

#app = Flask(__name__)
#app.config.from_object(Config)

db = SQLAlchemy()
# migrate = Migrate()
# Import routes and models after initializing app and db to avoid circular imports
# This was mentioned in tutorial 1 May second half of the session. 
login = LoginManager()
login.login_view = 'main.login'  # The login_view should be set to the name of the route that loads the login screen.

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class) 
    db.init_app(app)
    from app.blueprints import main
    app.register_blueprint(main)
    login.init_app(app)
    return app

#adding log in manager, just installed flask-login, so need to import it and initialize it here.



from app import routes, models
