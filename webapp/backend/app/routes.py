from app import app
from app import db
from flask import render_template, flash, redirect, url_for, session, request
from app.forms import LoginForm
from app.models import User
from sqlalchemy.exc import SQLAlchemyError


@app.route("/", methods=['GET', 'POST']) 
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    show_signup = False
    form_data = {}

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
            session['username'] = user.name or user.username
            flash("Profile created successfully.")
            return redirect(url_for('myprofile'))
        except ValueError as error:
            flash(str(error))
        except SQLAlchemyError:
            db.session.rollback()
            flash("Profile could not be saved right now. Please try again.")

    elif form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid login ID or password.")
        else:
            session['username'] = user.name or user.username
            return redirect(url_for('myprofile'))

    return render_template(
        'login.html',
        title='Sign In',
        form=form,
        form_data=form_data,
        show_signup=show_signup
    )


@app.route("/nutrition")
def nutrition():
    return render_template('nutrition.html', title='Nutrition')


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
