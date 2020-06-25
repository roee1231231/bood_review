# import csv
# from models import *
# from flask import Flask
#
# app = Flask(__name__)
# app.secret_key = "Needs_to_change"
#
# app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://jcvwmqhjhvpyvf:6341f6696618f90b07a0f08cd3d73738b6ce4a4f837bd89a9e6bb6532ad19ad7@ec2-52-72-221-20.compute-1.amazonaws.com:5432/dd95sk0modea7s'
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
#
# # db = SQLAlchemy(app)
# db.init_app(app)
#
# with open('books.csv', 'r') as books:
#     csv_reader = csv.reader(books)
#     for count, row in enumerate(csv_reader):
#         if count > 0:
#             data = Books(isbn=row[0], title=row[1], author=row[2], year=row[3])
#             db.session.add(data)
#             print('commiting data')
#             db.session.commit()
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine("postgres://jcvwmqhjhvpyvf:6341f6696618f90b07a0f08cd3d73738b6ce4a4f837bd89a9e6bb6532ad19ad7@ec2-52-72-221-20.compute-1.amazonaws.com:5432/dd95sk0modea7s")
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    db.execute("CREATE TABLE IF NOT EXISTS books (isbn VARCHAR PRIMARY KEY, title VARCHAR, author VARCHAR, year INTEGER)")
    db.commit()
    for isbn, title, author, year in reader:
        print(isbn, title, author, year)
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()

if __name__ == "__main__":
    main()
