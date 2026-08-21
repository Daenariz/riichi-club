from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    request,
    session,
    current_app,
    abort,
)
from app.forms import (
    LoginForm,
    EditProfileForm,
    EventForm,
    BlogForm,
    TournamentRegistrationForm,
    TournamentForm,
)
from flask_login import login_user, current_user, logout_user, login_required
import sqlalchemy as sa
from app import db
from app.models import User, Post, BlogPost, Tournament, Registration
from flask_babel import _
from urllib.parse import urlsplit
from datetime import datetime, timezone
from functools import wraps

home_bp = Blueprint("home", __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


@home_bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@home_bp.route("/")
@home_bp.route("/index")
def index():
    query = sa.select(Post).order_by(Post.timestamp.desc())
    posts = db.session.scalars(query).all()
    query = sa.select(BlogPost).order_by(BlogPost.timestamp.desc())
    latest_news = db.session.scalar(query)

    return render_template(
        "index.html", title="Home Page", posts=posts, latest_news=latest_news
    )


@home_bp.route("/set_language/<lang>")
def set_language(lang):
    session["lang"] = lang
    return redirect(request.referrer or url_for("home.index"))


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
            flash(_("Invalid username or password"))
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
            location_type=form.location_type.data,
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
        form.event_type.data = post.event_type
        form.description.data = post.body
        form.date.data = post.timestamp.date()
        form.time.data = post.timestamp.time()

    return render_template("create_event.html", title="Edit Event", form=form)


@home_bp.route("/delete_event/<int:id>", methods=["POST"])
@login_required
def delete_event(id):
    post = db.session.get(Post, id)
    if post.author != current_user:
        flash(_("You cannot delete this event."))
        return redirect(url_for("home.index"))

    db.session.delete(post)
    db.session.commit()
    flash(_("Event has been deleted."))
    return redirect(url_for("home.user", username=current_user.username))


@home_bp.route("/blog")
def blog():
    page = request.args.get("page", 1, type=int)
    query = sa.select(BlogPost).order_by(BlogPost.timestamp.desc())
    pagination = db.paginate(
        query, page=page, per_page=current_app.config["POSTS_PER_PAGE"], error_out=False
    )
    posts = pagination.items
    return render_template(
        "blog.html", title="Blog", posts=posts, pagination=pagination
    )


@home_bp.route("/blog/<int:id>")
def view_blog(id):
    post = db.session.get(BlogPost, id)
    if post is None:
        abort(404)
    return render_template("view_blog.html", post=post, title=post.title)


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
        flash(_("Blog post deleted successfully."))
    else:
        flash(_("You cannot delete this post."))
    return redirect(url_for("home.user", username=current_user.username))


@home_bp.route("/edit_profile/<username>", methods=["GET", "POST"])
@login_required
def edit_profile(username):
    if current_user.username != username:
        flash(_("You can only edit your own profile."))
        return redirect(url_for("home.index"))
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_("Your changes have been saved."))
        return redirect(url_for("home.user", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", form=form)


@home_bp.route("/edit_blog/<int:id>", methods=["GET", "POST"])
@login_required
def edit_blog(id):
    blog_post = db.session.get(BlogPost, id)
    form = BlogForm()

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


# --- Tournament Routes (Public) ---


@home_bp.route("/turnier")
def tournament_list():
    active = db.session.scalar(
        sa.select(Tournament).where(Tournament.is_active == True).limit(1)
    )
    if active:
        return redirect(url_for("home.tournament_detail", id=active.id))
    return render_template("tournament.html", tournament=None)


@home_bp.route("/turnier/<int:id>")
def tournament_detail(id):
    tournament = db.session.get(Tournament, id)
    if tournament is None:
        abort(404)
    form = TournamentRegistrationForm()

    registrations = db.session.scalars(
        sa.select(Registration)
        .where(
            Registration.tournament_id == id,
            Registration.is_confirmed == True,
        )
        .order_by(Registration.created_at.asc())
    ).all()

    main_list = registrations[: tournament.max_players]
    wait_list = registrations[tournament.max_players :]

    return render_template(
        "tournament.html",
        tournament=tournament,
        form=form,
        main_list=main_list,
        wait_list=wait_list,
    )


@home_bp.route("/turnier/<int:id>/anmelden", methods=["POST"])
def tournament_register(id):
    tournament = db.session.get(Tournament, id)
    if tournament is None:
        abort(404)
    form = TournamentRegistrationForm()
    if form.validate_on_submit():
        existing = db.session.scalar(
            sa.select(Registration).where(
                Registration.tournament_id == id,
                Registration.email == form.email.data,
            )
        )
        if existing:
            flash(_("You are already registered for this tournament."))
            return redirect(url_for("home.tournament_detail", id=id))

        reg = Registration(
            tournament_id=id,
            ingame_name=form.ingame_name.data,
            club_name=form.club_name.data or None,
            email=form.email.data,
        )
        db.session.add(reg)
        db.session.commit()
        return redirect(url_for("home.tournament_thanks", id=id))
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text}: {error}")
    return redirect(url_for("home.tournament_detail", id=id))


@home_bp.route("/turnier/<int:id>/anmelden/danke")
def tournament_thanks(id):
    tournament = db.session.get(Tournament, id)
    if tournament is None:
        abort(404)
    return render_template("tournament_thanks.html", tournament=tournament)


@home_bp.route("/turnier/<int:id>/teilnehmer")
def tournament_participants(id):
    tournament = db.session.get(Tournament, id)
    if tournament is None:
        abort(404)

    registrations = db.session.scalars(
        sa.select(Registration)
        .where(
            Registration.tournament_id == id,
            Registration.is_confirmed == True,
        )
        .order_by(Registration.created_at.asc())
    ).all()

    main_list = registrations[: tournament.max_players]
    wait_list = registrations[tournament.max_players :]

    return render_template(
        "participants.html",
        tournament=tournament,
        main_list=main_list,
        wait_list=wait_list,
    )


# --- Admin Routes ---


@home_bp.route("/admin")
@admin_required
def admin():
    tournaments = db.session.scalars(
        sa.select(Tournament).order_by(Tournament.created_at.desc())
    ).all()
    return render_template("admin.html", tournaments=tournaments)


@home_bp.route("/admin/turnier/neu", methods=["GET", "POST"])
@admin_required
def admin_tournament_create():
    form = TournamentForm()
    if form.validate_on_submit():
        tournament = Tournament(
            title=form.title.data,
            description=form.description.data,
            max_players=form.max_players.data,
            is_active=form.is_active.data,
        )
        db.session.add(tournament)
        db.session.commit()
        flash(_("Tournament created."))
        return redirect(url_for("home.admin"))
    return render_template(
        "admin_tournament_form.html", form=form, title=_("Create Tournament")
    )


@home_bp.route("/admin/turnier/<int:id>", methods=["GET", "POST"])
@admin_required
def admin_tournament_edit(id):
    tournament = db.session.get(Tournament, id)
    if tournament is None:
        abort(404)
    form = TournamentForm()
    if form.validate_on_submit():
        tournament.title = form.title.data
        tournament.description = form.description.data
        tournament.max_players = form.max_players.data
        tournament.is_active = form.is_active.data
        db.session.commit()
        flash(_("Tournament updated."))
        return redirect(url_for("home.admin"))
    elif request.method == "GET":
        form.title.data = tournament.title
        form.description.data = tournament.description
        form.max_players.data = tournament.max_players
        form.is_active.data = tournament.is_active
    return render_template(
        "admin_tournament_form.html",
        form=form,
        title=_("Edit Tournament"),
        tournament=tournament,
    )


@home_bp.route("/admin/turnier/<int:id>/loeschen", methods=["POST"])
@admin_required
def admin_tournament_delete(id):
    tournament = db.session.get(Tournament, id)
    if tournament is None:
        abort(404)
    db.session.execute(sa.delete(Registration).where(Registration.tournament_id == id))
    db.session.delete(tournament)
    db.session.commit()
    flash(_("Tournament deleted."))
    return redirect(url_for("home.admin"))


@home_bp.route("/admin/turnier/<int:id>/anmeldungen")
@admin_required
def admin_registrations(id):
    tournament = db.session.get(Tournament, id)
    if tournament is None:
        abort(404)

    registrations = db.session.scalars(
        sa.select(Registration)
        .where(Registration.tournament_id == id)
        .order_by(Registration.created_at.asc())
    ).all()

    return render_template(
        "admin_registrations.html",
        tournament=tournament,
        registrations=registrations,
    )


@home_bp.route("/admin/anmeldung/<int:id>/confirm", methods=["POST"])
@admin_required
def admin_registration_confirm(id):
    reg = db.session.get(Registration, id)
    if reg is None:
        abort(404)
    reg.is_confirmed = not reg.is_confirmed
    db.session.commit()
    status = _("confirmed") if reg.is_confirmed else _("pending")
    flash(_("Registration status changed to %(status)s.", status=status))
    return redirect(
        url_for("home.admin_registrations", id=reg.tournament_id)
    )


@home_bp.route("/admin/anmeldung/<int:id>/loeschen", methods=["POST"])
@admin_required
def admin_registration_delete(id):
    reg = db.session.get(Registration, id)
    if reg is None:
        abort(404)
    tid = reg.tournament_id
    db.session.delete(reg)
    db.session.commit()
    flash(_("Registration deleted."))
    return redirect(url_for("home.admin_registrations", id=tid))