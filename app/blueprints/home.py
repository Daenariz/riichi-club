from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app, abort
from app.forms import LoginForm, EditProfileForm, EventForm, BlogForm
from flask_login import login_user, current_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User, Post, BlogPost
from urllib.parse import urlsplit
from datetime import datetime, timezone

home_bp = Blueprint("home", __name__)


@home_bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@home_bp.route("/")
@home_bp.route("/index")
# @login_required
def index():
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.session.scalars(query).all()
    query = sa.select(BlogPost).order_by(BlogPost.timestamp.desc())
    latest_news = db.session.scalar(query)

    return render_template(
        "index.html", title="Home Page", posts=posts, latest_news=latest_news
    )


@home_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("home.login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("home.index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@home_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home.index"))


@home_bp.route("/user/<username>")
@login_required
def user(username):
    user = db.session.scalar(sa.select(User).where(User.username == username))
    posts = db.session.scalars(user.posts.select()).all()
    blog_posts = db.session.scalars(
        db.select(BlogPost).where(BlogPost.user_id == user.id)
    ).all()

    return render_template("user.html", user=user, posts=posts, blog_posts=blog_posts)


@home_bp.route("/create_event", methods=["GET", "POST"])
@login_required
def create_event():
    form = EventForm()
    if form.validate_on_submit():
        combined_dt = datetime.combine(form.date.data, form.time.data)
        post = Post(
            body=form.description.data,
            author=current_user,
            timestamp=combined_dt,
            event_type=form.event_type.data,
            location_type=form.location_type.data,  # Diese Zeile hinzufügen!
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("home.index"))
    return render_template("create_event.html", title="Create Event", form=form)


@home_bp.route("/edit_event/<int:id>", methods=["GET", "POST"])
@login_required
def edit_event(id):
    post = db.session.get(Post, id)

    form = EventForm()
    if form.validate_on_submit():
        post.event_type = form.event_type.data
        post.location_type = form.location_type.data
        post.body = form.description.data
        post.timestamp = datetime.combine(form.date.data, form.time.data)
        db.session.commit()
        return redirect(url_for("home.user", username=current_user.username))

    elif request.method == "GET":
        # WICHTIG: Hier werden die alten Daten ins Formular geladen
        form.event_type.data = (
            post.event_type
        )  # Setzt das Dropdown auf den gespeicherten Wert
        form.description.data = post.body
        form.date.data = post.timestamp.date()
        form.time.data = post.timestamp.time()

    return render_template("create_event.html", title="Edit Event", form=form)


@home_bp.route("/delete_event/<int:id>", methods=["POST"])
@login_required
def delete_event(id):
    post = db.session.get(Post, id)
    if post.author != current_user:
        flash("You cannot delete this event.")
        return redirect(url_for("home.index"))

    db.session.delete(post)
    db.session.commit()
    flash("Event has been deleted.")
    return redirect(url_for("home.user", username=current_user.username))


@home_bp.route("/blog")
def blog():
    page = request.args.get("page", 1, type=int)
    query = sa.select(BlogPost).order_by(BlogPost.timestamp.desc())
    pagination = db.paginate(
        query, page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
    )
    posts = pagination.items
    return render_template("blog.html", title="Blog", posts=posts, pagination=pagination)


@home_bp.route('/blog/<int:id>')
def view_blog(id):
    post = db.session.get(BlogPost, id)
    if post is None:
        abort(404)
    return render_template('view_blog.html', post=post, title=post.title)


@home_bp.route("/create_blog", methods=["GET", "POST"])
@login_required
def create_blog():
    form = BlogForm()
    if form.validate_on_submit():
        post = BlogPost(
            title=form.title.data,
            body=form.body.data,
            timestamp=datetime.combine(form.date.data, datetime.min.time()),
            author=current_user,
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("home.index"))
    return render_template("create_blog.html", form=form)


@home_bp.route("/delete_blog/<int:id>", methods=["POST"])
@login_required
def delete_blog(id):
    blog_post = db.session.get(BlogPost, id)
    if blog_post and blog_post.author == current_user:
        db.session.delete(blog_post)
        db.session.commit()
        flash("Blog post deleted successfully.")
    else:
        flash("You cannot delete this post.")
    return redirect(url_for("home.user", username=current_user.username))


@home_bp.route("/edit_blog/<int:id>", methods=["GET", "POST"])
@login_required
def edit_blog(id):
    blog_post = db.session.get(BlogPost, id)
    form = BlogForm()  # Erst mal ein leeres Formular

    if form.validate_on_submit():
        blog_post.title = form.title.data
        blog_post.body = form.body.data
        blog_post.timestamp = datetime.combine(form.date.data, datetime.min.time())
        db.session.commit()
        return redirect(url_for("home.user", username=current_user.username))

    elif request.method == "GET":
        form.title.data = blog_post.title
        form.body.data = blog_post.body

    return render_template("edit_blog.html", form=form, title="Edit Blog")
