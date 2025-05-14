from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from datetime import datetime

# Date parser for release_date
def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("release_date must be in YYYY-MM-DD format")

# Initialize Flask app and configuration
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

# Define the Movie model
class MovieModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Float)
    release_date = db.Column(db.Date)

    def __repr__(self):
        return f"<Movie {self.title}>"

# Request parser for input validation
movie_args = reqparse.RequestParser()
movie_args.add_argument('title', type=str, required=True, help="Title cannot be blank")
movie_args.add_argument('description', type=str, required=False, default="")
movie_args.add_argument('rating', type=float, required=False, default=0.0)
movie_args.add_argument('release_date', type=parse_date, required=False)

# Define the fields to return in the response
movieFields = {
    'id': fields.Integer,
    'title': fields.String,
    'description': fields.String,
    'rating': fields.Float,
    'release_date': fields.String,
}

# Resource to handle GET all movies and POST new movie
class Movies(Resource):
    @marshal_with(movieFields)
    def get(self):
        movies = MovieModel.query.all()
        return movies

    @marshal_with(movieFields)
    def post(self):
        args = movie_args.parse_args()
        movie = MovieModel(
            title=args["title"],
            description=args.get("description", ""),
            rating=args.get("rating", 0.0),
            release_date=args.get("release_date")
        )
        db.session.add(movie)
        db.session.commit()
        return movie, 201

# Resource to handle GET a movie by its ID
class MovieById(Resource):
    @marshal_with(movieFields)
    def get(self, id):
        movie = MovieModel.query.get(id)
        if not movie:
            abort(404, message="Movie not found")
        return movie

# Register API resources
api.add_resource(Movies, '/api/movies')  # For GET all and POST
api.add_resource(MovieById, '/api/movies/<int:id>')  # For GET by ID

# Root route for a simple health check
@app.route('/')
def home():
    return 'API is running!'

# Ensure database is created before first request
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
