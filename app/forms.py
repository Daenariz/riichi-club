from flask_wtf import FlaskForm
from wtforms import (
    SelectField,
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    DateField,
    TimeField,
)
from wtforms.validators import DataRequired, Length


class EventForm(FlaskForm):
    # title = StringField('Event Title', validators=[DataRequired()])
    event_type = SelectField(
        "Event Type",
        choices=[
            ("workshop", "Einsteigerworkshop"),
            ("suzume", "Suzume Jong - Mahjong Schnupperabend"),
        ],
    )
    location_type = SelectField(
        "Location", choices=[("online", "Online"), ("lokal", "Lokal")]
    )
    date = DateField("Date", format="%Y-%m-%d", validators=[DataRequired()])
    time = TimeField("Time", validators=[DataRequired()])
    description = TextAreaField("Description", validators=[Length(max=2000)])
    submit = SubmitField("Event erstellen")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About Me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")


class BlogForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(min=1, max=140)])
    body = TextAreaField(
        "Content", validators=[DataRequired(), Length(min=1, max=2000)]
    )
    date = DateField("Date", format="%Y-%m-%d", validators=[DataRequired()])
    submit = SubmitField("Post")
