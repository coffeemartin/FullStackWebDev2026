from datetime import date, timedelta

from app.models import ExerciseLog, NutritionLog


def remove_none_values(data):
    return {key: value for key, value in data.items() if value is not None}

def build_ai_input(user, days=7):
    today = date.today()
    # days is the number of previous days to include (exclude today)
    start_date = today - timedelta(days=days)

    recent_exercise_logs = (
        ExerciseLog.query
        .filter(
            ExerciseLog.user_id == user.id,
            ExerciseLog.log_date >= start_date,
            ExerciseLog.log_date < today   # exclude today
        )
        .order_by(ExerciseLog.log_date.desc())
        .all()
    )

    recent_nutrition_logs = (
        NutritionLog.query
        .filter(
            NutritionLog.user_id == user.id,
            NutritionLog.log_date >= start_date,
            NutritionLog.log_date < today
        )
        .order_by(NutritionLog.log_date.desc())
        .all()
    )

    return {
        "user_profile": {
            "age": user.age,
            "gender": user.gender,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
            "goal": user.goal,
            "activity_level": user.activity_level,
            "injury_notes": user.injury_notes,
        },
          "recent_exercise_logs": [
            remove_none_values({
                "date": str(log.log_date),
                "exercise": log.exercise.name,
                "category": log.exercise.category,
                "sets": log.sets,
                "reps": log.reps,
                "weight_kg": log.weight_kg,
                "duration_minutes": log.duration_minutes,
                "notes": log.notes,
            })
            for log in recent_exercise_logs
        ],
       "recent_nutrition_logs": [
            remove_none_values({
                "date": str(log.log_date),
                "food": log.food.name,
                "meal_type": log.meal_type,
                "quantity_g": log.quantity_g,
                "notes": log.notes,
            })
            for log in recent_nutrition_logs
        ]
    }

