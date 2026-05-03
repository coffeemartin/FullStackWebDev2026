from datetime import date

from app import app, db
from flask import jsonify, render_template, flash, redirect, url_for, session, request
from app.forms import LoginForm
from app.models import Food, NutritionLog, User


@app.route("/", methods=['GET', 'POST']) 
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        session['username'] = form.username.data
        return redirect(url_for('myprofile'))
    return render_template('login.html', title='Sign In', form=form)


# Nutrion page route
@app.route("/nutrition")
def nutrition():
    user = User.query.first()
    initial_water = 0
    food_entries = []

    if user is not None:
        water_log = (
            NutritionLog.query
            .filter_by(user_id=user.id, log_date=date.today(), meal_type="Water")
            .order_by(NutritionLog.id.desc())
            .first()
        )
        if water_log and water_log.water_glasses:
            initial_water = water_log.water_glasses
        nutrition_logs = (
            NutritionLog.query
            .filter(NutritionLog.user_id == user.id)
            .filter(NutritionLog.log_date == date.today())
            .filter(NutritionLog.meal_type != "Water")
            .join(Food)
            .order_by(NutritionLog.id.asc())
            .all()
        )
        food_entries = [
            {
                "mealType": log.meal_type or "",
                "foodName": log.food.name,
                "quantity": log.quantity_g or 0,
                "calculatedCalories": round(((log.quantity_g or 0) / 100) * (log.food.calories_per_100g or 0)),
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
    )


@app.route("/nutrition/log", methods=["POST"])
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

    user = User.query.first()
    if user is None:
        return jsonify({"error": "Create a user before saving nutrition logs."}), 400

    nutrition_log = NutritionLog(
        user_id=user.id,
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
def save_water_log():
    data = request.get_json() or {}
    water_glasses = data.get("water_glasses")

    try:
        water_glasses = int(water_glasses)
    except (TypeError, ValueError):
        return jsonify({"error": "Water glasses must be a valid number."}), 400

    if water_glasses < 0:
        return jsonify({"error": "Water glasses cannot be negative."}), 400

    user = User.query.first()
    if user is None:
        return jsonify({"error": "Create a user before saving water intake."}), 400

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
        .filter_by(user_id=user.id, log_date=date.today(), meal_type="Water")
        .order_by(NutritionLog.id.desc())
        .first()
    )

    if water_log is None:
        water_log = NutritionLog(
            user_id=user.id,
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


@app.route("/exercise")
def exercise():
    return render_template('exercise.html', title='Exercise')


@app.route("/AI")
def AI():
    return render_template('AI.html', title='AI')


@app.route("/myprofile")
def myprofile():
    username = session.get('username', 'Guest')
    posts = [
        {
            'author': {'username': 'Franco'},
            'body': 'Whatever the mind of man can conceive and believe, it can achieve.'
        },
        {
            'author': {'username': 'Swathy'},
            'body': 'The only thing that overcomes hard luck is hard work.'
        },
        {
            'author': {'username': 'Faiz'},
            'body': 'Strive not to be a success, but rather to be of value.'
        },
        {
            'author': {'username': 'Ananya'},
            'body': 'Success is the good fortune that comes from aspiration, desperation, perspiration and inspiration.'
        }
    ]
    return render_template('myprofile.html', title='My Profile', username=username, posts=posts)


# ✅ YOUR NEW FEATURE
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
                quote = "You're doing well—let’s improve fitness step by step!"
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
