from flask_sqlalchemy import SQLAlchemy

from typing import Any
db: Any = SQLAlchemy()


class User(db.Model):
    """
    User model - represents a user in the system.
    Each user can have multiple movies.
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # nullable=False → DB will raise an IntegrityError if name is missing
    name = db.Column(db.String, nullable=False)

    # Relationship to Movie
    # lazy='dynamic' → allows query operations (filter, count, etc.)
    movies = db.relationship('Movie', backref='user', lazy='dynamic')

    def __repr__(self):
        return f"User('{self.name}')"

    def __str__(self):
        return f"User('{self.name}')"


class Movie(db.Model):
    """
    Movie model - represents a movie linked to a user.
    """

    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Required field → can raise IntegrityError if missing
    title = db.Column(db.String, nullable=False)

    # Optional fields
    director = db.Column(db.String, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    poster_url = db.Column(db.String, nullable=True)

    # Foreign key → ensures movie belongs to a valid user
    # If invalid user_id is used → IntegrityError
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f"Movie('{self.title}({self.year})')"

    def __str__(self):
        return f"Movie('{self.title}({self.year})')"
