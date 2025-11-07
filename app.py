from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy

# Create the Flask application and the API
app = Flask(__name__)
api = Api(app)

# Configure our database. This tells the app to create a database file named 'books.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
db = SQLAlchemy(app)

# This class defines the structure of our 'books' table in the database
class BookModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))

    # This is a helper function to easily convert a book object to a dictionary format
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre
        }
    
# --- Part 1: Input Validation ---
# This parser will check the data sent when creating a book. Title and author are required.
post_parser = reqparse.RequestParser()
post_parser.add_argument('title', type=str, required=True, help='Title cannot be blank')
post_parser.add_argument('author', type=str, required=True, help='Author cannot be blank')
post_parser.add_argument('genre', type=str, default="")

# This parser is for updating. The fields are optional.
patch_parser = reqparse.RequestParser()
patch_parser.add_argument('title', type=str)
patch_parser.add_argument('author', type=str)
patch_parser.add_argument('genre', type=str)


# --- Part 2: API Resources (The actual endpoints) ---

# This resource handles requests for the entire list of books
# Corresponds to the URL: /books
class BookList(Resource):
    def get(self):
        """Get a list of all books."""
        books = BookModel.query.all()
        return {'books': [book.to_dict() for book in books]}, 200

    def post(self):
        """Create a new book."""
        args = post_parser.parse_args()
        book = BookModel(
            title=args['title'],
            author=args['author'],
            genre=args['genre']
        )
        db.session.add(book)
        db.session.commit()
        return book.to_dict(), 201

# This resource handles requests for a single, specific book
# Corresponds to the URL: /books/<id>
class Book(Resource):
    def patch(self, book_id):
        """Update an existing book."""
        book = BookModel.query.get_or_404(book_id) # get_or_404 is a shortcut to get the book or return a 404 error
        args = patch_parser.parse_args()

        # Update fields only if they are provided in the request
        if args['title']:
            book.title = args['title']
        if args['author']:
            book.author = args['author']
        if args['genre'] is not None: # Check for None to allow setting an empty string
            book.genre = args['genre']

        db.session.commit()
        return book.to_dict(), 200

    def delete(self, book_id):
        """Delete a book."""
        book = BookModel.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return {'message': 'Book deleted successfully'}, 200


# --- Part 3: Add the Resources to the API ---
api.add_resource(BookList, '/books')
api.add_resource(Book, '/books/<int:book_id>')


# --- Part 4: Run the Application ---
if __name__ == '__main__':
    app.run(debug=True)