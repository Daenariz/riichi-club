from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

from wtforms import StringField, TextAreaField, SubmitField, DateField, TimeField
from wtforms.validators import DataRequired, Length

class EventForm(FlaskForm):
    title = StringField('Event Title', validators=[DataRequired(), Length(max=100)])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=500)])
    submit = SubmitField('Post Event')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About Me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')
