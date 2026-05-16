import os
import sys
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "webapp" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.models import User


def test_user_password_is_stored_as_hash():
    user = User(
        username="testuser",
        email="testuser@example.com",
        name="Test User",
        age=22,
        gender="Other",
        height_cm=170,
        weight_kg=65,
        goal="Build consistency",
        activity_level="Moderate",
        injury_notes="None",
    )

    user.set_password("Password123")

    assert user.password_hash != "Password123"
    assert user.check_password("Password123")
    assert not user.check_password("WrongPassword")
