import os

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology



# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure python standard library Library to use SQLite database
con = sqlite3.connect('school.db',check_same_thread=False)
db = con.cursor()

def listify (obj):
    """makes the output of the database SELECT as a list contains a dictionary"""
    keys = []
    lis = []
    for i, n in enumerate(db.description):
        keys.append(n[0])
    for item in obj:
        lis.append({keys[i]: item[i] for i in range(len(item))})
    return lis








# Application's Routes
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return render_template("index.html")









@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html",msg = "register_student")
    else:
        username = request.form.get("username")
        fullname = request.form.get("fullname")
        address = request.form.get("address")
        dob = request.form.get("date")
        nationality = request.form.get("nationality")
        Id = request.form.get("id")
        dept = request.form.get("department")
        password = request.form.get("password")
        confirmation = request.form.get("confirm")
        if fullname == "":
            return apology("Please Enter your Full name")
        if len(fullname) < 5:
            return apology("your name should be at least 5 characters long")
        if username == "":
            return apology("Please Enter your account")
        if len(username) < 5:
            return apology("your Account should be at least 5 characters long")
        users =  listify(db.execute("SELECT * FROM student WHERE username =:username", {"username":username}))
        if len(users) != 0:
            return apology('Email Already Exists!')
        if address == "":
            return apology("Please Enter your address")
        if dob == "":
            return apology("Please Enter your date of birth")
        if nationality == "":
            return apology("Please Choose your Nationality")
        if Id == "":
            return apology("Please Enter your national id or Passport Number")
        if dept == "":
            return apology("Please Choose Your Department")
        if password == "":
            return apology("Please Enter your Password")
        if len(password) < 8:
            return apology("Your Password Should Be At Least 8 Digits long")
        if confirmation == "":
            return apology("Please Re-Enter your password")
        if  confirmation != password:
            return apology("The Passwords Don't Match!")
        else:
            if nationality == 'egyptian':
                db.execute('INSERT INTO student (name,address,dateOfBirth,nationality,nationalId,department,username,password) VALUES(:name,:address,:dateOfBirth,:nationality,:nationalID,:department,:username,:password)',{"name":fullname,"address":address,"dateOfBirth":dob,"nationality":nationality,"nationalID":Id,"department":dept,"username":username,"password":generate_password_hash(password)} )
                con.commit()
            else:
                db.execute('INSERT INTO student (name,address,dateOfBirth,nationality,passport,department,username,password) VALUES(:name,:address,:dateOfBirth,:nationality,:passport,:department,:username,:password)',{"name":fullname,"address":address,"dateOfBirth":dob,"nationality":nationality,"passport":Id,"department":dept,"username":username,"password":generate_password_hash(password)} )
                con.commit()

            user_data_list =  listify(db.execute("SELECT sid, username FROM student WHERE username =:username", {"username":username}))

            # Remember which user has Reigsterd
            session["user_id"] = user_data_list[0]["sid"]
            session["user_username"] = user_data_list[0]["username"]

            #Redirect the user to home page
            return redirect("/login")





@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    # Forget any user_id
    session.clear()

    # gets executed when the user submit the form
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "" :
            return apology("must provide username")
        if password == "":
            return apology("must provide Password")


        # Query database for username
        ''' اسم الداتا بيز الي انت حاطه غبي YA'''
        rows = listify(db.execute("SELECT * FROM student WHERE username = :username",{"username":request.form.get("username")}) )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["sid"]

        # Redirect user to home page
        return redirect("/")

    # Gets executed when the user reche route via GET(as by clicking a link or via redirect)
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")










def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("apology.html")

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)