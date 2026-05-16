import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file, if it exists, I have also added .env to .gitignore to prevent it from being committed to version control.

basedir = os.path.abspath(os.path.dirname(__file__))
default_database_location = 'sqlite:///' + os.path.join(basedir, 'app.db')

class Config:
    # Franco Notes: For production, set the DATABASE_URL environment variable to database connection. 
    # This also avoid anyone to edit the configuration without knowing what programming language 
    # my backend is written in. (Lecture tutorial 1 May mentioned this)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('MYAPP_DATABASE_URL') or default_database_location
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'


class DeploymentConfig(Config):
    # Franco Notes: deployment-specific 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

class TestingConfig(Config):
    # Franco Notes: Add any testing-specific 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True