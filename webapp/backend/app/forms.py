from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

# Define the LoginForm class using Flask-WTF. This form will be used for user login, containing fields for username, password, a remember me checkbox, and a submit button. 
# Each field has appropriate validators to ensure that the required data is provided when the form is submitted.

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')