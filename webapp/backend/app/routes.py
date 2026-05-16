from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from app import app, db
from flask import jsonify, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, ExerciseLogForm, CSRFOnlyForm
from app.models import User, Exercise, ExerciseLog, Food, Friendship, LoginEvent, NutritionLog
from app.exercise_recommendation import get_exercise_plan
from sqlalchemy import and_, or_, func
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


def find_friendship_between(user_id, other_user_id):
    return Friendship.query.filter(or_(
        and_(Friendship.requester_id == user_id, Friendship.receiver_id == other_user_id),
        and_(Friendship.requester_id == other_user_id, Friendship.receiver_id == user_id)
    )).first()


def users_are_friends(user_id, other_user_id):
    friendship = find_friendship_between(user_id, other_user_id)
    return bool(friendship and friendship.status == "accepted")


def get_connected_friend_user_ids(user_id):
    connected_friendships = Friendship.query.filter(
        or_(
            Friendship.requester_id == user_id,
            Friendship.receiver_id == user_id
        ),
        Friendship.status.in_(["pending", "accepted"])
    ).all()
    return {
        item.receiver_id if item.requester_id == user_id else item.requester_id
        for item in connected_friendships
    }


def search_available_friends(user_id, search_term, limit=8):
    if not search_term:
        return []

    connected_user_ids = get_connected_friend_user_ids(user_id)
    search_pattern = f"%{search_term}%"
    query = (
        User.query
        .filter(User.id != user_id)
        .filter(or_(
            User.name.ilike(search_pattern),
            User.username.ilike(search_pattern),
            User.email.ilike(search_pattern)
        ))
    )
    if connected_user_ids:
        query = query.filter(~User.id.in_(connected_user_ids))
    return query.order_by(User.username).limit(limit).all()


def get_friend_suggestions(user_id, limit=8):
    connected_user_ids = get_connected_friend_user_ids(user_id)
    query = User.query.filter(User.id != user_id)
    if connected_user_ids:
        query = query.filter(~User.id.in_(connected_user_ids))
    return query.order_by(User.username).limit(limit).all()


def get_latest_nutrition_summary(user_id):
    latest_log = (
        NutritionLog.query
        .filter(NutritionLog.user_id == user_id)
        .filter(NutritionLog.meal_type != "Water")
        .join(Food)
        .order_by(NutritionLog.log_date.desc(), NutritionLog.id.desc())
        .first()
    )
    if not latest_log or not latest_log.food:
        return None

    quantity_ratio = (latest_log.quantity_g or 0) / 100
    return {
        "food_name": latest_log.food.name,
        "meal_type": latest_log.meal_type or "Meal",
        "log_date": latest_log.log_date,
        "calories": round(quantity_ratio * (latest_log.food.calories_per_100g or 0)),
        "protein": round(quantity_ratio * (latest_log.food.protein_per_100g or 0), 1),
        "carbs": round(quantity_ratio * (latest_log.food.carbs_per_100g or 0), 1),
        "fat": round(quantity_ratio * (latest_log.food.fat_per_100g or 0), 1),
    }


def serialize_nutrition_log(log, is_previous_day=False):
    quantity_ratio = (log.quantity_g or 0) / 100
    food = log.food
    return {
        "id": log.id,
        "mealType": log.meal_type or "",
        "foodName": food.name if food else "",
        "quantity": log.quantity_g or 0,
        "calculatedCalories": round(quantity_ratio * (food.calories_per_100g or 0)) if food else 0,
        "protein": round(quantity_ratio * (food.protein_per_100g or 0), 1) if food else 0,
        "carbs": round(quantity_ratio * (food.carbs_per_100g or 0), 1) if food else 0,
        "fat": round(quantity_ratio * (food.fat_per_100g or 0), 1) if food else 0,
        "comments": log.notes or "",
        "logDate": log.log_date.isoformat(),
        "isPreviousDay": is_previous_day,
    }


def get_nutrition_relative_label(log_date):
    day_delta = (log_date - get_app_today()).days
    if day_delta == 0:
        return "Today"
    if day_delta == -1:
        return "Yesterday"
    if day_delta == 1:
        return "Tomorrow"
    return None


def build_grouped_recent_nutrition_logs(user_id, limit=10):
    recent_logs = (
        NutritionLog.query
        .filter(NutritionLog.user_id == user_id)
        .filter(NutritionLog.meal_type != "Water")
        .join(Food)
        .order_by(NutritionLog.log_date.desc(), NutritionLog.id.desc())
        .limit(limit)
        .all()
    )

    grouped_logs = []
    grouped_logs_by_date = {}

    for log in recent_logs:
        day_group = grouped_logs_by_date.get(log.log_date)
        if day_group is None:
            water_total = (
                db.session.query(func.sum(NutritionLog.water_glasses))
                .filter_by(user_id=user_id, log_date=log.log_date, meal_type="Water")
                .scalar()
            ) or 0

            day_group = {
                "log_date": log.log_date,
                "relative_label": get_nutrition_relative_label(log.log_date),
                "entries": [],
                "food_count": 0,
                "total_calories": 0,
                "total_protein": 0,
                "total_carbs": 0,
                "total_fat": 0,
                "water_glasses": int(water_total),
            }
            grouped_logs_by_date[log.log_date] = day_group
            grouped_logs.append(day_group)

        entry = serialize_nutrition_log(log)
        day_group["entries"].append(entry)
        day_group["food_count"] += 1
        day_group["total_calories"] += entry["calculatedCalories"]
        day_group["total_protein"] += entry["protein"]
        day_group["total_carbs"] += entry["carbs"]
        day_group["total_fat"] += entry["fat"]

    return grouped_logs


def get_latest_workout_summary(user_id):
    return (
        ExerciseLog.query
        .filter_by(user_id=user_id)
        .join(Exercise)
        .order_by(ExerciseLog.log_date.desc(), ExerciseLog.id.desc())
        .first()
    )

from app.ai_page import * 
from app.ai_service import generate_ai_plan
from app.models import LLMRecommendation
import json
from werkzeug.datastructures import MultiDict


APP_TIMEZONE = ZoneInfo("Australia/Perth")


def get_app_today():
    return datetime.now(APP_TIMEZONE).date()



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
    selected_date = request.args.get("date", "")
    today = get_app_today()
    try:
        selected_date_date = date.fromisoformat(selected_date) if selected_date else today
    except ValueError:
        selected_date_date = today
    if selected_date_date > today:
        selected_date_date = today

    selected_date_str = selected_date_date.isoformat()
    selected_date_label = (
        "Today's Food Entries"
        if selected_date_date == today
        else f"Food Entries for {selected_date_str}"
    )

    initial_water = 0
    food_entries = []
    previous_day_entries = []
    water_by_date = {}
    water_logged_dates = {}

    water_log = (
        NutritionLog.query
        .filter_by(user_id=current_user.id, log_date=selected_date_date, meal_type="Water")
        .order_by(NutritionLog.id.desc())
        .first()
    )
    if water_log and water_log.water_glasses:
        initial_water = water_log.water_glasses
    water_by_date[selected_date_str] = initial_water
    water_logged_dates[selected_date_str] = water_log is not None

    foods = Food.query.order_by(Food.name).all()
    food_options = [food.name for food in foods if food.name.lower() != "water"]
    food_calories = {food.name.lower(): food.calories_per_100g or 0 for food in foods}
    food_macros = {
        food.name.lower(): {
            "calories": food.calories_per_100g or 0,
            "protein": food.protein_per_100g or 0,
            "carbs": food.carbs_per_100g or 0,
            "fat": food.fat_per_100g or 0,
        }
        for food in foods
    }

    nutrition_logs = (
        NutritionLog.query
        .filter(NutritionLog.user_id == current_user.id)
        .filter(NutritionLog.log_date == selected_date_date)
        .filter(NutritionLog.meal_type != "Water")
        .join(Food)
        .order_by(NutritionLog.id.asc())
        .all()
    )
    food_entries = [serialize_nutrition_log(log) for log in nutrition_logs]

    # Fetch previous day's food entries if viewing today
    if selected_date_date == today:
        previous_date = selected_date_date - timedelta(days=1)
        previous_water_log = (
            NutritionLog.query
            .filter_by(user_id=current_user.id, log_date=previous_date, meal_type="Water")
            .order_by(NutritionLog.id.desc())
            .first()
        )
        water_by_date[previous_date.isoformat()] = (
            previous_water_log.water_glasses
            if previous_water_log and previous_water_log.water_glasses
            else 0
        )
        water_logged_dates[previous_date.isoformat()] = previous_water_log is not None
        previous_logs = (
            NutritionLog.query
            .filter(NutritionLog.user_id == current_user.id)
            .filter(NutritionLog.log_date == previous_date)
            .filter(NutritionLog.meal_type != "Water")
            .join(Food)
            .order_by(NutritionLog.id.asc())
            .all()
        )
        previous_day_entries = [serialize_nutrition_log(log, True) for log in previous_logs]

    grouped_recent_nutrition_logs = build_grouped_recent_nutrition_logs(current_user.id)

    return render_template(
        'nutrition.html',
        title='Nutrition',
        initial_water=initial_water,
        food_entries=food_entries,
        previous_day_entries=previous_day_entries,
        water_by_date=water_by_date,
        water_logged_dates=water_logged_dates,
        nutrition_logs=nutrition_logs,
        selected_date=selected_date_str,
        selected_date_label=selected_date_label,
        server_today=today.isoformat(),
        food_options=food_options,
        food_calories=food_calories,
        food_macros=food_macros,
        grouped_recent_nutrition_logs=grouped_recent_nutrition_logs,
    )


@app.route("/nutrition/data")
@login_required
def nutrition_data():
    # Return nutrition data for a given date as JSON (used by client-side date picker)
    selected_date = request.args.get("date", "")
    today = get_app_today()
    try:
        selected_date_date = date.fromisoformat(selected_date) if selected_date else today
    except ValueError:
        selected_date_date = today
    if selected_date_date > today:
        selected_date_date = today

    selected_date_str = selected_date_date.isoformat()

    initial_water = 0
    food_entries = []
    previous_day_entries = []
    water_by_date = {}
    water_logged_dates = {}

    foods = Food.query.order_by(Food.name).all()
    food_options = [food.name for food in foods if food.name.lower() != "water"]
    food_calories = {food.name.lower(): food.calories_per_100g or 0 for food in foods}
    food_macros = {
        food.name.lower(): {
            "calories": food.calories_per_100g or 0,
            "protein": food.protein_per_100g or 0,
            "carbs": food.carbs_per_100g or 0,
            "fat": food.fat_per_100g or 0,
        }
        for food in foods
    }

    water_log = (
        NutritionLog.query
        .filter_by(user_id=current_user.id, log_date=selected_date_date, meal_type="Water")
        .order_by(NutritionLog.id.desc())
        .first()
    )
    if water_log and water_log.water_glasses:
        initial_water = water_log.water_glasses
    water_by_date[selected_date_str] = initial_water
    water_logged_dates[selected_date_str] = water_log is not None

    nutrition_logs = (
        NutritionLog.query
        .filter(NutritionLog.user_id == current_user.id)
        .filter(NutritionLog.log_date == selected_date_date)
        .filter(NutritionLog.meal_type != "Water")
        .join(Food)
        .order_by(NutritionLog.id.asc())
        .all()
    )
    food_entries = [serialize_nutrition_log(log) for log in nutrition_logs]

    # Fetch previous day's food entries if viewing today
    if selected_date_date == today:
        previous_date = selected_date_date - timedelta(days=1)
        previous_water_log = (
            NutritionLog.query
            .filter_by(user_id=current_user.id, log_date=previous_date, meal_type="Water")
            .order_by(NutritionLog.id.desc())
            .first()
        )
        water_by_date[previous_date.isoformat()] = (
            previous_water_log.water_glasses
            if previous_water_log and previous_water_log.water_glasses
            else 0
        )
        water_logged_dates[previous_date.isoformat()] = previous_water_log is not None
        previous_logs = (
            NutritionLog.query
            .filter(NutritionLog.user_id == current_user.id)
            .filter(NutritionLog.log_date == previous_date)
            .filter(NutritionLog.meal_type != "Water")
            .join(Food)
            .order_by(NutritionLog.id.asc())
            .all()
        )
        previous_day_entries = [serialize_nutrition_log(log, True) for log in previous_logs]

    return jsonify({
        "food_entries": food_entries,
        "previous_day_entries": previous_day_entries,
        "initial_water": initial_water,
        "water_by_date": water_by_date,
        "water_logged_dates": water_logged_dates,
        "selected_date": selected_date_str,
        "server_today": today.isoformat(),
        "food_options": food_options,
        "food_calories": food_calories,
        "food_macros": food_macros,
    })


@app.route("/nutrition/log", methods=["POST"])
@login_required
def save_nutrition_log():
    data = request.get_json() or {}
    today = get_app_today()
    meal_type = (data.get("meal_type") or "").strip()
    food_name = (data.get("food_name") or "").strip()
    quantity_g = data.get("quantity_g")
    log_date = data.get("log_date")
    notes = (data.get("notes") or "").strip()
    calories_per_100g = data.get("calories_per_100g")
    protein_per_100g = data.get("protein_per_100g", 0)
    carbs_per_100g = data.get("carbs_per_100g", 0)
    fat_per_100g = data.get("fat_per_100g", 0)

    if log_date:
        try:
            log_date = date.fromisoformat(log_date)
        except ValueError:
            return jsonify({"error": "Log date must be a valid ISO date."}), 400
    else:
        log_date = today

    if log_date > today:
        return jsonify({"error": "Food entries can only be logged for today or previous dates."}), 400

    try:
        quantity_g = float(quantity_g)
        calories_per_100g = float(calories_per_100g)
        protein_per_100g = float(protein_per_100g or 0)
        carbs_per_100g = float(carbs_per_100g or 0)
        fat_per_100g = float(fat_per_100g or 0)
    except (TypeError, ValueError):
        return jsonify({"error": "Quantity, calories, and macros must be valid numbers."}), 400

    if (
        not meal_type
        or not food_name
        or quantity_g <= 0
        or calories_per_100g < 0
        or protein_per_100g < 0
        or carbs_per_100g < 0
        or fat_per_100g < 0
    ):
        return jsonify({"error": "Meal type, food name, quantity, and non-negative nutrition values are required."}), 400

    food = Food.query.filter(db.func.lower(Food.name) == food_name.lower()).first()
    if food is None:
        food = Food(name=food_name)
        db.session.add(food)

    food.calories_per_100g = calories_per_100g
    food.protein_per_100g = protein_per_100g
    food.carbs_per_100g = carbs_per_100g
    food.fat_per_100g = fat_per_100g

    nutrition_log = NutritionLog(
        user_id=current_user.id,
        food=food,
        meal_type=meal_type,
        quantity_g=quantity_g,
        log_date=log_date,
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
        "protein": round((quantity_g / 100) * protein_per_100g, 1),
        "carbs": round((quantity_g / 100) * carbs_per_100g, 1),
        "fat": round((quantity_g / 100) * fat_per_100g, 1),
        "log_date": nutrition_log.log_date.isoformat(),
    })


@app.route("/nutrition/log/<int:log_id>", methods=["DELETE"])
@login_required
def delete_nutrition_log(log_id):
    nutrition_log = (
        NutritionLog.query
        .filter_by(id=log_id, user_id=current_user.id)
        .filter(NutritionLog.meal_type != "Water")
        .first()
    )

    if nutrition_log is None:
        return jsonify({"error": "Food entry was not found."}), 404

    db.session.delete(nutrition_log)
    db.session.commit()
    return jsonify({"deleted": True, "log_id": log_id})


@app.route("/nutrition/water", methods=["POST"])
@login_required
def save_water_log():
    data = request.get_json() or {}
    today = get_app_today()
    water_glasses = data.get("water_glasses")
    log_date = data.get("log_date")

    try:
        water_glasses = int(water_glasses)
    except (TypeError, ValueError):
        return jsonify({"error": "Water glasses must be a valid number."}), 400

    if water_glasses < 0:
        return jsonify({"error": "Water glasses cannot be negative."}), 400

    if log_date:
        try:
            log_date = date.fromisoformat(log_date)
        except ValueError:
            return jsonify({"error": "Log date must be a valid ISO date."}), 400
    else:
        log_date = today

    if log_date > today:
        return jsonify({"error": "Water intake can only be logged for today or previous dates."}), 400

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
        .filter_by(user_id=current_user.id, log_date=log_date, meal_type="Water")
        .order_by(NutritionLog.id.desc())
        .first()
    )

    if water_log is None:
        water_log = NutritionLog(
            user_id=current_user.id,
            food=water_food,
            log_date=log_date,
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

    grouped_recent_logs = []
    grouped_recent_logs_by_date = {}

    # Group the latest entries by workout date so the history reads as one daily story.
    for log in recent_logs:
        category = log.exercise.category if log.exercise and log.exercise.category else "Workout"
        category_lower = category.lower()
        is_strength = "strength" in category_lower
        is_cardio_style = any(token in category_lower for token in ("cardio", "walking", "cycling", "water", "sport"))
        is_mobility = "mobility" in category_lower
        is_recovery = "recovery" in category_lower

        filter_tokens = []
        if is_strength:
            filter_tokens.append("strength")
        if is_cardio_style:
            filter_tokens.append("cardio")
        if is_mobility:
            filter_tokens.append("mobility")
        if is_recovery:
            filter_tokens.append("recovery")
        if not filter_tokens:
            filter_tokens.append("other")

        day_group = grouped_recent_logs_by_date.get(log.log_date)
        if day_group is None:
            day_delta = (log.log_date - date.today()).days
            relative_label = None
            if day_delta == 0:
                relative_label = "Today"
            elif day_delta == -1:
                relative_label = "Yesterday"
            elif day_delta == 1:
                relative_label = "Tomorrow"

            day_group = {
                "log_date": log.log_date,
                "relative_label": relative_label,
                "entries": [],
                "filter_tokens": [],
                "primary_filter": filter_tokens[0],
                "workout_count": 0,
                "total_minutes": 0,
            }
            grouped_recent_logs_by_date[log.log_date] = day_group
            grouped_recent_logs.append(day_group)

        for token in filter_tokens:
            if token not in day_group["filter_tokens"]:
                day_group["filter_tokens"].append(token)

        day_group["entries"].append({
            "log": log,
            "category": category,
            "category_lower": category_lower,
            "is_strength": is_strength,
            "is_cardio_style": is_cardio_style,
        })
        day_group["workout_count"] += 1
        day_group["total_minutes"] += log.duration_minutes or 0

    # Dashboard stats
    total_workouts = ExerciseLog.query.filter_by(user_id=user.id).count()

    week_start = date.today() - timedelta(days=date.today().weekday())
    workouts_this_week = (
        ExerciseLog.query
        .filter_by(user_id=user.id)
        .filter(ExerciseLog.log_date >= week_start)
        .count()
    )

    total_minutes_raw = (
        db.session.query(func.sum(ExerciseLog.duration_minutes))
        .filter_by(user_id=user.id)
        .scalar()
    )
    total_minutes = int(total_minutes_raw) if total_minutes_raw else 0

    return render_template(
        'exercise.html',
        title='Exercise',
        form=form,
        exercise_options=exercises,
        recent_logs=recent_logs,
        grouped_recent_logs=grouped_recent_logs,
        bmi_value=bmi_value,
        exercise_level=user.activity_level,
        recommendation=recommendation,
        total_workouts=total_workouts,
        workouts_this_week=workouts_this_week,
        total_minutes=total_minutes,
    )

# this route allows user to update personal profile and generate new AI plan based on the updated profile and recent logs,
# all in one flow. If user want to update the generated plan, that will be handled by a separate route /AI/save-all 
# which only updates the training plan of the latest recommendation.
@app.route("/AI", methods=["GET", "POST"])
@login_required
def AI():
    csrf_form = CSRFOnlyForm()
    # maximum days of history allowed to include in LLM input
    MAX_HISTORY_DAYS = 90

    if request.method == "POST":
        if not csrf_form.validate_on_submit():
            flash("Your session expired. Please try again.")
            return redirect(url_for("AI"))
       
        form_action = request.form.get("form_action", "generate")
        # If user submitted the profile update form, update the user's profile and return without generating new plan
        # This form_action is corresponding to the hidden input field in the profile edit form, 
        # which allows me to use the same route for both profile updates and plan generation.
        if form_action == "update_profile":
            current_user.age = _coerce_int(request.form.get("age"))
            current_user.height_cm = _coerce_float(request.form.get("height_cm"))
            current_user.weight_kg = _coerce_float(request.form.get("weight_kg"))
            current_user.goal = request.form.get("goal", "").strip() or None
            current_user.injury_notes = request.form.get("injury_notes", "").strip() or None

            db.session.commit()
            flash("Your profile has been updated.")
            return redirect(url_for("AI"))


        # Ifg form_action is not profile update, proceed to generate new plan. 
        # This allows user to update their profile and immediately see the impact of their changes on the generated plan in one seamless flow.
        # allow user to specify number of days of history (cap to 90, default to 30) to include in LLM input when generating plan
        try:
            days = int(request.form.get("history_days", 30))
        except (TypeError, ValueError):
            days = 30

        if days < 1:
            days = 1
        if days > MAX_HISTORY_DAYS:
            days = MAX_HISTORY_DAYS

        # allow user to control creativity, clamp to [0, 1], default 0
        try:
            temperature = float(request.form.get("temperature", 0))
        except (TypeError, ValueError):
            temperature = 0.0

        if temperature < 0:
            temperature = 0.0
        if temperature > 1:
            temperature = 1.0

        ai_input = build_ai_input(current_user, days=days)
        ai_response = generate_ai_plan(ai_input, temperature=temperature)

        recommendation = LLMRecommendation(
            user_id=current_user.id,
            input_summary=json.dumps(ai_input),
            llm_comments=ai_response["summary_comment"],
        )

        recommendation.set_training_plan(ai_response["weekly_training_plan"])
        recommendation.set_nutrition_plan(ai_response["nutrition_plan"])

        db.session.add(recommendation)
        db.session.commit()

        flash("Customised plan generated successfully.")
        ## Updated this to inlcude the new recommendation id as query param,
        ## so that after generation, the page will show the newly generated plan 
        # instead of defaulting back to the most recent saved plan.
        return redirect(url_for("AI", recommendation_id=recommendation.id))


    recommendation_id = request.args.get("recommendation_id", type=int)
    latest_recommendation = None

    # firstly try to find the recommendation based on the recommendation_id query param, 
    # which is set after a new plan generation or when user clicks on a past plan to view details. 
    # This allows the page to show the generated plan right after generation.
    if recommendation_id is not None:
        latest_recommendation = LLMRecommendation.query.filter_by(
            id=recommendation_id,
            user_id=current_user.id,
        ).first()

    # If no recommendation found based on the query param, then try to find the user's current plan.
    if latest_recommendation is None:
        # On GET, prefer the user's current plan. If they have not marked one yet,
        # fall back to the most recent recommendation so the page still has a plan to show.
        latest_recommendation = (
            LLMRecommendation.query
            .filter_by(user_id=current_user.id, is_current=True)
            .order_by(LLMRecommendation.created_at.desc())
            .first()
        # if current plan not found, fall back to most recent recommendation to show on the page 
        ) or (
            LLMRecommendation.query
            .filter_by(user_id=current_user.id)
            .order_by(LLMRecommendation.created_at.desc())
            .first()
        )
    # On GET, show the recent 5 saved recommendations from the database
    saved_recommendations = (
        LLMRecommendation.query
        .filter_by(user_id=current_user.id, user_saved=True)
        .order_by(LLMRecommendation.created_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "AI.html",
        latest_recommendation=latest_recommendation,
        saved_recommendations=saved_recommendations,
        csrf_form=csrf_form,
    )


def _coerce_int(value):
    value = (value or "").strip()
    if not value:
        return None
    return int(value)


def _coerce_float(value):
    value = (value or "").strip()
    if not value:
        return None
    return float(value)

@app.route("/AI/save-all", methods=["POST"]) 
@login_required
def save_ai_all():
    csrf_form = CSRFOnlyForm()
    if not csrf_form.validate_on_submit():
        flash("Your edit session expired. Please try again.")
        return redirect(url_for("AI"))

    recommendation_id = request.form.get("recommendation_id", type=int)
    training_plan_json = request.form.get("training_plan_json", "")

    if recommendation_id is None or not training_plan_json:
        flash("Could not save that plan.")
        return redirect(url_for("AI"))

    recommendation = LLMRecommendation.query.filter_by(
        id=recommendation_id,
        user_id=current_user.id,
    ).first()

    if recommendation is None:
        flash("Could not find that AI plan.")
        return redirect(url_for("AI"))

    try:
        training_plan = json.loads(training_plan_json)
    except Exception:
        flash("Invalid plan data.")
        return redirect(url_for("AI"))

    recommendation.set_training_plan(training_plan)

    # Extract exercise names from the training plan and add to Exercise table if needed
    try:
        for day in training_plan:
            for exercise in day.get("exercises", []):
                exercise_name = exercise.get("name", "").strip()

                if exercise_name:
                    existing_exercise = Exercise.query.filter(
                        db.func.lower(Exercise.name) == exercise_name.lower()
                    ).first()

                    if existing_exercise is None:
                        new_exercise = Exercise(
                            name=exercise_name,
                            category=None,
                            muscle_group=None,
                            equipment=None,
                        )
                        db.session.add(new_exercise)
    except Exception as e:
        # Log the error but don't fail the save
        flash(f"Warning: Could not add some exercises to your exercise library: {str(e)}")

    # If request included mark_saved, mark this recommendation as saved
    mark_saved = request.form.get("mark_saved")
    if mark_saved:
        recommendation.user_saved = True

    db.session.commit()

    flash("All edits saved.{}".format(" Plan added to your profile." if mark_saved else ""))
    return redirect(url_for("AI"))


@app.route("/AI/set-current", methods=["POST"])
@login_required
def set_current_reco():
    csrf_form = CSRFOnlyForm()
    if not csrf_form.validate_on_submit():
        return jsonify({"success": False, "error": "Session expired."}), 400

    recommendation_id = request.form.get("recommendation_id", type=int)
    if recommendation_id is None:
        return jsonify({"success": False, "error": "Missing recommendation id."}), 400

    recommendation = LLMRecommendation.query.filter_by(
        id=recommendation_id,
        user_id=current_user.id,
    ).first()

    if recommendation is None:
        return jsonify({"success": False, "error": "Recommendation not found."}), 404

    try:
        LLMRecommendation.query.filter_by(
            user_id=current_user.id,
            is_current=True,
        ).update({"is_current": None})
        recommendation.is_current = True
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/AI/delete-reco", methods=["POST"])
@login_required
def delete_reco():
    csrf_form = CSRFOnlyForm()
    if not csrf_form.validate_on_submit():
        return jsonify({"success": False, "error": "Session expired."}), 400

    recommendation_id = request.form.get("recommendation_id", type=int)
    if recommendation_id is None:
        return jsonify({"success": False, "error": "Missing recommendation id."}), 400

    recommendation = LLMRecommendation.query.filter_by(
        id=recommendation_id,
        user_id=current_user.id,
    ).first()

    if recommendation is None:
        return jsonify({"success": False, "error": "Recommendation not found."}), 404

    try:
        db.session.delete(recommendation)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/myprofile", methods=['GET', 'POST'])
@login_required
def myprofile():
    friend_search = request.values.get('friend_search', '').strip()

    if request.method == 'POST' and request.form.get('form_type') == 'add_friend':
        friend_username = request.form.get('friend_username', '').strip()
        friend = User.query.filter_by(username=friend_username).first()
        if not friend:
            flash("Please choose a friend to add.")
        elif friend.id == current_user.id:
            flash("You cannot send a friend request to yourself.")
        elif find_friendship_between(current_user.id, friend.id):
            flash("A friend request or friendship already exists with this user.")
        else:
            db.session.add(Friendship(
                requester_id=current_user.id,
                receiver_id=friend.id,
                status="pending"
            ))
            db.session.commit()
            flash(f"Friend request sent to {friend.name or friend.username}.")
        return redirect(url_for('myprofile', friend_search=friend_search))

    if request.method == 'POST' and request.form.get('form_type') in {"accept_friend", "decline_friend"}:
        friendship_id = request.form.get('friendship_id')
        friendship = Friendship.query.filter_by(
            id=friendship_id,
            receiver_id=current_user.id,
            status="pending"
        ).first()

        if not friendship:
            flash("Friend request could not be found.")
        elif request.form.get('form_type') == "accept_friend":
            friendship.status = "accepted"
            db.session.commit()
            flash(f"You are now friends with {friendship.requester.name or friendship.requester.username}.")
        else:
            friendship.status = "declined"
            db.session.commit()
            flash(f"Friend request from {friendship.requester.name or friendship.requester.username} declined.")
        return redirect(url_for('myprofile', friend_search=friend_search))

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

    incoming_requests = (
        Friendship.query
        .filter_by(receiver_id=current_user.id, status="pending")
        .order_by(Friendship.created_at.desc())
        .all()
    )
    outgoing_requests = (
        Friendship.query
        .filter_by(requester_id=current_user.id, status="pending")
        .order_by(Friendship.created_at.desc())
        .all()
    )
    accepted_friendships = (
        Friendship.query
        .filter(
            or_(
                Friendship.requester_id == current_user.id,
                Friendship.receiver_id == current_user.id
            ),
            Friendship.status == "accepted"
        )
        .order_by(Friendship.updated_at.desc())
        .all()
    )
    accepted_friends = [
        item.receiver if item.requester_id == current_user.id else item.requester
        for item in accepted_friendships
    ]
    suggested_friends = get_friend_suggestions(current_user.id)

    app_friends = []
    if friend_search:
        app_friends = search_available_friends(current_user.id, friend_search)

    return render_template(
        "myprofile.html",
        title="My Profile",
        user=current_user,
        latest_login_at=latest_login_at,
        bmi=bmi,
        bmi_category=bmi_category,
        bmi_quote=bmi_quote,
        fitness_points=fitness_points,
        app_friends=app_friends,
        friend_search=friend_search,
        incoming_requests=incoming_requests,
        outgoing_requests=outgoing_requests,
        accepted_friends=accepted_friends,
        suggested_friends=suggested_friends
    )


@app.route("/friends/search")
@login_required
def search_friends():
    friend_search = request.args.get("q", "").strip()
    users = search_available_friends(current_user.id, friend_search)
    return jsonify({
        "results": [
            {
                "username": user.username,
                "name": user.name or user.username,
                "goal": user.goal or "Fitness journey in progress",
                "initial": (user.name or user.username)[:1].upper()
            }
            for user in users
        ]
    })


@app.route("/profile/<int:user_id>")
@login_required
def friend_profile(user_id):
    friend = db.session.get(User, user_id)
    if not friend:
        flash("Profile could not be found.")
        return redirect(url_for("myprofile"))

    if friend.id != current_user.id and not users_are_friends(current_user.id, friend.id):
        flash("You can view this profile after the friend request is accepted.")
        return redirect(url_for("myprofile"))

    bmi = None
    bmi_category = None
    bmi_quote = "This user has not added height and weight yet."
    fitness_points = get_bmi_fitness_points(None)
    current_recommendation = (
        LLMRecommendation.query
        .filter_by(user_id=friend.id, is_current=True)
        .first()
    )
    if friend.height_cm and friend.weight_kg:
        try:
            bmi, bmi_category, bmi_quote = calculate_bmi_result(friend.height_cm, friend.weight_kg)
            fitness_points = get_bmi_fitness_points(bmi_category)
        except ValueError:
            pass

    latest_workout = get_latest_workout_summary(friend.id)
    latest_nutrition = get_latest_nutrition_summary(friend.id)

    return render_template(
        "friend_profile.html",
        title=f"{friend.name or friend.username} Profile",
        friend=friend,
        bmi=bmi,
        bmi_category=bmi_category,
        bmi_quote=bmi_quote,
        fitness_points=fitness_points,
        latest_workout=latest_workout,
        latest_nutrition=latest_nutrition,
        hide_app_nav=True,
        current_recommendation=current_recommendation
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
