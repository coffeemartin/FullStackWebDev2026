from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from app import app, db
from flask import jsonify, render_template, flash, redirect, url_for, session, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, ExerciseLogForm
from app.models import User, Exercise, ExerciseLog, Food, LoginEvent, NutritionLog
from app.exercise_recommendation import get_exercise_plan


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('myprofile'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('Logged in successfully as {}'.format(user.username))
        login_event = LoginEvent(user_id=user.id)
        db.session.add(login_event)
        db.session.commit()
        return redirect(url_for('myprofile'))
    return render_template('login.html', title='Sign In', form=form)


# Nutrion page route
@app.route("/nutrition")
@login_required
def nutrition():
    initial_water = 0
    food_entries = []

    water_log = (
        NutritionLog.query
        .filter_by(user_id=current_user.id, log_date=date.today(), meal_type="Water")
        .order_by(NutritionLog.id.desc())
        .first()
    )
    if water_log and water_log.water_glasses:
        initial_water = water_log.water_glasses

    nutrition_logs = (
        NutritionLog.query
        .filter(NutritionLog.user_id == current_user.id)
        .filter(NutritionLog.log_date == date.today())
        .filter(NutritionLog.meal_type != "Water")
        .join(Food)
        .order_by(NutritionLog.id.asc())
        .all()
    )
    food_entries = [
        {
            "mealType": log.meal_type or "",
            "foodName": log.food.name if log.food else "",
            "quantity": log.quantity_g or 0,
            "calculatedCalories": round(((log.quantity_g or 0) / 100) * (log.food.calories_per_100g or 0)) if log.food else 0,
            "feedback": "",
            "comments": log.notes or "",
        }
        for log in nutrition_logs
    ]

    return render_template(
        'nutrition.html',
        title='Nutrition',
        initial_water=initial_water,
        food_entries=food_entries,
        nutrition_logs=nutrition_logs,
    )


@app.route("/nutrition/log", methods=["POST"])
@login_required
def save_nutrition_log():
    data = request.get_json() or {}
    meal_type = (data.get("meal_type") or "").strip()
    food_name = (data.get("food_name") or "").strip()
    quantity_g = data.get("quantity_g")
    notes = (data.get("notes") or "").strip()
    calories_per_100g = data.get("calories_per_100g")

    try:
        quantity_g = float(quantity_g)
        calories_per_100g = float(calories_per_100g)
    except (TypeError, ValueError):
        return jsonify({"error": "Quantity and calories must be valid numbers."}), 400

    if not meal_type or not food_name or quantity_g <= 0 or calories_per_100g < 0:
        return jsonify({"error": "Meal type, food name, and quantity are required."}), 400

    food = Food.query.filter(db.func.lower(Food.name) == food_name.lower()).first()
    if food is None:
        food = Food(name=food_name)
        db.session.add(food)

    food.calories_per_100g = calories_per_100g

    nutrition_log = NutritionLog(
        user_id=current_user.id,
        food=food,
        meal_type=meal_type,
        quantity_g=quantity_g,
        notes=notes,
    )
    db.session.add(nutrition_log)
    db.session.commit()

    return jsonify({
        "food_id": food.id,
        "log_id": nutrition_log.id,
        "food_name": food.name,
        "quantity_g": nutrition_log.quantity_g,
        "calories": round((quantity_g / 100) * calories_per_100g),
    })


@app.route("/nutrition/water", methods=["POST"])
@login_required
def save_water_log():
    data = request.get_json() or {}
    water_glasses = data.get("water_glasses")

    try:
        water_glasses = int(water_glasses)
    except (TypeError, ValueError):
        return jsonify({"error": "Water glasses must be a valid number."}), 400

    if water_glasses < 0:
        return jsonify({"error": "Water glasses cannot be negative."}), 400

    water_food = Food.query.filter(db.func.lower(Food.name) == "water").first()
    if water_food is None:
        water_food = Food(
            name="Water",
            calories_per_100g=0,
            protein_per_100g=0,
            carbs_per_100g=0,
            fat_per_100g=0,
        )
        db.session.add(water_food)

    water_log = (
        NutritionLog.query
        .filter_by(user_id=current_user.id, log_date=date.today(), meal_type="Water")
        .order_by(NutritionLog.id.desc())
        .first()
    )

    if water_log is None:
        water_log = NutritionLog(
            user_id=current_user.id,
            food=water_food,
            log_date=date.today(),
            meal_type="Water",
        )
        db.session.add(water_log)

    water_log.food = water_food
    water_log.quantity_g = water_glasses * 250
    water_log.water_glasses = water_glasses
    water_log.notes = "Daily water intake"
    db.session.commit()

    return jsonify({
        "log_id": water_log.id,
        "water_glasses": water_log.water_glasses,
        "quantity_g": water_log.quantity_g,
    })
# Nutrition Page end


@app.route("/exercise", methods=['GET', 'POST'])
@login_required
def exercise():
    user = current_user

    # Compute BMI and recommendation from the user's profile
    bmi_value = None
    recommendation = None
    if user.height_cm and user.weight_kg:
        bmi_value = user.weight_kg / ((user.height_cm / 100) ** 2)
        if user.activity_level:
            recommendation = get_exercise_plan(bmi_value, user.activity_level)

    form = ExerciseLogForm()

    # Populate the dropdown from the Exercise catalogue
    exercises = Exercise.query.order_by(Exercise.name).all()
    form.exercise_id.choices = [(e.id, e.name) for e in exercises]

    # Save the workout to the database
    if form.validate_on_submit():
        log = ExerciseLog(
            user_id=user.id,
            exercise_id=form.exercise_id.data,
            log_date=form.workout_date.data,
            sets=form.sets.data,
            reps=form.reps.data,
            weight_kg=float(form.weight_kg.data) if form.weight_kg.data is not None else None,
            duration_minutes=form.duration_minutes.data,
            notes=form.notes.data,
        )
        db.session.add(log)
        db.session.commit()

        chosen = db.session.get(Exercise, form.exercise_id.data)
        flash(f"Workout logged: {chosen.name}")
        return redirect(url_for('exercise'))

    # Pull the user's recent workouts from the database
    recent_logs = (
        ExerciseLog.query
        .filter_by(user_id=user.id)
        .order_by(ExerciseLog.log_date.desc(), ExerciseLog.id.desc())
        .limit(10)
        .all()
    )

    return render_template(
        'exercise.html',
        title='Exercise',
        form=form,
        recent_logs=recent_logs,
        bmi_value=bmi_value,
        exercise_level=user.activity_level,
        recommendation=recommendation,
    )


@app.route("/AI")
def AI():
    return render_template('AI.html', title='AI')


@app.route("/myprofile")
@login_required
def myprofile():
    latest_login_event = (
        LoginEvent.query.filter_by(user_id=current_user.id)
        .order_by(LoginEvent.login_at.desc())
        .first()
    )
    latest_login_at = None
    if latest_login_event:
        utc_time = latest_login_event.login_at.replace(tzinfo=timezone.utc)
        perth_time = utc_time.astimezone(ZoneInfo("Australia/Perth"))
        latest_login_at = perth_time.strftime("%Y-%m-%d %H:%M:%S %Z")

    return render_template(
        "myprofile.html",
        title="My Profile",
        user=current_user,
        latest_login_at=latest_login_at
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/details", methods=['GET', 'POST'])
def user_details():
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        height = request.form.get('height_cm')
        weight = request.form.get('weight_kg')
        injury = request.form.get('injury_notes')

        try:
            height = float(height)
            weight = float(weight)
            height_m = height / 100
            bmi = weight / (height_m ** 2)

            if bmi < 18.5:
                quote = "Start building strength and nourish your body!"
            elif bmi < 25:
                quote = "Great shape! Keep maintaining your healthy lifestyle!"
            elif bmi < 30:
                quote = "You're doing well—let's improve fitness step by step!"
            else:
                quote = "Start your fitness journey today—small steps make big changes!"

            return render_template(
                "user_details.html",
                bmi=round(bmi, 2),
                quote=quote
            )

        except:
            return "Invalid input!"

    return render_template("user_details.html")
