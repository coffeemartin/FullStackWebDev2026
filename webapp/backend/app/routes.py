from datetime import timezone
from zoneinfo import ZoneInfo

from app import app,db
from flask import render_template, flash, redirect, url_for, session, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm
from app.models import ExerciseLog, Food, LoginEvent, NutritionLog, User


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


@app.route("/exercise")
@login_required
def exercise():
    exercise_logs = (
        ExerciseLog.query.filter_by(user_id=current_user.id)
        .join(ExerciseLog.exercise)
        .order_by(ExerciseLog.log_date.desc(), ExerciseLog.id.desc())
        .all()
    )
    return render_template(
        'exercise.html',
        title='Exercise',
        exercise_logs=exercise_logs,
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