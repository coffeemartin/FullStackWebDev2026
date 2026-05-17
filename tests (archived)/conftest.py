import os
import sys
from pathlib import Path

import pytest


os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("MYAPP_DATABASE_URL", "sqlite:///:memory:")

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "webapp" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app import app as flask_app, db
from app.models import User


@pytest.fixture()
def app():
    flask_app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )

    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def make_user(username, name=None, password="Password123"):
    user = User(
        username=username,
        email=f"{username}@example.com",
        name=name or username.title(),
        age=22,
        gender="Other",
        height_cm=170,
        weight_kg=65,
        goal="Build consistency",
        activity_level="Moderate",
        injury_notes="None",
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user


def login(client, username, password="Password123"):
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
            "remember_me": "y",
            "submit": "Sign In",
        },
        follow_redirects=True,
    )
