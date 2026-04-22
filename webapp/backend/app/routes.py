from app import app
from flask import render_template, flash, redirect, url_for, session
from app.forms import LoginForm

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