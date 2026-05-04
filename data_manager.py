from models import db, User, Movie


class DataManager:
    """
    Handles all database operations (CRUD).
    Exceptions are handled here to keep app.py clean.
    """

    def create_user(self, name):
        """
        Create and save a new user.
        """
        user = User(name=name)
        db.session.add(user)
        db.session.commit()
        return user

    def get_users(self):
        """
        Retrieve all users.
        """
        return User.query.all()

    def get_movies(self, user_id):
        """
        Get all movies for a specific user.
        """
        return Movie.query.filter_by(user_id=user_id).all()

    def get_movie(self, movie_id):
        """
        Get a single movie by ID.
        Returns None if not found.
        """
        return Movie.query.filter_by(id=movie_id).first()

    def add_movie(self, movie):
        """
        Add a new movie to the database.
        """
        db.session.add(movie)
        db.session.commit()
        return movie

    def update_movie(self, movie_id, new_title):
        """
        Update movie title.
        """
        movie = Movie.query.filter_by(id=movie_id).first()
        movie.title = new_title
        db.session.commit()
        return movie

    def delete_movie(self, movie_id):
        """
        Delete a movie by ID.
        """
        movie = Movie.query.filter_by(id=movie_id).first()
        db.session.delete(movie)
        db.session.commit()

        return movie
