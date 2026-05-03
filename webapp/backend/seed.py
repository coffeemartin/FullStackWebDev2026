from datetime import date, timedelta

from run import app
from app import db
from app.models import User, Exercise, ExerciseLog, Food, NutritionLog


with app.app_context():
    # ---- Create or get user ----
    user = User.query.filter_by(username="franco").first()
    if not user:
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
            injury_notes="Occasional knee soreness",
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
        {"name": "Goblet Squat", "category": "Strength", "muscle_group": "Legs", "equipment": "Dumbbell"},
        {"name": "Push-Up", "category": "Strength", "muscle_group": "Chest", "equipment": "None"},
        {"name": "Dumbbell Row", "category": "Strength", "muscle_group": "Back", "equipment": "Dumbbell"},
        {"name": "Easy Walk", "category": "Light Cardio", "muscle_group": "Full Body", "equipment": "None"},
        {"name": "Cat-Cow Stretch", "category": "Mobility", "muscle_group": "Spine", "equipment": "None"},
        {"name": "Foam Rolling", "category": "Recovery", "muscle_group": "Full Body", "equipment": "Foam Roller"},
        {"name": "Back Squat", "category": "Strength", "muscle_group": "Legs", "equipment": "Barbell"},
        {"name": "Plank", "category": "Mobility", "muscle_group": "Core", "equipment": "None"},
        {"name": "Yoga Flow", "category": "Mobility", "muscle_group": "Full Body", "equipment": "Mat"},
        {"name": "Recreational Sport", "category": "Skill / Sport", "muscle_group": "Full Body", "equipment": "Varies"},
        {"name": "Brisk Walking", "category": "Low-Impact Cardio", "muscle_group": "Full Body", "equipment": "None"},
        {"name": "Stationary Bike", "category": "Low-Impact Cardio", "muscle_group": "Legs", "equipment": "Bike"},
        {"name": "Bodyweight Squat", "category": "Strength", "muscle_group": "Legs", "equipment": "None"},
        {"name": "Wall Push-Up", "category": "Strength", "muscle_group": "Chest", "equipment": "Wall"},
        {"name": "Hip Mobility Drills", "category": "Mobility", "muscle_group": "Hips", "equipment": "None"},
        {"name": "Stretch & Breathe", "category": "Recovery", "muscle_group": "Full Body", "equipment": "None"},
        {"name": "Walking", "category": "Walking / Cycling", "muscle_group": "Full Body", "equipment": "None"},
        {"name": "Recumbent Bike", "category": "Walking / Cycling", "muscle_group": "Legs", "equipment": "Recumbent Bike"},
        {"name": "Water Walking", "category": "Water-Based Cardio", "muscle_group": "Full Body", "equipment": "Pool"},
        {"name": "Swimming", "category": "Water-Based Cardio", "muscle_group": "Full Body", "equipment": "Pool"},
        {"name": "Seated Stretching", "category": "Mobility", "muscle_group": "Full Body", "equipment": "Chair"},
        {"name": "Diaphragmatic Breathing", "category": "Recovery", "muscle_group": "Core", "equipment": "None"},
    ]

    for item in exercises_data:
        existing = Exercise.query.filter_by(name=item["name"]).first()
        if not existing:
            db.session.add(Exercise(**item))

    db.session.commit()

    exercise_by_name = {exercise.name: exercise for exercise in Exercise.query.all()}

    # ---- Exercise Logs ----
    if not ExerciseLog.query.filter_by(user_id=user.id).first():
        logs = [
            ExerciseLog(
                user_id=user.id,
                exercise_id=exercise_by_name["Bench Press"].id,
                log_date=date.today() - timedelta(days=3),
                sets=3,
                reps=8,
                weight_kg=60,
            ),
            ExerciseLog(
                user_id=user.id,
                exercise_id=exercise_by_name["Squat"].id,
                log_date=date.today() - timedelta(days=2),
                sets=3,
                reps=10,
                weight_kg=80,
            ),
            ExerciseLog(
                user_id=user.id,
                exercise_id=exercise_by_name["Running"].id,
                log_date=date.today() - timedelta(days=1),
                duration_minutes=45,
            ),
        ]
        db.session.add_all(logs)
        db.session.commit()

    # ---- Foods ----
    foods_data = [
        {"name": "Chicken Breast", "calories_per_100g": 165, "protein_per_100g": 31, "carbs_per_100g": 0, "fat_per_100g": 3.6},
        {"name": "White Rice", "calories_per_100g": 130, "protein_per_100g": 2.7, "carbs_per_100g": 28, "fat_per_100g": 0.3},
        {"name": "Banana", "calories_per_100g": 89, "protein_per_100g": 1.1, "carbs_per_100g": 23, "fat_per_100g": 0.3},
    ]

    for item in foods_data:
        existing = Food.query.filter_by(name=item["name"]).first()
        if not existing:
            db.session.add(Food(**item))

    db.session.commit()

    food_by_name = {food.name: food for food in Food.query.all()}

    # ---- Nutrition Logs ----
    if not NutritionLog.query.filter_by(user_id=user.id).first():
        nutrition_logs = [
            NutritionLog(user_id=user.id, food_id=food_by_name["Chicken Breast"].id, quantity_g=200, meal_type="Lunch"),
            NutritionLog(user_id=user.id, food_id=food_by_name["White Rice"].id, quantity_g=250, meal_type="Lunch"),
            NutritionLog(user_id=user.id, food_id=food_by_name["Banana"].id, quantity_g=120, meal_type="Snack"),
        ]
        db.session.add_all(nutrition_logs)
        db.session.commit()

    print("Seed data ready.")
