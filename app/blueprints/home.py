from flask import Blueprint, render_template, flash, redirect, url_for, request
from app.forms import LoginForm, EditProfileForm, EventForm
from flask_login import login_user, current_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User, Post
from urllib.parse import urlsplit
from datetime import datetime, timezone

home_bp = Blueprint("home", __name__)

@home_bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@home_bp.route('/')
@home_bp.route('/index')
# @login_required
def index():
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.session.scalars(query).all()
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

@home_bp.route('/user/<username>')
@login_required
def user(username):
    user = db.session.scalar(sa.select(User).where(User.username == username))
    posts = db.session.scalars(user.posts.select()).all()
    return render_template('user.html', user=user, posts=posts)


@home_bp.route('/create_event', methods=['GET', 'POST'])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        # Kombiniere Datum und Zeit
        combined_dt = datetime.combine(form.date.data, form.time.data)
        
        # Erstelle ein Event (Post)
        # Wir nutzen den Titel und die Beschreibung im Body, oder passen dein Model an
        event_content = f"{form.title.data}: {form.description.data}"
        post = Post(body=event_content, author=current_user, timestamp=combined_dt)
        
        db.session.add(post)
        db.session.commit()
        flash('Event successfully created!')
        return redirect(url_for('home.index'))
    return render_template('create_event.html', title='Create Event', form=form)

@home_bp.route('/edit_event/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_event(id):
    post = db.session.get(Post, id)
    if post.author != current_user:
        flash('You cannot edit this event.')
        return redirect(url_for('home.index'))
    
    form = EventForm()
    if form.validate_on_submit():
        # Kombiniere Datum und Zeit aus dem Formular
        combined_dt = datetime.combine(form.date.data, form.time.data)
        
        post.body = f"{form.title.data}: {form.description.data}"
        post.timestamp = combined_dt
        
        db.session.commit()
        flash('Your event has been updated.')
        return redirect(url_for('home.user', username=current_user.username))
    
    elif request.method == 'GET':
        form.description.data = post.body
        form.date.data = post.timestamp.date()
        form.time.data = post.timestamp.time()
        form.title.data = "Event Title" 
        
    return render_template('create_event.html', title='Edit Event', form=form)

@home_bp.route('/delete_event/<int:id>', methods=['POST'])
@login_required
def delete_event(id):
    post = db.session.get(Post, id)
    if post.author != current_user:
        flash('You cannot delete this event.')
        return redirect(url_for('home.index'))
    
    db.session.delete(post)
    db.session.commit()
    flash('Event has been deleted.')
    return redirect(url_for('home.user', username=current_user.username))
