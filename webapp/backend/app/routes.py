from app import app
from flask import render_template, flash, redirect, url_for, session
from app.forms import LoginForm, ExerciseLogForm

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


@app.route("/exercise", methods=['GET', 'POST'])
def exercise():
    form = ExerciseLogForm()

    bmi_value = session.get('bmi_value')
    exercise_level = session.get('exercise_level')
    recommendation = None

    if bmi_value is not None and exercise_level:
        try:
            bmi_value = float(bmi_value)
            recommendation = get_exercise_plan(bmi_value, exercise_level)
        except (TypeError, ValueError):
            bmi_value = None
            recommendation = None

    if form.validate_on_submit():
        session['last_workout'] = {
            "exercise_name": form.exercise_name.data,
            "category": form.category.data,
            "workout_date": form.workout_date.data.strftime("%d %b %Y"),
            "duration_minutes": form.duration_minutes.data,
            "difficulty": form.difficulty.data,
            "sets": form.sets.data,
            "reps": form.reps.data,
            "weight_kg": float(form.weight_kg.data) if form.weight_kg.data is not None else None,
            "distance_km": float(form.distance_km.data) if form.distance_km.data is not None else None,
            "notes": form.notes.data,
            "is_public": form.is_public.data,
        }
        flash(f"Workout saved for {form.exercise_name.data}.")
        return redirect(url_for('myprofile'))

    return render_template(
        'exercise.html',
        title='Exercise',
        form=form,
        bmi_value=bmi_value,
        exercise_level=exercise_level,
        recommendation=recommendation,
    )

    return render_template('exercise.html', title='Exercise')


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