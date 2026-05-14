import os
import sys
from pathlib import Path

os.environ.setdefault("OPENAI_API_KEY", "test-key")

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "webapp" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.routes import calculate_bmi_result


def test_calculate_bmi_result_returns_healthy_weight_category():
    bmi, category, quote = calculate_bmi_result(170, 65)

    assert bmi == 22.5
    assert category == "Healthy weight"
    assert quote
