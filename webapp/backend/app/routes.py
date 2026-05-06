from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from app import app, db
from flask import jsonify, render_template, flash, redirect, url_for, session, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, ExerciseLogForm
from app.models import User, Exercise, ExerciseLog, Food, LoginEvent, NutritionLog
from app.exercise_recommendation import get_exercise_plan
from sqlalchemy.exc import SQLAlchemyError


def calculate_bmi_result(height_cm, weight_kg):
    height = float(height_cm)
    weight = float(weight_kg)
    if height <= 0 or weight <= 0:
        raise ValueError("Please enter a valid height and weight.")

    height_m = height / 100
    bmi = round(weight / (height_m ** 2), 1)

    if bmi < 18.5:
        return bmi, "Underweight", "Start building strength and nourish your body!"
    if bmi < 25:
        return bmi, "Healthy weight", "Great shape! Keep maintaining your healthy lifestyle!"
    if bmi < 30:
        return bmi, "Overweight", "You are doing well. Let us improve fitness step by step!"
    return bmi, "Obese", "Start your fitness journey today. Small steps make big changes!"


def get_bmi_fitness_points(category):
    points_by_category = {
        "Underweight": [
            "Prioritise balanced meals with enough protein and healthy carbohydrates.",
            "Use strength training to build muscle gradually.",
            "Keep cardio light to moderate while you focus on healthy weight gain.",
            "Track energy levels so workouts support recovery, not exhaustion.",
            "Speak with a health professional if weight gain is difficult."
        ],
        "Healthy weight": [
            "Maintain your current habits with consistent weekly movement.",
            "Mix strength, cardio, mobility, and recovery for balance.",
            "Keep protein, vegetables, hydration, and sleep in your routine.",
            "Set performance goals such as more reps, better pace, or flexibility.",
            "Use your BMI as one guide, not the only measure of progress."
        ],
        "Overweight": [
            "Start with realistic sessions such as walking, cycling, or full-body circuits.",
            "Add strength training to support metabolism and protect joints.",
            "Choose small nutrition changes you can repeat every week.",
            "Increase workout time slowly instead of jumping into intense plans.",
            "Celebrate consistency before focusing only on the scale."
        ],
        "Obese": [
            "Begin with low-impact exercise to protect knees, hips, and back.",
            "Aim for short, repeatable movement sessions throughout the week.",
            "Pair activity with simple meal planning and regular hydration.",
            "Use strength exercises at a comfortable level to build confidence.",
            "Consider professional guidance for a safe long-term plan."
        ]
    }
    return points_by_category.get(category, [
        "Add height and weight to unlock BMI-based fitness guidance.",
        "Begin with simple movement you can repeat consistently.",
        "Balance exercise with sleep, hydration, and nutrition.",
        "Avoid comparing your progress with someone else's journey.",
        "Small improvements each week can become lasting habits."
    ])


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('myprofile'))

    form = LoginForm()
    show_signup = False
    form_data = {}
    bmi = None
    category = None
    quote = None

    if request.method == 'POST' and request.form.get('form_type') == 'new_user':
        show_signup = True
        form_data = {
            'username': request.form.get('new_username', '').strip(),
            'email': request.form.get('email', '').strip(),
            'name': request.form.get('name', '').strip(),
            'age': request.form.get('age', '').strip(),
            'gender': request.form.get('gender', '').strip(),
            'height_cm': request.form.get('height_cm', '').strip(),
            'weight_kg': request.form.get('weight_kg', '').strip(),
            'goal': request.form.get('goal', '').strip(),
            'activity_level': request.form.get('activity_level', '').strip(),
            'injury_notes': request.form.get('injury_notes', '').strip()
        }
        password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        try:
            if not form_data['username'] or not form_data['email'] or not password:
                raise ValueError("Please enter a login ID, email, and password.")
            if password != confirm_password:
                raise ValueError("Passwords do not match.")
            if User.query.filter_by(username=form_data['username']).first():
                raise ValueError("That login ID is already taken.")
            if User.query.filter_by(email=form_data['email']).first():
                raise ValueError("That email is already registered.")

            bmi, category, quote = calculate_bmi_result(
                form_data['height_cm'],
                form_data['weight_kg']
            )

            user = User(
                username=form_data['username'],
                email=form_data['email'],
                name=form_data['name'],
                age=int(form_data['age']) if form_data['age'] else None,
                gender=form_data['gender'],
                height_cm=float(form_data['height_cm']) if form_data['height_cm'] else None,
                weight_kg=float(form_data['weight_kg']) if form_data['weight_kg'] else None,
                goal=form_data['goal'],
                activity_level=form_data['activity_level'],
                injury_notes=form_data['injury_notes']
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            login_user(user)
            flash("Profile created successfully.")
        except ValueError as error:
            flash(str(error))
        except SQLAlchemyError:
            db.session.rollback()
            flash("Profile could not be saved right now. Please try again.")

    elif form.validate_on_submit():
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

    return render_template(
        'login.html',
        title='Sign In',
        form=form,
        form_data=form_data,
        show_signup=show_signup,
        bmi=bmi,
        category=category,
        quote=quote
    )


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


@app.route("/myprofile", methods=['GET', 'POST'])
@login_required
def myprofile():
    if request.method == 'POST' and request.form.get('form_type') == 'add_friend':
        friend_username = request.form.get('friend_username', '').strip()
        if friend_username:
            flash(f"Friend request ready for {friend_username}.")
        else:
            flash("Please choose a friend to add.")

    bmi = None
    bmi_category = None
    bmi_quote = "Add your height and weight to unlock your BMI guidance."
    fitness_points = get_bmi_fitness_points(None)

    if current_user.height_cm and current_user.weight_kg:
        try:
            bmi, bmi_category, bmi_quote = calculate_bmi_result(
                current_user.height_cm,
                current_user.weight_kg
            )
            fitness_points = get_bmi_fitness_points(bmi_category)
        except ValueError:
            pass

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

    app_friends = (
        User.query
        .filter(User.id != current_user.id)
        .order_by(User.username)
        .limit(6)
        .all()
    )

    return render_template(
        "myprofile.html",
        title="My Profile",
        user=current_user,
        latest_login_at=latest_login_at,
        bmi=bmi,
        bmi_category=bmi_category,
        bmi_quote=bmi_quote,
        fitness_points=fitness_points,
        app_friends=app_friends
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
                quote = "You're doing well. Let's improve fitness step by step!"
            else:
                quote = "Start your fitness journey today. Small steps make big changes!"

            return render_template(
                "user_details.html",
                bmi=round(bmi, 2),
                quote=quote
            )

        except:
            return "Invalid input!"

    return render_template("user_details.html")
