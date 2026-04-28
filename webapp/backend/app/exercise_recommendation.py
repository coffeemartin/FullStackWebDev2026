"""Exercise recommendation helper.

Returns a structured plan for the Exercise page based on the user's BMI
and self-reported activity level. Consumed by routes.exercise() and
rendered by templates/exercise.html.

The returned dict has the shape:
    {
        "label":      str,            # BMI status label, e.g. "Healthy Range"
        "focus":      str,            # one-line focus statement
        "message":    str,            # blurb under "Recommended Categories"
        "categories": list[str],      # 4 category names
        "exercises":  list[dict],     # each: {category, name, tip}
    }
"""

from typing import Optional


# ---------- BMI bucketing ----------------------------------------------------

def _bmi_category(bmi: float) -> str:
    """Map a BMI number to one of four buckets used internally."""
    if bmi < 18.5:
        return "underweight"
    if bmi < 25:
        return "normal"
    if bmi < 30:
        return "overweight"
    return "obese"


# ---------- Activity-level normalisation ------------------------------------

def _normalize_level(level: Optional[str]) -> str:
    """Accept whatever the rest of the app stores and squash to 3 keys."""
    if not level:
        return "beginner"
    key = str(level).strip().lower()
    if key in {"beginner", "low", "sedentary", "easy", "lightly active"}:
        return "beginner"
    if key in {"intermediate", "moderate", "medium", "moderately active"}:
        return "intermediate"
    if key in {"advanced", "high", "hard", "expert", "very active"}:
        return "advanced"
    return "beginner"


# ---------- Static recommendation data --------------------------------------

_BMI_PROFILES = {
    "underweight": {
        "label": "Underweight",
        "focus": "Build healthy muscle and weight with calorie-supported strength work.",
        "message": "These categories help you gain strength steadily without overtraining.",
        "categories": ["Strength", "Mobility", "Light Cardio", "Recovery"],
    },
    "normal": {
        "label": "Healthy Range",
        "focus": "Maintain fitness with a balanced mix of strength and cardio.",
        "message": "A well-rounded routine to keep you progressing and feeling great.",
        "categories": ["Strength", "Cardio", "Mobility", "Skill / Sport"],
    },
    "overweight": {
        "label": "Overweight",
        "focus": "Improve cardiovascular health and start gentle strength training.",
        "message": "Lower-impact options to build a habit and protect your joints.",
        "categories": ["Low-Impact Cardio", "Strength", "Mobility", "Recovery"],
    },
    "obese": {
        "label": "Obese",
        "focus": "Prioritise low-impact movement, joint care, and gradual consistency.",
        "message": "Start small and stay consistent — these categories are joint-friendly.",
        "categories": ["Walking / Cycling", "Water-Based Cardio", "Mobility", "Recovery"],
    },
}


_EXERCISES = {
    "underweight": [
        {"name": "Goblet Squat", "category": "Strength", "tips": {
            "beginner":     "Hold a light dumbbell at chest. 3 sets of 8 reps.",
            "intermediate": "Use a moderate dumbbell. 4 sets of 10 reps.",
            "advanced":     "Heavier dumbbell, slow tempo. 5 sets of 8 reps.",
        }},
        {"name": "Push-Up", "category": "Strength", "tips": {
            "beginner":     "Knees down or against a wall. 3 sets of 6-8 reps.",
            "intermediate": "Standard form. 4 sets of 10 reps.",
            "advanced":     "Add a tempo pause or weighted vest. 4 sets of 12 reps.",
        }},
        {"name": "Dumbbell Row", "category": "Strength", "tips": {
            "beginner":     "Light weight, focus on form. 3 sets of 10 reps.",
            "intermediate": "Moderate weight. 4 sets of 10 reps.",
            "advanced":     "Heavy weight, controlled tempo. 5 sets of 8 reps.",
        }},
        {"name": "Easy Walk", "category": "Light Cardio", "tips": {
            "beginner":     "20 minutes at a comfortable pace.",
            "intermediate": "30 minutes brisk walk.",
            "advanced":     "40 minutes on an incline.",
        }},
        {"name": "Cat-Cow Stretch", "category": "Mobility", "tips": {
            "beginner":     "8 slow reps to open the spine.",
            "intermediate": "10 reps with deeper range.",
            "advanced":     "12 reps paired with breath control.",
        }},
        {"name": "Foam Rolling", "category": "Recovery", "tips": {
            "beginner":     "5 minutes on quads and back.",
            "intermediate": "10 minutes full body.",
            "advanced":     "15 minutes targeted release.",
        }},
    ],
    "normal": [
        {"name": "Back Squat", "category": "Strength", "tips": {
            "beginner":     "Bodyweight or empty bar. 3 sets of 10.",
            "intermediate": "Moderate load. 4 sets of 8.",
            "advanced":     "Heavy load with controlled depth. 5 sets of 5.",
        }},
        {"name": "Bench Press", "category": "Strength", "tips": {
            "beginner":     "Light dumbbells. 3 sets of 10.",
            "intermediate": "Bar with moderate plates. 4 sets of 8.",
            "advanced":     "Heavy bar, slow eccentric. 5 sets of 5.",
        }},
        {"name": "Running", "category": "Cardio", "tips": {
            "beginner":     "Run/walk intervals for 20 minutes.",
            "intermediate": "30-minute steady jog.",
            "advanced":     "40-minute tempo or interval run.",
        }},
        {"name": "Plank", "category": "Mobility", "tips": {
            "beginner":     "3 holds of 20 seconds.",
            "intermediate": "3 holds of 45 seconds.",
            "advanced":     "3 holds of 75 seconds.",
        }},
        {"name": "Yoga Flow", "category": "Mobility", "tips": {
            "beginner":     "15-minute beginner sequence.",
            "intermediate": "30-minute vinyasa flow.",
            "advanced":     "45-minute power yoga.",
        }},
        {"name": "Recreational Sport", "category": "Skill / Sport", "tips": {
            "beginner":     "Pick something fun once a week.",
            "intermediate": "Play 60-90 minutes of sport.",
            "advanced":     "Mix sport with conditioning drills.",
        }},
    ],
    "overweight": [
        {"name": "Brisk Walking", "category": "Low-Impact Cardio", "tips": {
            "beginner":     "20 minutes, 3-4 days a week.",
            "intermediate": "40 minutes daily.",
            "advanced":     "60 minutes with hill intervals.",
        }},
        {"name": "Stationary Bike", "category": "Low-Impact Cardio", "tips": {
            "beginner":     "15 minutes easy pace.",
            "intermediate": "30 minutes moderate effort.",
            "advanced":     "45 minutes with intervals.",
        }},
        {"name": "Bodyweight Squat", "category": "Strength", "tips": {
            "beginner":     "Hold a chair for support. 3 sets of 8.",
            "intermediate": "No support. 4 sets of 10.",
            "advanced":     "Add light dumbbells. 4 sets of 12.",
        }},
        {"name": "Wall Push-Up", "category": "Strength", "tips": {
            "beginner":     "Standing against wall. 3 sets of 8.",
            "intermediate": "Incline on bench. 3 sets of 10.",
            "advanced":     "Standard floor push-up. 3 sets of 10.",
        }},
        {"name": "Hip Mobility Drills", "category": "Mobility", "tips": {
            "beginner":     "5 minutes of hip circles and stretches.",
            "intermediate": "10 minutes flow.",
            "advanced":     "15 minutes deep mobility routine.",
        }},
        {"name": "Stretch & Breathe", "category": "Recovery", "tips": {
            "beginner":     "10 minutes gentle stretch nightly.",
            "intermediate": "15 minutes guided stretch.",
            "advanced":     "20 minutes mobility + breathwork.",
        }},
    ],
    "obese": [
        {"name": "Walking", "category": "Walking / Cycling", "tips": {
            "beginner":     "10 minutes, 5 days a week.",
            "intermediate": "20-30 minutes daily.",
            "advanced":     "45 minutes brisk pace.",
        }},
        {"name": "Recumbent Bike", "category": "Walking / Cycling", "tips": {
            "beginner":     "10 minutes light resistance.",
            "intermediate": "25 minutes moderate.",
            "advanced":     "40 minutes with intervals.",
        }},
        {"name": "Water Walking", "category": "Water-Based Cardio", "tips": {
            "beginner":     "15 minutes shallow water walk.",
            "intermediate": "25 minutes with arm motion.",
            "advanced":     "40 minutes water jog.",
        }},
        {"name": "Swimming", "category": "Water-Based Cardio", "tips": {
            "beginner":     "10 minutes easy pace.",
            "intermediate": "20 minutes mixed strokes.",
            "advanced":     "30+ minutes intervals.",
        }},
        {"name": "Seated Stretching", "category": "Mobility", "tips": {
            "beginner":     "10 minutes of chair-based stretches.",
            "intermediate": "15 minutes seated + standing.",
            "advanced":     "20 minutes full mobility.",
        }},
        {"name": "Diaphragmatic Breathing", "category": "Recovery", "tips": {
            "beginner":     "5 minutes belly breathing.",
            "intermediate": "10 minutes box breathing.",
            "advanced":     "15 minutes guided meditation.",
        }},
    ],
}


def get_exercise_plan(bmi_value: float, exercise_level: Optional[str]) -> dict:
    """Build a recommendation plan for the Exercise page.

    Args:
        bmi_value:      The user's BMI as a number.
        exercise_level: Free-form level string, e.g. "Beginner", "Moderately active".

    Returns:
        A dict matching the contract used by templates/exercise.html.
    """
    category = _bmi_category(float(bmi_value))
    profile = _BMI_PROFILES[category]
    level_key = _normalize_level(exercise_level)

    exercises = [
        {
            "category": ex["category"],
            "name": ex["name"],
            "tip": ex["tips"][level_key],
        }
        for ex in _EXERCISES[category]
    ]

    return {
        "label": profile["label"],
        "focus": profile["focus"],
        "message": profile["message"],
        "categories": profile["categories"],
        "exercises": exercises,
    }