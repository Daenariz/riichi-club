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
    IntegerField,
)
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Regexp
from flask_babel import lazy_gettext as _l


class TournamentForm(FlaskForm):
    title = StringField(
        _l("Title"),
        validators=[DataRequired(_l("This field is required.")), Length(max=140)],
    )
    description = TextAreaField(_l("Description"), validators=[Length(max=2000)])
    max_players = IntegerField(
        _l("Max Players"),
        validators=[DataRequired(_l("This field is required.")), NumberRange(min=2)],
        default=8,
    )
    is_active = BooleanField(_l("Active"))
    submit = SubmitField(_l("Save"))


class TournamentRegistrationForm(FlaskForm):
    ingame_name = StringField(
        _l("Ingame Name"),
        validators=[DataRequired(_l("This field is required.")), Length(max=64)],
    )
    club_name = StringField(
        _l("Club Name (optional)"),
        validators=[Optional(), Length(max=100)],
    )
    email = StringField(
        _l("Email"),
        validators=[
            DataRequired(_l("This field is required.")),
            Regexp(r"^[^@]+@[^@]+\.[^@]+$", message=_l("Invalid email address.")),
            Length(max=120),
        ],
    )
    submit = SubmitField(_l("Register"))


class EventForm(FlaskForm):
    event_type = SelectField(
        _l("Event Type"),
        choices=[
            ("workshop", _l("Einsteigerworkshop")),
            ("suzume", _l("Suzume Jong - Mahjong Schnupperabend")),
        ],
    )
    location_type = SelectField(
        _l("Location"),
        choices=[("online", _l("Online")), ("lokal", _l("Lokal"))],
    )
    date = DateField(
        _l("Date"),
        format="%Y-%m-%d",
        validators=[DataRequired(_l("This field is required."))],
    )
    time = TimeField(
        _l("Time"), validators=[DataRequired(_l("This field is required."))]
    )
    description = TextAreaField(_l("Description"), validators=[Length(max=2000)])
    submit = SubmitField(_l("Event erstellen"))


class LoginForm(FlaskForm):
    username = StringField(
        _l("Username"), validators=[DataRequired(_l("This field is required."))]
    )
    password = PasswordField(
        _l("Password"), validators=[DataRequired(_l("This field is required."))]
    )
    remember_me = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l("Sign In"))


class EditProfileForm(FlaskForm):
    username = StringField(
        _l("Username"), validators=[DataRequired(_l("This field is required."))]
    )
    about_me = TextAreaField(_l("About Me"), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l("Submit"))


class BlogForm(FlaskForm):
    title = StringField(
        _l("Title"),
        validators=[
            DataRequired(_l("This field is required.")),
            Length(min=1, max=140),
        ],
    )
    body = TextAreaField(
        _l("Content"),
        validators=[
            DataRequired(_l("This field is required.")),
            Length(min=1, max=2000),
        ],
    )
    date = DateField(
        _l("Date"),
        format="%Y-%m-%d",
        validators=[DataRequired(_l("This field is required."))],
    )
    submit = SubmitField(_l("Post"))
