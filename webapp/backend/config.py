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
    # I had issues by using in-memory for my selenium tests, as in-memory SQLite often breaks multi-threaded Selenium/integration tests
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Franco more notes: as due to the log in manager, I need to use a file-based SQLite database for testing, 
    # otherwise the in-memory database will be created separately in each thread and cause issues with the tests. 
    # This is a bit different to the lecuture tutorial? I am not sure if I misunderstood or something,\
    # but tutorial used a very simple selenium test that doesn't involve log in, only checking the group numbers etc.
    # so it didn't encounter this issue ?

    # From what I am reading, the In-memory SQLite was suitable for isolated unit tests, 
    # but not for Selenium tests because Selenium starts the Flask app in a separate server thread and 
    # sends real browser requests. 
    # The setup code and the request handler may use different database connections, 
    # and an in-memory SQLite database only exists within the connection that created it. 
    # Therefore the Flask route could not see the tables created during test setup. 


    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    TESTING = True