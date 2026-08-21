from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from . import db
from flask_login import UserMixin
from app import login
from hashlib import md5


class Tournament(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140))
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(2000))
    max_players: so.Mapped[int] = so.mapped_column(default=8)
    is_active: so.Mapped[bool] = so.mapped_column(default=True)
    created_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    registrations: so.WriteOnlyMapped["Registration"] = so.relationship(
        back_populates="tournament", passive_deletes=True
    )

    def __repr__(self):
        return f"<Tournament {self.title}>"


class Registration(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    tournament_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey("tournament.id"), index=True
    )
    ingame_name: so.Mapped[str] = so.mapped_column(sa.String(64))
    club_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    email: so.Mapped[str] = so.mapped_column(sa.String(120))
    is_confirmed: so.Mapped[bool] = so.mapped_column(default=False)
    created_at: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )

    tournament: so.Mapped[Tournament] = so.relationship(back_populates="registrations")

    def __repr__(self):
        return f"<Registration {self.ingame_name}>"


class Event(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(100))
    location: so.Mapped[str] = so.mapped_column(sa.String(100))
    event_time: so.Mapped[datetime] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def __repr__(self):
        return f"<Event {self.title}>"


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts: so.WriteOnlyMapped["Post"] = so.relationship(back_populates="author")
    blog_posts: so.WriteOnlyMapped["BlogPost"] = so.relationship(
        back_populates="author"
    )
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    is_admin: so.Mapped[bool] = so.mapped_column(default=False)

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return f"https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}"


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(2000))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    event_type: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    location_type: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    author: so.Mapped[User] = so.relationship(back_populates="posts")


class BlogPost(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140))
    body: so.Mapped[str] = so.mapped_column(sa.String(2000))
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"), index=True)

    author: so.Mapped["User"] = so.relationship(back_populates="blog_posts")


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))