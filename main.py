from flask import Flask, session, render_template, url_for, request, redirect, flash, jsonify
from datetime import timedelta
import requests
from models import *
from sqlalchemy import or_, func, cast

app = Flask(__name__)
app.secret_key = "Needs_to_change"

app.permanent_session_lifetime = timedelta(hours=3)
app.config["SQLALCHEMY_DATABASE_URI"] = 'postgres://jcvwmqhjhvpyvf:6341f6696618f90b07a0f08cd3d73738b6ce4a4f837bd89a9e6bb6532ad19ad7@ec2-52-72-221-20.compute-1.amazonaws.com:5432/dd95sk0modea7s'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db = SQLAlchemy(app)

db.init_app(app)

def check_pass(value):
    count1, count2 = False, False
    # generators need fixing!!!
    # count1 = bool(True if x in '1234567890' else False for x in value)
    for x in value:
        if x in '1234567890':
            count1 = True
    print('count1:', count1)
    # count2 = bool(x.casefold() in 'abcdefghijklmnopqrstuvwxyz' for x in value)
    for x in value:
        if x in 'abcdefghijklmnopqrstuvwxyz':
            count2 = True
    print('count2:', count2)
    return all([count1, count2])

def email_avail(email):
    if User.query.filter(User.email == email).all():
        return False
    return True

def user_avail(username):
    if User.query.filter(User.username == username).all():
        return False
    return True

def name_grab(email):
    name = email.split("@")[0].capitalize()
    lst = [x for x in name if x.casefold() not in "1234567890"]
    name = ''.join(lst)
    for char in '_./-,':
        name = name.replace(char, ' ')
    return name

@app.route('/register', methods=["GET", "POST"])
def register():
    global info
    if request.method == "GET":
        return render_template('register.html')
    if not email_avail(request.form.get('email')):
        return render_template("register.html", email_avail='<br><span style="color: red;">Email not available</span>')
    if not user_avail(request.form.get('email')):
        return render_template("register.html", user_avail='<br><span style="color: red;">Username not available</span>')
    if not check_pass(request.form.get('password')):
        return render_template("register.html", pass_avail='<br><span style="color: red;">Password invalid: Needs at least 6 characters and one number</span>')
    name = request.form.get('name')
    email = request.form.get('email')
    last_name = request.form.get('last_name')
    birth_date = request.form.get('birth_date')
    username = request.form.get('username')
    password = request.form.get('password')
    user = User(email=email, username=username, password=password, birth_date=birth_date, name=name, last_name=last_name)
    print("data written successfully!")
    db.session.add(user)
    db.session.commit()
    return render_template('login.html')

@app.route("/")
def home():
    name = ''
    if 'user' in session:
        name = session['user']
    return render_template('home.html', name=name)

@app.route("/login", methods=["POST", "GET"])
def login():
    if not 'user' in session:
        if request.method == "POST":
            username = request.form.get('username')
            print(username)
            if not user_avail(username):
                user_details = User.query.filter(User.username == username).first()
                password = user_details.password
                if request.form.get('password') == password:
                    session["user"] = username
                    return render_template('home.html', name=username)
                flash('Wrong password!', category='error')
                return redirect(url_for('login'))
            flash('No such user!', category='error')
            return redirect(url_for('login'))
        else:
            return render_template('login.html')
    else:
        return render_template('home.html', message=f'You are already logged in as {session["user"]}')

@app.route('/search', methods=["GET", "POST"])
def search():
    if request.method == "GET":
        if 'user' not in session:
            return render_template('login.html')
        else:
            return render_template('search.html')
    else:
        print('line 109')
        search = request.form.get('search')
        print(search)
        # matches = db.execute("SELECT * FROM books WHERE isbn LIKE '%:search%' OR title LIKE '%:search%'"
        #                      " OR autor LIKE '%:search%' OR year LIKE '%:search%'", {'search': search}).fetchall()
        # matches = Books.query.filter(or_(Books.isbn.like(f'%{search}%'), Books.title.like(f'%{search}%'),
        #                                  Books.author.like(f'%{search}%'), Books.year.like(f'%{search}%'))).all()
        search = search.casefold()
        int_search = 123
        try:
            int_search = int(search)
        except:
            pass
        matches = Books.query.filter(or_(func.lower(Books.title).like(f'%{search}%'),
                                         func.lower(Books.author).like(f'%{search}%'),
                                         func.lower(Books.isbn).like(f'%{search}%'),
                                         cast(Books.year, db.String).like(f'%{search}%')))
        print('search successful')
        for m in matches:
            print(m.title)
        if matches:
            print(type(matches))
            return render_template('search.html', matches=matches)
        return render_template('search.html', message="Nothing found!")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/book/<string:ls>', methods=['POST', 'GET'])
def book(ls):
    lst = ls.split('|')
    creds = {'isbn': lst[0], 'title': lst[1], 'author': lst[2], 'year': lst[3]}
    print(creds)
    book = Books.query.get(lst[0])
    reviews = book.reviews
    if request.method == 'GET':
        print('get method')
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "JBimoce3BGsKgO2HrNUcQ", "isbns": creds['isbn']})
        res = res.json()['books'][0]
        creds['ratings_count'] = res['ratings_count']
        creds['average_rating'] = res['average_rating']
        return render_template("book.html", info=creds, reviews=reviews)
    else:
        print(reviews)
        for review in reviews:
            if review.username == session['user']:
                return "You cannot post on the same book twice!"
        print('post method...')
        title = request.form.get('title')
        text = request.form.get('text')
        if title and text:
            db.create_all()
            review = Reviews(username=session['user'], title=title, text=text, isbn=lst[0])
            db.session.add(review)
            db.session.commit()
        else:
            return render_template('book.html', info=creds, message="Must include title and content!")
        return render_template('book.html', info=creds, message="Review sent!", reviews=reviews)

@app.route('/api/<isbn>')
def api(isbn):
    book = Books.query.get(isbn)
    print(book)
    review_count = len(book.reviews)
    # add score to json
    print(book.title)
    return jsonify(title=book.title, author=book.author, year=book.year, isbn=book.isbn, review_count=review_count)

if __name__ == '__main__':
    app.run(debug=True)
