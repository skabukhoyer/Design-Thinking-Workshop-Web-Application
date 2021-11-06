#
# File containing main server code
#
#

# Dependencies
from flask import Flask, render_template, request, redirect, url_for

user_database = [
    {
        "username": "nithish",
        "password": "password"
    }
]

# Initialise app
app = Flask(__name__)
# Initialise config variables
app.config['logged_in'] = False

# Define home route
@app.route("/")
def home():
    # Display home if user is logged in, else redirect to login page
    if app.config['logged_in']:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

# Define login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Validate the request if post request, else display login page
    if request.method == 'POST':
        flag = False
        print(request.form['username'], request.form['password'])
        for item in user_database:
            if request.form['username'] == item['username'] and request.form['password'] == item['password']:
                flag = True
                break
        if flag:
            app.config['logged_in'] = True
            return redirect(url_for('home'))
        else:
            # return log_the_user_in(request.form['username'])
            error = 'Invalid username/password'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html', error=None)
