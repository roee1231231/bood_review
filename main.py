from flask import Flask, session, render_template, url_for, request, redirect, flash
from datetime import timedelta
from models import *

app = Flask(__name__)
app.secret_key = "Needs_to_change"

app.permanent_session_lifetime = timedelta(minutes=5)
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

# @app.route('/', methods=["POST", "GET"])
# def home():
#     if request.method == "POST":
#         if check_value(request.form['password']):
#             info['name'] = name_grab(request.form['email'])
#             info['email'] = request.form['email']
#             info['password'] = request.form['password']
#             session['user'] = info['name']
#         else:
#             flash("Password must contain a minimum of 6 characters and at least one number!", category='error')
#             return redirect(url_for('home'))
#     elif 'user' not in session:
#         return render_template("login.html")
#     return render_template("home.html", info=info)
#

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
    db.create_all()
