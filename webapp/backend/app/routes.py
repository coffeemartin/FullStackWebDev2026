from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app import app, db
from flask import render_template, flash, redirect, url_for, session, request
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


@app.route("/nutrition")
@login_required
def nutrition():
    nutrition_logs = (
        NutritionLog.query.filter_by(user_id=current_user.id)
        .join(Food)
        .order_by(NutritionLog.log_date.desc(), NutritionLog.id.desc())
        .all()
    )
    return render_template(
        'nutrition.html',
        title='Nutrition',
        nutrition_logs=nutrition_logs,
    )


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
