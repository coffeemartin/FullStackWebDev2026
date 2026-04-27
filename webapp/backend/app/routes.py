from datetime import datetime
from app import app, db
from flask import render_template, flash, redirect, url_for, session, request
from app.forms import LoginForm, ExerciseLogForm
from app.models import User, Exercise, ExerciseLog, LoginEvent

@app.route("/", methods=['GET', 'POST']) 
@app.route("/login", methods=['GET', 'POST'])  # Allow both GET and POST requests for the login route
def login():  # create a login route, use form validation, flash messages, and redirect to myprofile page on successful login
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        session['username'] = form.username.data
        return redirect(url_for('myprofile'))
    return render_template('login.html', title='Sign In', form=form)


@app.route("/nutrition")
def nutrition():
    return render_template('nutrition.html', title='Nutrition')


DUMMY_USER_ID = 1   # TODO: replace with real auth once login is wired up


@app.route("/exercise", methods=['GET', 'POST'])
def exercise():
    user = db.session.get(User, DUMMY_USER_ID)
    if not user:
        return ("No user with id=1 in database. "
                "Run `python seed.py` from webapp/backend first."), 500

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
        # Leave BMI / recommendation None so the existing 'locked' UI shows.
        bmi_value=None,
        exercise_level=None,
        recommendation=None,
    )

@app.route("/AI")
def AI():
    return render_template('AI.html', title='AI')


@app.route("/myprofile")
def myprofile():
    username = session.get('username', 'Guest')
    last_workout = session.get('last_workout')
    bmi_value = session.get('bmi_value')
    exercise_level = session.get('exercise_level')
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
    return render_template(
        'myprofile.html',
        title='My Profile',
        username=username,
        posts=posts,
        last_workout=last_workout,
        bmi_value=bmi_value,
        exercise_level=exercise_level,
    )