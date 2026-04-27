from datetime import date, timedelta
from run import app
from app import db
from app.models import User, Exercise, ExerciseLog, Food, NutritionLog
from datetime import date, timedelta

with app.app_context():

    # ---- Create User ----
    user = User(
        username="franco",
        email="franco@test.com",
        name="Franco Test",
        age=28,
        gender="Male",
        height_cm=175,
        weight_kg=78,
        goal="Build muscle and improve running endurance",
        activity_level="Moderately active",
        injury_notes="Occasional knee soreness"
    )

    user.set_password("password123")

    db.session.add(user)
    db.session.commit()

    # ---- Exercises ----
    exercises_data = [
        {"name": "Bench Press", "category": "Strength", "muscle_group": "Chest", "equipment": "Barbell"},
        {"name": "Squat", "category": "Strength", "muscle_group": "Legs", "equipment": "Barbell"},
        {"name": "Deadlift", "category": "Strength", "muscle_group": "Back", "equipment": "Barbell"},
        {"name": "Running", "category": "Cardio", "muscle_group": "Full Body", "equipment": "None"},
    ]

    exercises = [Exercise(**e) for e in exercises_data]
    db.session.add_all(exercises)
    db.session.commit()

    # ---- Exercise Logs ----
    logs = [
        ExerciseLog(user_id=user.id, exercise_id=exercises[0].id, log_date=date.today()-timedelta(days=3), sets=3, reps=8, weight_kg=60),
        ExerciseLog(user_id=user.id, exercise_id=exercises[1].id, log_date=date.today()-timedelta(days=2), sets=3, reps=10, weight_kg=80),
        ExerciseLog(user_id=user.id, exercise_id=exercises[3].id, log_date=date.today()-timedelta(days=1), duration_minutes=45),
    ]

    db.session.add_all(logs)
    db.session.commit()

    # ---- Foods ----
    foods_data = [
        {"name": "Chicken Breast", "calories_per_100g": 165, "protein_per_100g": 31, "carbs_per_100g": 0, "fat_per_100g": 3.6},
        {"name": "White Rice", "calories_per_100g": 130, "protein_per_100g": 2.7, "carbs_per_100g": 28, "fat_per_100g": 0.3},
        {"name": "Banana", "calories_per_100g": 89, "protein_per_100g": 1.1, "carbs_per_100g": 23, "fat_per_100g": 0.3},
    ]

    foods = [Food(**f) for f in foods_data]
    db.session.add_all(foods)
    db.session.commit()

    # ---- Nutrition Logs ----
    nutrition_logs = [
        NutritionLog(user_id=user.id, food_id=foods[0].id, quantity_g=200, meal_type="Lunch"),
        NutritionLog(user_id=user.id, food_id=foods[1].id, quantity_g=250, meal_type="Lunch"),
        NutritionLog(user_id=user.id, food_id=foods[2].id, quantity_g=120, meal_type="Snack"),
    ]

    db.session.add_all(nutrition_logs)
    db.session.commit()

    print("✅ Seed data created!")