from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.String, nullable=True)


class Books(db.Model):
    __tablename__ = "books"
    isbn = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    author = db.Column(db.String)
    year = db.Column(db.Integer)
    reviews = db.relationship("Reviews", backref="books", lazy=True)


class Reviews(db.Model):
    __lablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String)
    title = db.Column(db.String)
    text = db.Column(db.String)
    isbn = db.Column(db.String, db.ForeignKey("books.isbn"), nullable=False)
