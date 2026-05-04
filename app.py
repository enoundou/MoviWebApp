import json
from dotenv import load_dotenv
import os

import requests
from flask import Flask, request, redirect, url_for, flash, render_template
from sqlalchemy.exc import SQLAlchemyError

from data_manager import DataManager
from models import db, Movie, User

# ---------------------------
# App configuration
# ---------------------------

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

load_dotenv()

API_KEY = os.getenv("OMDB_API_KEY")
SECRET_KEY = os.getenv("OMDB_SECRET_KEY")

# Database configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'instance/movies.db')}"
app.config['SECRET_KEY'] = SECRET_KEY

# Initialize database
db.init_app(app)

# Data manager instance (handles CRUD logic)
data_manager = DataManager()


# ---------------------------
# External API (OMDb)
# ---------------------------

def api_search_movie(title, year):
    """
    Fetch movie data from OMDb API.
    Returns JSON data or None if something fails.
    """
    url = "http://www.omdbapi.com/"

    params = {
        "apikey": API_KEY,
        "t": title
    }

    if year:
        params["y"] = year

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()

        data = response.json()
        if data.get("Response") == "False":
            return None

        return data

    except requests.exceptions.Timeout:
        print("OMDb API timeout.")
        return None

    except requests.exceptions.ConnectionError:
        print("Could not connect to OMDb API.")
        return None

    except requests.exceptions.HTTPError as e:
        print(f"OMDb API HTTP error: {e}")
        return None

    except requests.exceptions.RequestException as e:
        print(f"OMDb API request error: {e}")
        return None

    except json.JSONDecodeError:
        print("OMDb API returned invalid JSON.")
        return None


# ---------------------------
# Routes
# ---------------------------

@app.route('/', methods=['GET'])
def index():
    """
    Homepage: display all users
    """
    try:
        users = data_manager.get_users()
        return render_template("index.html", users=users)

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error in index: {e}")
        return render_template("500.html"), 500


@app.route('/users', methods=['POST'])
def add_user():
    """
    add a user to the database
    :return: index.html
    """
    try:
        name = request.form.get('name')
        if not name:
            flash(f"User name is required")
            return redirect(url_for('index'))

        data_manager.create_user(name)
        flash(f"User '{name}' created successfully")
        return redirect(url_for('index'))

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error while adding user: {e}")
        return render_template("500.html"), 500


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_movies(user_id):
    """
     Display all movies for a specific user
    :param user_id:  id
    :return: url
    """
    try:
        user = db.session.get(User, user_id)

        if not user:
            flash(f"User with id {user_id} does not exist")
            return redirect(url_for('index'))

        movies = data_manager.get_movies(user_id)
        return render_template("movies.html", user=user, movies=movies)

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error while getting movies: {e}")
        return render_template("500.html"), 500


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie(user_id):
    """
    Add a movie for a user
    :param user_id: user id
    :return: url
    """
    try:
        user = db.session.get(User, user_id)

        if not user:
            flash(f"User with id {user_id} does not exist")
            return redirect(url_for('index'))

        title_movie = request.form.get('title', '').strip()
        year = request.form.get('year', '').strip()

        if not title_movie:
            flash(f"Movie title is required")
            return redirect(url_for('get_movies', user_id=user_id))

        data = api_search_movie(title_movie, year)
        if data:
            movie = Movie(
                title=title_movie,
                year=int(data.get("Year", 0)[:4]) if data.get("Year") else 0,
                director=data.get('Director', 'Unknown'),
                poster_url=data.get('Poster', ''),
                user_id=user_id
            )
        else:
            movie = Movie(
                title=title_movie,
                year=int(year) if year else 0,
                director="Unknown",
                poster_url="",
                user_id=user_id
            )

        data_manager.add_movie(movie)
        flash(f"Movie '{title_movie}' added successfully")
        return redirect(url_for('get_movies', user_id=user_id))

    except ValueError:
        flash("Year must be a valid number")
        return redirect(url_for('get_movies', user_id=user_id))

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error while adding movie: {e}")
        return render_template("500.html"), 500


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update', methods=['POST'])
def update_movie(user_id, movie_id):
    """
    update the title of a movie
    :param user_id: user id
    :param movie_id: movie id
    :return: url
    """
    try:
        movie = data_manager.get_movie(movie_id)

        if not movie or movie.user_id != user_id:
            flash(f"Movie {movie_id} does not exist")
            return redirect(url_for('get_movies', user_id=user_id))

        title_movie = request.form.get('title', '').strip()
        if not title_movie:
            flash(f"Movie title is required")
            return redirect(url_for('get_movies', user_id=user_id))

        data_manager.update_movie(movie_id, title_movie)
        flash("Movie updated successfully")

        return redirect(url_for('get_movies', user_id=user_id))

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error while updating movie: {e}")
        return render_template("500.html"), 500


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete', methods=['POST'])
def delete_movie(user_id, movie_id):
    """
    delete a movie
    :param user_id: user id
    :param movie_id: movie id
    :return: url
    """
    try:
        movie = data_manager.get_movie(movie_id)
        print(movie)
        if not movie or movie.user_id != user_id:
            flash(f"Movie with id {movie_id} does not exist")
            return redirect(url_for('get_movies', user_id=user_id))

        movie_title = movie.title
        data_manager.delete_movie(movie_id)

        flash(f"Movie '{movie_title}' deleted successfully")
        return redirect(url_for('get_movies', user_id=user_id))

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Database error while deleting movie: {e}")
        return render_template("500.html"), 500


# ---------------------------
# Error Handlers
# ---------------------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ---------------------------
# Run application
# ---------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=False)
