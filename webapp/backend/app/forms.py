from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    IntegerField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional

# Define the LoginForm class using Flask-WTF. This form will be used for user login, containing fields for username, password, a remember me checkbox, and a submit button. 
# Each field has appropriate validators to ensure that the required data is provided when the form is submitted.

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class ExerciseLogForm(FlaskForm):
    exercise_id = SelectField(
        'Exercise',
        coerce=int,
        validators=[DataRequired()],
    )
    workout_date = DateField(
        'Workout Date',
        format='%Y-%m-%d',
        default=date.today,
        validators=[DataRequired()],
    )
    duration_minutes = IntegerField(
        'Duration (minutes)',
        validators=[Optional(), NumberRange(min=1, max=300)],
    )
    sets = IntegerField('Sets', validators=[Optional(), NumberRange(min=1, max=20)])
    reps = IntegerField('Reps', validators=[Optional(), NumberRange(min=1, max=200)])
    weight_kg = DecimalField(
        'Weight Used (kg)',
        places=1,
        validators=[Optional(), NumberRange(min=0, max=500)],
    )
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=250)])
    submit = SubmitField('Save Workout')