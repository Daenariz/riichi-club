from flask import Blueprint, render_template, flash, redirect, url_for, request
# from app import app
from ..forms import LoginForm
from flask_login import login_user, current_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User
from urllib.parse import urlsplit

home_bp = Blueprint("home", __name__)

@home_bp.route('/')
@home_bp.route('/index')
@login_required
def index():
    # user = {'username': 'Miguel'}
    posts = [
            {
                'author': {'username': 'John'},
                'body': 'Beautiful day in Portland!'
                },
            {
                'author': {'username': 'Susan'},
                'body': 'The Avengers movie was super cool!'
                }
            ]
    return render_template('index.html', title='Home Page', posts=posts)

@home_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('home.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@home_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home.index'))
