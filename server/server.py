#
# File containing main server code
#
#

# Dependencies
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_manager, login_user, logout_user, login_required, UserMixin

# Initialise app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://newuser:password@localhost/ssd_db'
app.config['SECRET_KEY'] = 'secretkey'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class Team(db.Model):
    id = db.Column(db.String(80), nullable=False, primary_key=True)
    problem_statement = db.Column(db.String(1000))
    member_1 = db.Column(db.Integer, nullable=False)
    member_2 = db.Column(db.Integer, nullable=False)
    member_3 = db.Column(db.Integer, nullable=True)
    member_4 = db.Column(db.Integer, nullable=True)
    member_5 = db.Column(db.Integer, nullable=True)
    stage = db.Column(db.String(80), default="empathize")

class Empathize(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    team_name = db.Column(db.String(80), nullable=False)
    member_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(1000), nullable=True)

class Stage(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    team_name = db.Column(db.String(80), nullable=False)
    define_content = db.Column(db.String(1000), nullable=True)
    ideate_content = db.Column(db.String(1000), nullable=True)
    prototype_content = db.Column(db.String(1000), nullable=True)

class Chat(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    content = db.Column(db.String(1000), nullable=True)
    user_id = db.Column(db.Integer, nullable=False)
    team_name = db.Column(db.String(80), nullable=False)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    # gender = db.Column(db.String(80), nullable=True)
    # dob = db.Column(db.String(80), nullable=True)
    # contact = db.Column(db.String(80), nullable=True)
    # about = db.Column(db.String(80), nullable=True)

# Signin/signup routes

@login_manager.user_loader
def load_user(user_id):
    """ Fetches from the database, the user with given user id.

    Keyword Arguments:
    user_id -- string/integer
    """
    return User.query.get(int(user_id))

@app.route('/signin', methods = ['POST', 'GET'])
def signin():
    """Function to handle requests to /signin route."""
    if(request.method=='GET'):
        return render_template('login.html')
    if(request.method=='POST'):
        data = request.form
        # print("signin: ", data)
        username = data['username']
        password = data['password']
        check_user = User.query.filter_by(username=username).first()
        if(check_user is not None):
            if(check_user.password == password):
                login_user(check_user)
                return render_template('home.html')
            else:
                error = 'Invalid credentials'
                return redirect(url_for('signin'))
        else:
            error = 'Invalid credentials'
            return redirect(url_for('signin'))

@app.route('/signout', methods=['GET'])
@login_required
def signout():
    """Function to handle requests to /signout route."""
    logout_user()
    return redirect(url_for('signin'))

@app.route('/signup', methods = ['POST'])
def signup():
    """Function to handle requests to /signup route."""
    if(request.method=='POST'):
        data = request.form
        # print("signup: ", data)
        username = data['username']
        password = data['password']
        role = data['role']
        # gender = data['gender']
        # dob = data['dob']
        # contact = data['contact']
        # about = data['about']
        check_user = User.query.filter_by(username=username).first()
        if(check_user is not None):
            # error = 'Cannot create new account'
            # return render_template('login.html', error=error)
            return 'User exists'
        else:
            user = User(username=username, password=password, role=role)
            db.session.add(user)
            db.session.commit()
            # print(user.username, user.password, user.role)
            return redirect(url_for('signin'))

# User routes

# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
#     username = db.Column(db.String(80), nullable=False)
#     password = db.Column(db.String(80), nullable=False)
#     role = db.Column(db.String(80), nullable=False)

@app.route("/create_user", methods=['POST'])
def create_user():
    if(request.method=='POST'):
        data = request.get_json()
        username = data['username']
        password = data['password']
        role = data['role']
        check_user = User.query.filter_by(username=username).first()
        if(check_user is not None):
            return 'User exists', 400
        else:
            user = User(username=username, password=password, role=role)
            db.session.add(user)
            db.session.commit()
            # print(user.username, user.password, user.role)
            return 'Created successfully'

@app.route("/read_user", methods=['POST'])
def read_user():
    if(request.method=='POST'):
        data = request.get_json()
        username = data['username']
        check_user = User.query.filter_by(username=username).first()
        if(check_user is not None):
            res = {}
            res["id"] = check_user.id
            res["username"] = check_user.username
            res["password"] = check_user.password
            res["role"] = check_user.role
            return jsonify(res)
        else:
            return 'User does not exist', 400

# Static routes

@app.route("/", methods=['GET'])
@login_required
def home():
    return render_template('home.html')

if(__name__ == '__main__'):
    app.run(port=8000,debug=True)
