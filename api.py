from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with
from datetime import datetime

def parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("release_date must be in YYYY-MM-DD format")

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
api = Api(app)

# Movie Model Definition
class MovieModel(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   title = db.Column(db.String(80), nullable=False)
   description = db.Column(db.String(200), nullable=False)
   rating = db.Column(db.Float)
   release_date = db.Column(db.Date)
   
   def __repr__(self):
      return f"Movie {self.title}, Description {self.description}, Rating {self.rating}, Release_date {self.release_date}"

# Request Parser for Post
movie_args = reqparse.RequestParser()
movie_args.add_argument('title', type=str, required=True, help="Title can not be blank")
movie_args.add_argument('description', type=str)
movie_args.add_argument('rating', type=float)
movie_args.add_argument('release_date', type=parse_date, required=False)

# Serialization Fields
movieFields = {
   'id': fields.Integer,
   'title': fields.String,
   'description': fields.String,
   'rating': fields.Float,
   'release_date': fields.String,
}

# Movie Resource to handle GET by id
class MovieById(Resource):
    @marshal_with(movieFields)
    def get(self, id):
        movie = MovieModel.query.get(id)
        if not movie:
            return {'message': 'Movie not found'}, 404
        return movie

# Movie Resource to handle POST (Create movie)
class Movies(Resource):
    @marshal_with(movieFields)
    def post(self):
        args = movie_args.parse_args()
        movie = MovieModel(title=args["title"], description=args["description"],rating=args["rating"], release_date=args["release_date"])
        db.session.add(movie)
        db.session.commit()
        return movie, 201

# Registering the resources with different routes
api.add_resource(MovieById, '/api/movies/<int:id>')  # Route for GET by id
api.add_resource(Movies, '/api/movies')  # Route for POST (to create a movie)

@app.route('/')
def home():
    return '✅ Flask API is running!'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures DB is created before first request
    app.run(debug=True)
