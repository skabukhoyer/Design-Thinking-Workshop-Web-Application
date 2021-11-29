from flask import Flask, render_template, session, request, redirect, url_for, flash, send_file

from flask_sqlalchemy import SQLAlchemy

from flask_socketio import SocketIO, send

from time import localtime, strftime

from io import BytesIO

from base64 import b64encode

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:SSD2021!lab3b@localhost/ssdpro'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SECRET_KEY'] = 'secret'
app.config["SESSION_TYPE"] = 'filesystem'

db = SQLAlchemy(app)

socketio = SocketIO(app)



""" Creating a class for each table"""

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique = True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(80), nullable=False)  #Participant/Host/Stakeholder
    name = db.Column(db.String(80), nullable=False)


class MemberTeam(db.Model):
    username = db.Column(db.String(80), unique = True, nullable=False)
    tid = db.Column(db.Integer, nullable=False)
    uid = db.Column(db.Integer, nullable=False, primary_key=True)

    def __init__(self, username, uid, tid):
        self.username = username
        self.uid = uid
        self.tid = tid


class Team(db.Model):
    tid = db.Column(db.Integer, primary_key=True)

    teamname = db.Column(db.String(80), nullable=False)
    problem = db.Column(db.String(80), nullable=False)

    mid1 = db.Column(db.Integer, nullable=True)
    mid2 = db.Column(db.Integer, nullable=True)
    
    mid3 = db.Column(db.Integer, nullable=True)
    mid4 = db.Column(db.Integer, nullable=True)
    mid5 = db.Column(db.Integer, nullable=True)
    
    activestage = db.Column(db.String(80), default="Empathize" , nullable=False)


    def __init__(self, teamname, problem, mid1, mid2, activestage, mid3=None, mid4=None, mid5=None):
        self.problem = problem
        self.teamname = teamname

        self.mid1 = mid1
        self.mid2 = mid2
        
        self.mid3 = mid3
        self.mid4 = mid4
        self.mid5 = mid5

        self.activestage = activestage


class Empathize(db.Model):
    eid = db.Column(db.Integer, primary_key=True)
    tid = db.Column(db.Integer, nullable =False)
    uid = db.Column(db.Integer, nullable=False, unique=True)
    content = db.Column(db.String(500), nullable=False)


    def __init__(self, tid, uid, content):
        self.tid = tid
        self.uid = uid
        self.content = content


class Other(db.Model):
    tid = db.Column(db.Integer, primary_key=True)

    define = db.Column(db.String(500), nullable=False)
    ideate = db.Column(db.String(500), nullable=True)
    prototype = db.Column(db.LargeBinary, nullable=True)
    
    def __init__(self, tid, define):
        self.tid = tid
        self.define = define


class Chat(db.Model):
    cid = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500), nullable=False)
    uid = db.Column(db.Integer, nullable=False)
    tid = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(20), nullable=False)

    def __init__(self, content, uid, tid, date):
        self.content = content
        self.uid = uid
        self.tid = tid
        self.date = date

"""
@socketio.on('message')
def handleMessage(msg):
    content = msg
    uid = session['user']

    u = User.query.get(uid)

    if( (u.role == "host") or (u.role == "stakeholder")):
        pass

    else:
        #teamid
        tid = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()
        tid = tid.tid
        
        date = strftime('%d %b %H:%M', localtime())

        c = Chat(content, uid, tid, date)
        
        db.session.add(c)
        db.session.commit()
 
    send(msg, broadcast=True)
"""


# custom event chat
@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):

    uname = str(json['user_name']).strip()
    content = json['message'].strip()
    
    u = User.query.filter_by(username = uname).first()

    uid = u.uid

    if( (u.role == "host") or (u.role == "stakeholder")):
        tid = int(json['teamid'].strip())
        
        date = strftime('%d %b %H:%M', localtime())
        
        c = Chat(content, uid, tid, date)

        db.session.add(c)
        db.session.commit()

    else:
        #teamid
        tid = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()
        tid = tid.tid
        
        date = strftime('%d %b %H:%M', localtime())

        c = Chat(content, uid, tid, date)
        
        db.session.add(c)
        db.session.commit()

    socketio.emit('my response', json, callback=messageReceived)


def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')


@app.route('/signup', methods = ['POST'])
def signup():
    """Function to handle requests to /signup route."""
    if(request.method=='POST'):
        data = request.form
        
        username = data['username']
        password = data['password']
        role = data['role']
        name = data['name']

        check_user = User.query.filter_by(username=username).first()

        if(check_user is not None):
            flash('User already exists', 'info')
            return redirect(url_for('login'))

        else:
            user = User(username=username, password=password, role=role, name=name)
            db.session.add(user)
            db.session.commit()

            flash('User registered successfully', 'success')
            return redirect(url_for('login'))


@app.route('/', methods = ['POST', 'GET'])
def login():
    """Function to handle requests to /signin route."""
    if(request.method=='GET'):
        return render_template('login.html')

    if(request.method=='POST'):
        data = request.form

        username = data['username']
        password = data['password']
        
        check_user = User.query.filter_by(username=username).first()

        if(check_user is not None):
            if(check_user.password == password):
                session['user'] = check_user.uid

                if (check_user.role == "host"):
                    flash('Successfully logged in as Host', 'success')
                    return redirect(url_for('teams'))

                elif (check_user.role == "stakeholder"):
                    flash('Successfully logged in as Stakeholder', 'success')
                    return redirect(url_for('stakeholder'))

                else:
                    flash('Successfully logged in as Participant', 'success')
                    return redirect(url_for('home'))
            
            else:
                flash('Invalid credentials', 'error')
                return redirect(url_for('login'))
        
        else:
            flash('User does not exist', 'info')
            return redirect(url_for('login'))


@app.route('/signout', methods=['GET'])
def logout():
    session.pop('user', None)
    flash("You have successfully logged out", "success")
    return render_template("logout.html")


@app.route('/team', methods=['GET', 'POST'])
def team():
    uid = session['user']

    #teamid
    number = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()
    number = number.tid

    teaminfo = Team.query.filter_by(tid = number).first()

    messages = Chat.query.filter_by(tid=number).all()
    
    empathizecontent = Empathize.query.filter_by(tid = number).order_by(Empathize.eid.desc()).all()
    othercontent = Other.query.filter_by(tid = number).first()
    
    username = dict()
    specialuser = User.query.filter((User.role=="stakeholder") | (User.role=="host"))
    for i in specialuser:
        username[i.uid] = i.name
    
    if (teaminfo.mid1 is not None):
        username[teaminfo.mid1] = User.query.filter_by(uid = teaminfo.mid1).first().name

    if (teaminfo.mid2 is not None):
        username[teaminfo.mid2] = User.query.filter_by(uid = teaminfo.mid2).first().name

    if (teaminfo.mid3 is not None):
        username[teaminfo.mid3] = User.query.filter_by(uid = teaminfo.mid3).first().name
    
    if (teaminfo.mid4 is not None):
        username[teaminfo.mid4] = User.query.filter_by(uid = teaminfo.mid4).first().name
    
    if (teaminfo.mid5 is not None):
        username[teaminfo.mid5] = User.query.filter_by(uid = teaminfo.mid5).first().name


    o = Other.query.filter_by(tid = number).first()

    if ( (o is not None) and (o.prototype is not None) ):
        image = b64encode(o.prototype).decode("utf-8")

    else:
        image = ""

    currentusername = User.query.filter_by(uid = uid).first().name

    return render_template("team.html", messages = messages, empathizecontent = empathizecontent,
                           othercontent = othercontent, username = username, 
                           teaminfo = teaminfo, obj=o, image=image,
                           currentusername = currentusername)


@app.route('/empathizestage', methods=['GET', 'POST'])
def empathizestage():
    if request.method == "POST":
        
        empathizecontent = request.form["empathizedata"]
        uid = session['user']
        
        #teamid
        tid = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()
        tid = tid.tid

        e = Empathize(tid, uid, empathizecontent)

        db.session.add(e)
        db.session.commit()

        t = Team.query.filter_by(tid = tid).first()

        numberofmembers = 0

        if(t.mid1 is not None):
            numberofmembers += 1

        if(t.mid2 is not None):
            numberofmembers += 1

        if(t.mid3 is not None):
            numberofmembers += 1

        if(t.mid4 is not None):
            numberofmembers += 1

        if(t.mid5 is not None):
            numberofmembers += 1


        l = Empathize.query.filter_by(tid = tid).all()
        completedmembers = len(l)


        if(completedmembers == numberofmembers):
            t.activestage = "Define"
            db.session.commit()
        
        flash("Empathize Stage data updated successfully", "success")
        return redirect(url_for("team"))


    else:
        uid = session['user']
        alreadydone = Empathize.query.filter_by(uid = uid).first()

        if (alreadydone is not None):
            flash("You have already completed this stage. Please wait for your teammates.", "info")
            return redirect(url_for("team"))

        return render_template("empathize.html")


@app.route('/definestage', methods=['GET', 'POST'])
def definestage():
    if request.method == "POST":
        definecontent = request.form["definedata"]

        uid = session['user']
        #teamid
        tid = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()
        tid = tid.tid

        e = Other(tid, definecontent)

        db.session.add(e)
        db.session.commit()

        t = Team.query.filter_by(tid = tid).first()
        t.activestage = "Ideate"
        db.session.commit()
        
        flash("Define Stage data updated successfully", "success")
        return redirect(url_for("team"))

    else:
        uid = session['user']

        #teamid
        number = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()
        number = number.tid

        teaminfo = Team.query.filter_by(tid = number).first()

        username = dict()
        specialuser = User.query.filter((User.role=="stakeholder") | (User.role=="host"))
        
        for i in specialuser:
            username[i.uid] = i.name
        
        if (teaminfo.mid1 is not None):
            username[teaminfo.mid1] = User.query.filter_by(uid = teaminfo.mid1).first().name

        if (teaminfo.mid2 is not None):
            username[teaminfo.mid2] = User.query.filter_by(uid = teaminfo.mid2).first().name

        if (teaminfo.mid3 is not None):
            username[teaminfo.mid3] = User.query.filter_by(uid = teaminfo.mid3).first().name
        
        if (teaminfo.mid4 is not None):
            username[teaminfo.mid4] = User.query.filter_by(uid = teaminfo.mid4).first().name
        
        if (teaminfo.mid5 is not None):
            username[teaminfo.mid5] = User.query.filter_by(uid = teaminfo.mid5).first().name

        currentusername = User.query.filter_by(uid = uid).first().name

        messages = Chat.query.filter_by(tid=number).all()

        return render_template("define.html", messages = messages,
                                username = username,
                                currentusername = currentusername)


@app.route('/ideatestage', methods=['GET', 'POST'])
def ideatestage():
    if request.method == "POST":
        ideatecontent = request.form["ideatedata"]
        
        uid = session['user']
        
        #teamid
        tid = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()
        tid = tid.tid
        
        e = Other.query.filter_by(tid = tid).first()
        e.ideate = ideatecontent

        db.session.commit()


        t = Team.query.filter_by(tid = tid).first()
        t.activestage = "Prototype"
        db.session.commit()
        
        flash("Ideate Stage data updated successfully", "success")
        return redirect(url_for("team"))

    else:
        uid = session['user']

        #teamid
        number = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()
        number = number.tid

        teaminfo = Team.query.filter_by(tid = number).first()

        username = dict()
        specialuser = User.query.filter((User.role=="stakeholder") | (User.role=="host"))
        for i in specialuser:
            username[i.uid] = i.name
        
        if (teaminfo.mid1 is not None):
            username[teaminfo.mid1] = User.query.filter_by(uid = teaminfo.mid1).first().name

        if (teaminfo.mid2 is not None):
            username[teaminfo.mid2] = User.query.filter_by(uid = teaminfo.mid2).first().name

        if (teaminfo.mid3 is not None):
            username[teaminfo.mid3] = User.query.filter_by(uid = teaminfo.mid3).first().name
        
        if (teaminfo.mid4 is not None):
            username[teaminfo.mid4] = User.query.filter_by(uid = teaminfo.mid4).first().name
        
        if (teaminfo.mid5 is not None):
            username[teaminfo.mid5] = User.query.filter_by(uid = teaminfo.mid5).first().name

        messages = Chat.query.filter_by(tid=number).all()

        currentusername = User.query.filter_by(uid = uid).first().name

        return render_template("ideate.html", messages=messages, 
                                username = username,
                                currentusername = currentusername)


#return send_file(BytesIO(o.prototype), attachment_filename="wireframe.pdf", as_attachment =True)


@app.route('/prototypestage', methods=['GET', 'POST'])
def prototypestage():
    if request.method == "POST":
        file = request.files['inputFile']

        uid = session['user']

        #teamid
        tid = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()
        teamnum = tid.tid

        o = Other.query.filter_by(tid = teamnum).first()
        o.prototype = file.read()
        db.session.commit()


        t = Team.query.filter_by(tid = teamnum).first()
        t.activestage = "Test"
        db.session.commit()
        
        flash("Wireframe file uploaded successfully","success")
        return redirect(url_for("team"))


    else:
        uid = session['user']

        #teamid
        number = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()
        number = number.tid

        teaminfo = Team.query.filter_by(tid = number).first()

        username = dict()
        specialuser = User.query.filter((User.role=="stakeholder") | (User.role=="host"))
        for i in specialuser:
            username[i.uid] = i.name

        if (teaminfo.mid1 is not None):
            username[teaminfo.mid1] = User.query.filter_by(uid = teaminfo.mid1).first().name

        if (teaminfo.mid2 is not None):
            username[teaminfo.mid2] = User.query.filter_by(uid = teaminfo.mid2).first().name

        if (teaminfo.mid3 is not None):
            username[teaminfo.mid3] = User.query.filter_by(uid = teaminfo.mid3).first().name
        
        if (teaminfo.mid4 is not None):
            username[teaminfo.mid4] = User.query.filter_by(uid = teaminfo.mid4).first().name
        
        if (teaminfo.mid5 is not None):
            username[teaminfo.mid5] = User.query.filter_by(uid = teaminfo.mid5).first().name

        currentusername = User.query.filter_by(uid = uid).first().name

        messages = Chat.query.filter_by(tid=number).all()

        return render_template("prototype.html", messages=messages, 
                                username = username,
                                currentusername = currentusername)


@app.route('/teststage', methods=['GET', 'POST'])
def teststage():
    uid = session['user']

    #teamid
    number = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()
    number = number.tid

    messages = Chat.query.filter_by(tid=number).all()
    
    empathizecontent = Empathize.query.filter_by(tid = number).order_by(Empathize.eid.desc()).all()
    othercontent = Other.query.filter_by(tid = number).first()
    
    teaminfo = Team.query.filter_by(tid = number).first()

    username = dict()
    specialuser = User.query.filter((User.role=="stakeholder") | (User.role=="host"))
    for i in specialuser:
        username[i.uid] = i.name

    if (teaminfo.mid1 is not None):
        username[teaminfo.mid1] = User.query.filter_by(uid = teaminfo.mid1).first().name

    if (teaminfo.mid2 is not None):
        username[teaminfo.mid2] = User.query.filter_by(uid = teaminfo.mid2).first().name

    if (teaminfo.mid3 is not None):
        username[teaminfo.mid3] = User.query.filter_by(uid = teaminfo.mid3).first().name
    
    if (teaminfo.mid4 is not None):
        username[teaminfo.mid4] = User.query.filter_by(uid = teaminfo.mid4).first().name
    
    if (teaminfo.mid5 is not None):
        username[teaminfo.mid5] = User.query.filter_by(uid = teaminfo.mid5).first().name


    o = Other.query.filter_by(tid = number).first()

    if ( (o is not None) and (o.prototype is not None) ):
        image = b64encode(o.prototype).decode("utf-8")

    else:
        image = ""

    return render_template("test.html", messages = messages, 
                           empathizecontent = empathizecontent, 
                           othercontent = othercontent, username = username, 
                           teaminfo = teaminfo, number = number, obj=o, image=image)
    



@app.route('/home', methods=['GET'])
def home():
    uid = session['user']

    #teamid
    number = Team.query.filter( (Team.mid1==uid) | (Team.mid2==uid) | (Team.mid3==uid) | (Team.mid4==uid) | (Team.mid5==uid) ).first()

    if (number is not None):
        flash("You have been assigned a team", "success")
        return redirect(url_for("team"))

    else:
        return render_template("home.html")


@app.route("/teams")
def teams():
    g_teams = Team.query.all()
    teams = []
    for team in g_teams:
        teams.append({'tid': team.tid , 'tname': team.teamname, 'activestage': team.activestage})

    g_participants = User.query.all()
    participants = []
    for participant in g_participants:
        if participant.role == "participant":
            #participants.append({'username': participant.username , 'email': participant.email})
            participants.append({'username': participant.username})
    return render_template('teams.html', teams=teams, participants=participants)


@app.route("/add_team", methods=['POST'])
def add_team():
    team_name = request.form['team_name']
    problem = request.form['problem']

    print("Team name: ", team_name)
    team = Team(team_name, problem, None, None, "Empathize", None, None, None)
    db.session.add(team)
    db.session.commit()

    flash ("Team created successfully", "success")
    return redirect(url_for('teams'))


@app.route("/members/<tid>", methods=['GET'])
def members(tid):
    team = Team.query.get(tid)
    member = []
    activestage = team.activestage
    if team.mid1 != None:
        user = User.query.get(team.mid1)
        member.append({"uid":user.uid, "uname":user.username, "name":user.name})
    if team.mid2 != None:
        user = User.query.get(team.mid2)
        member.append({"uid":user.uid, "uname":user.username, "name":user.name})
    if team.mid3 != None:
        user = User.query.get(team.mid3)
        member.append({"uid":user.uid, "uname":user.username, "name":user.name})
    if team.mid4 != None:
        user = User.query.get(team.mid4)
        member.append({"uid":user.uid, "uname":user.username, "name":user.name})
    if team.mid5 != None:
        user = User.query.get(team.mid5)
        member.append({"uid":user.uid, "uname":user.username, "name":user.name})

    g_participants = User.query.all()
    participants = []
    for participant in g_participants:
        if participant.role == "participant":
            #participants.append({'username': participant.username , 'email': participant.email})
            participants.append({'username': participant.username})

    return render_template('members.html', member=member, participants=participants, team_name = team.teamname, tid = tid, activestage = activestage, problem = team.problem)


@app.route("/add_member/<tid>", methods=['POST'])
def add_member(tid):
    username = request.form['username']

    if (username == ""):
        flash ("Username cannot be empty", "error")
        return redirect(url_for('members',tid = tid))

    rel = MemberTeam.query.all()

    team = Team.query.get(tid)

    user = User.query.filter_by(username=username).first()


    flag = 0
    for x in rel:
        if x.uid == user.uid:
            flag = 1
            break

    if flag == 0:
        if team.mid1 == None:
            team.mid1 = user.uid
        elif team.mid2 == None:
            team.mid2 = user.uid
        elif team.mid3 == None:
            team.mid3 = user.uid
        elif team.mid4 == None:
            team.mid4 = user.uid
        elif team.mid5 == None:
            team.mid5 = user.uid
        else:
            flash ("Team is already full", "info")
            return redirect(url_for('members',tid = tid))

        relation = MemberTeam(username, user.uid, tid)
        db.session.add(relation)
    
    else:
        flash ("User is already in a team!", "info")
        return redirect(url_for('members',tid = tid))

    db.session.commit()
    return redirect(url_for('members',tid = tid))


@app.route("/remove_user/<tid>/<uid>")
def remove_user(tid, uid):
    team = Team.query.get(tid)
    
    print(tid + " " + uid)
    if team.mid1 and int(team.mid1) == int(uid):
        team.mid1 = None
    elif team.mid2 and  int(team.mid2) == int(uid):
        team.mid2 = None
    elif team.mid3 and  int(team.mid3) == int(uid):
        team.mid3 = None
    elif team.mid4 and  int(team.mid4) == int(uid):
        team.mid4 = None
    elif team.mid5 and  int(team.mid5) == int(uid):
        team.mid5 = None
    print(team)
    MemberTeam.query.filter(MemberTeam.uid==uid).delete()
    db.session.commit()
    return redirect(url_for('members',tid = tid))


@app.route("/stakeholder", methods=['GET','POST'])
def stakeholder():
    if request.method == "GET":
        g_participants = User.query.all()
        participants = []
        for participant in g_participants:
            if participant.role == "participant":
                #participants.append({'username': participant.username , 'email': participant.email})
                participants.append({'username': participant.username})

        messages = None
        teaminfo = None
        return render_template('stakeholder.html', participants=participants,
                                messages = messages, teaminfo = teaminfo)
    
    if request.method == "POST":
        uid = session['user']

        
        teamname = request.form["team_name"]
        
        number = Team.query.filter_by(teamname = teamname).first().tid
       
        messages = Chat.query.filter_by(tid = number).all()
        teaminfo = Team.query.filter_by(tid = number).first()

        username = dict()

        specialuser = User.query.filter((User.role=="stakeholder") | (User.role=="host"))
        for i in specialuser:
            username[i.uid] = i.name
        
        if (teaminfo.mid1 is not None):
            username[teaminfo.mid1] = User.query.filter_by(uid = teaminfo.mid1).first().name

        if (teaminfo.mid2 is not None):
            username[teaminfo.mid2] = User.query.filter_by(uid = teaminfo.mid2).first().name

        if (teaminfo.mid3 is not None):
            username[teaminfo.mid3] = User.query.filter_by(uid = teaminfo.mid3).first().name
        
        if (teaminfo.mid4 is not None):
            username[teaminfo.mid4] = User.query.filter_by(uid = teaminfo.mid4).first().name
        
        if (teaminfo.mid5 is not None):
            username[teaminfo.mid5] = User.query.filter_by(uid = teaminfo.mid5).first().name

        currentusername = User.query.filter_by(uid = uid).first().name

        g_participants = User.query.all()
        participants = []
        for participant in g_participants:
            if participant.role == "participant":
                #participants.append({'username': participant.username , 'email': participant.email})
                participants.append({'username': participant.username})

        return render_template('stakeholder.html', participants=participants,
                                messages = messages, username = username,
                                teaminfo = teaminfo, currentusername = currentusername)


@app.route("/host_inbox", methods=['GET','POST'])
def host_inbox():
    if request.method == "GET":
        g_participants = User.query.all()
        participants = []
        for participant in g_participants:
            if participant.role == "participant":
                #participants.append({'username': participant.username , 'email': participant.email})
                participants.append({'username': participant.username})

        messages = None
        teaminfo = None
        return render_template('host_inbox.html', participants=participants,
                                messages = messages, teaminfo = teaminfo)
    
    if request.method == "POST":
        uid = session['user']

        
        teamname = request.form["team_name"]
        
        number = Team.query.filter_by(teamname = teamname).first().tid
       
        messages = Chat.query.filter_by(tid = number).all()
        teaminfo = Team.query.filter_by(tid = number).first()

        username = dict()

        specialuser = User.query.filter((User.role=="stakeholder") | (User.role=="host"))
        for i in specialuser:
            username[i.uid] = i.name
        
        if (teaminfo.mid1 is not None):
            username[teaminfo.mid1] = User.query.filter_by(uid = teaminfo.mid1).first().name

        if (teaminfo.mid2 is not None):
            username[teaminfo.mid2] = User.query.filter_by(uid = teaminfo.mid2).first().name

        if (teaminfo.mid3 is not None):
            username[teaminfo.mid3] = User.query.filter_by(uid = teaminfo.mid3).first().name
        
        if (teaminfo.mid4 is not None):
            username[teaminfo.mid4] = User.query.filter_by(uid = teaminfo.mid4).first().name
        
        if (teaminfo.mid5 is not None):
            username[teaminfo.mid5] = User.query.filter_by(uid = teaminfo.mid5).first().name

        currentusername = User.query.filter_by(uid = uid).first().name

        g_participants = User.query.all()
        participants = []
        for participant in g_participants:
            if participant.role == "participant":
                #participants.append({'username': participant.username , 'email': participant.email})
                participants.append({'username': participant.username})

        return render_template('host_inbox.html', participants=participants,
                                messages = messages, username = username,
                                teaminfo = teaminfo, currentusername = currentusername)


if __name__ == '__main__':
    db.create_all()
    socketio.run(app, debug=True)