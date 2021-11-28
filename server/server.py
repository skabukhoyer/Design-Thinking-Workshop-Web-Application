#
# File containing main server code
#
#

# Dependencies
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, login_manager, login_user, logout_user, login_required, UserMixin

# Initialise app
app = Flask(__name__, static_url_path='', static_folder='static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://newuser:password@localhost/ssd_db'
app.config['SECRET_KEY'] = 'secretkey'

db = SQLAlchemy(app)
# login_manager = LoginManager()
# login_manager.init_app(app)

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

# class User(UserMixin, db.Model):
class User(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    # gender = db.Column(db.String(80), nullable=True)
    # dob = db.Column(db.String(80), nullable=True)
    # contact = db.Column(db.String(80), nullable=True)
    # about = db.Column(db.String(80), nullable=True)

# Signin/signup routes

# @login_manager.user_loader
# def load_user(user_id):
#     """ Fetches from the database, the user with given user id.
#
#     Keyword Arguments:
#     user_id -- string/integer
#     """
#     return User.query.get(int(user_id))

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
                print(check_user.name, ":::name", check_user.username)
                # login_user(check_user)
                return redirect(url_for('home'))
            else:
                error = 'Invalid credentials'
                return redirect(url_for('signin'))
        else:
            error = 'Invalid credentials'
            return redirect(url_for('signin'))

@app.route('/signout', methods=['GET'])
# @login_required
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
        name = data['name']
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
            user = User(username=username, password=password, role=role, name=name)
            print(user.name, ":::name")
            db.session.add(user)
            db.session.commit()
            # print(user.username, user.password, user.role)
            return redirect(url_for('signin'))

# User routes

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
            return 'Created user successfully'

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

@app.route("/get_all_user", methods=['POST'])
def get_all_user():
    if(request.method=='POST'):
        data = User.query.all()
        response = {}
        for item in data:
            response[ item.id ] = {
                "username": item.username,
                "password": item.password,
                "role": item.role
            }
        return response

# Team routes

@app.route("/create_team", methods=['POST'])
def create_team():
    if(request.method=='POST'):
        data = request.get_json()
        id = data["id"]
        problem_statement = data["problem_statement"]
        member_1 = data["member_1"]
        member_2 = data["member_2"]
        member_3 = data["member_3"]
        member_4 = data["member_4"]
        member_5 = data["member_5"]
        stage = data["stage"]
        check_team = Team.query.filter_by(id=id).first()
        if(check_team is not None):
            return 'Team exists', 400
        else:
            team = Team(id=id, problem_statement=problem_statement,
                member_1=member_1, member_2=member_2, member_3=member_3,
                member_4=member_4, member_5=member_5, stage=stage)
            db.session.add(team)
            db.session.commit()
            return 'Created team successfully'

@app.route("/read_team", methods=['POST'])
def read_team():
    if(request.method=='POST'):
        data = request.get_json()
        id = data['id']
        check_team = Team.query.filter_by(id=id).first()
        if(check_team is not None):
            res = {}
            res["id"] = check_team.id
            res["problem_statement"] = check_team.problem_statement
            res["member_1"] = check_team.member_1
            res["member_2"] = check_team.member_2
            res["member_3"] = check_team.member_3
            res["member_4"] = check_team.member_4
            res["member_5"] = check_team.member_5
            res["stage"] = check_team.stage
            return jsonify(res)
        else:
            return 'Team does not exist', 400

@app.route("/get_all_team", methods=['POST'])
def get_all_team():
    if(request.method=='POST'):
        data = Team.query.all()
        response = {}
        for item in data:
            response[ item.id ] = {
                "problem_statement": item.problem_statement,
                "member_1": item.member_1,
                "member_2": item.member_2,
                "member_3": item.member_3,
                "member_4": item.member_4,
                "member_5": item.member_5,
                "stage": item.stage
            }
        return response

@app.route("/update_team", methods=['POST'])
def update_team():
    if(request.method=='POST'):
        data = request.get_json()
        id = data["id"]
        check_team = Team.query.filter_by(id=id).first()
        if(check_team is not None):
            check_team.problem_statement = data["problem_statement"]
            check_team.member_1 = data["member_1"]
            check_team.member_2 = data["member_2"]
            check_team.member_3 = data["member_3"]
            check_team.member_4 = data["member_4"]
            check_team.member_5 = data["member_5"]
            check_team.stage = data["stage"]
            db.session.commit()
            return 'Updated team successfully'
        else:
            return 'Team does not exist', 400

@app.route("/delete_team", methods=['POST'])
def delete_team():
    if(request.method=='POST'):
        data = request.get_json()
        id = data["id"]
        check_team = Team.query.filter_by(id=id).first()
        if(check_team is not None):
            db.session.delete(check_team)
            db.session.commit()
            return 'Deleted team successfully'
        else:
            return 'Team does not exist', 400

# Chat routes

@app.route("/create_chat", methods=['POST'])
def create_chat():
    if(request.method=='POST'):
        data = request.get_json()
        content = data["content"]
        user_id = data["user_id"]
        team_name = data["team_name"]
        chat = Chat(content=content, user_id=user_id, team_name=team_name)
        db.session.add(chat)
        db.session.commit()
        return jsonify(chat.id)

@app.route("/read_chat", methods=['POST'])
def read_chat():
    if(request.method=='POST'):
        data = request.get_json()
        id = data['id']
        check_chat = Chat.query.filter_by(id=id).first()
        if(check_chat is not None):
            res = {}
            res["id"] = check_chat.id
            res["content"] = check_chat.content
            res["user_id"] = check_chat.user_id
            res["team_name"] = check_chat.team_name
            return jsonify(res)
        else:
            return 'Chat does not exist', 400

@app.route("/get_all_chat", methods=['POST'])
def get_all_chat():
    if(request.method=='POST'):
        data = Chat.query.all()
        response = {}
        for item in data:
            response[ item.id ] = {
                "content": item.content,
                "user_id": item.user_id,
                "team_name": item.team_name,
            }
        return response

@app.route("/update_chat", methods=['POST'])
def update_chat():
    if(request.method=='POST'):
        data = request.get_json()
        id = data["id"]
        check_chat = Chat.query.filter_by(id=id).first()
        if(check_chat is not None):
            check_chat.content = data["content"]
            check_chat.user_id = data["user_id"]
            check_chat.team_name = data["team_name"]
            db.session.commit()
            return 'Updated chat successfully'
        else:
            return 'Chat does not exist', 400

@app.route("/delete_chat", methods=['POST'])
def delete_chat():
    if(request.method=='POST'):
        data = request.get_json()
        id = data["id"]
        check_chat = Chat.query.filter_by(id=id).first()
        if(check_chat is not None):
            db.session.delete(check_chat)
            db.session.commit()
            return 'Deleted chat successfully'
        else:
            return 'Chat does not exist', 400

# Empathise routes

@app.route("/create_empathize", methods=['POST'])
def create_empathize():
    if(request.method=='POST'):
        data = request.get_json()
        team_name = data["team_name"]
        member_id = data["member_id"]
        content = data["content"]
        empathize = Empathize(content=content, member_id=member_id, team_name=team_name)
        db.session.add(empathize)
        db.session.commit()
        return jsonify(empathize.id)

@app.route("/read_empathize", methods=['POST'])
def read_empathize():
    if(request.method=='POST'):
        data = request.get_json()
        id = data['id']
        check_empathize = Empathize.query.filter_by(id=id).first()
        if(check_empathize is not None):
            res = {}
            res["id"] = check_empathize.id
            res["team_name"] = check_empathize.team_name
            res["member_id"] = check_empathize.member_id
            res["content"] = check_empathize.content
            return jsonify(res)
        else:
            return 'Empathize entry does not exist', 400

@app.route("/get_all_empathize", methods=['POST'])
def get_all_empathise():
    if(request.method=='POST'):
        data = Empathize.query.all()
        response = {}
        for item in data:
            response[ item.id ] = {
                "content": item.content,
                "member_id": item.member_id,
                "team_name": item.team_name
            }
        return response

@app.route("/update_empathize", methods=['POST'])
def update_empathize():
    if(request.method=='POST'):
        data = request.get_json()
        id = data["id"]
        check_empathize = Empathize.query.filter_by(id=id).first()
        if(check_empathize is not None):
            check_empathize.content = data["content"]
            check_empathize.member_id = data["member_id"]
            check_empathize.team_name = data["team_name"]
            db.session.commit()
            return 'Updated empathize entry successfully'
        else:
            return 'Empathize entry does not exist', 400

@app.route("/delete_empathize", methods=['POST'])
def delete_empathise():
    if(request.method=='POST'):
        data = request.get_json()
        id = data["id"]
        check_empathize = Empathize.query.filter_by(id=id).first()
        if(check_empathize is not None):
            db.session.delete(check_empathize)
            db.session.commit()
            return 'Deleted empathize entry successfully'
        else:
            return 'Empathize entry does not exist', 400

# Stage routes

# class Stage(db.Model):
#     id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
#     team_name = db.Column(db.String(80), nullable=False)
#     define_content = db.Column(db.String(1000), nullable=True)
#     ideate_content = db.Column(db.String(1000), nullable=True)
#     prototype_content = db.Column(db.String(1000), nullable=True)

@app.route("/create_stage", methods=['POST'])
def create_stage():
    if(request.method=='POST'):
        data = request.get_json()
        team_name = data["team_name"]
        define_content = data["define_content"]
        ideate_content = data["ideate_content"]
        prototype_content = data["prototype_content"]
        stage = Stage(team_name=team_name, define_content=define_content, ideate_content=ideate_content, prototype_content=prototype_content)
        db.session.add(stage)
        db.session.commit()
        return jsonify(stage.id)

@app.route("/read_stage", methods=['POST'])
def read_stage():
    if(request.method=='POST'):
        data = request.get_json()
        id = data['id']
        check_stage = Stage.query.filter_by(id=id).first()
        if(check_stage is not None):
            res = {}
            res["id"] = check_stage.id
            res["team_name"] = check_stage.team_name
            res["define_content"] = check_stage.define_content
            res["ideate_content"] = check_stage.ideate_content
            res["prototype_content"] = check_stage.prototype_content
            return jsonify(res)
        else:
            return 'Stage entry does not exist', 400

@app.route("/get_all_stage", methods=['POST'])
def get_all_stage():
    if(request.method=='POST'):
        data = Stage.query.all()
        response = {}
        for item in data:
            response[ item.id ] = {
                "team_name": item.team_name,
                "define_content": item.define_content,
                "ideate_content": item.ideate_content,
                "prototype_content": item.prototype_content
            }
        return response

@app.route("/update_stage", methods=['POST'])
def update_stage():
    if(request.method=='POST'):
        data = request.get_json()
        id = data["id"]
        check_stage = Stage.query.filter_by(id=id).first()
        if(check_stage is not None):
            check_stage.team_name = data["team_name"]
            check_stage.define_content = data["define_content"]
            check_stage.ideate_content = data["ideate_content"]
            check_stage.prototype_content = data["prototype_content"]
            db.session.commit()
            return 'Updated stage entry successfully'
        else:
            return 'Stage entry does not exist', 400

@app.route("/delete_stage", methods=['POST'])
def delete_stage():
    if(request.method=='POST'):
        data = request.get_json()
        id = data["id"]
        check_stage = Empathize.query.filter_by(id=id).first()
        if(check_stage is not None):
            db.session.delete(check_stage)
            db.session.commit()
            return 'Deleted stage entry successfully'
        else:
            return 'Stage entry does not exist', 400

# Static routes

@app.route("/", methods=['GET'])
# @login_required
def home():
    return render_template('home.html')

if(__name__ == '__main__'):
    db.create_all()
    app.run(port=8000,debug=True)
