import os

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

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
con = sqlite3.connect('mymo.db')
cur = con.cursor()


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("apology.html")

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)




# Application's Routes
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    return 'hello world'



@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        if not request.form.get("username"):
            return apology("Please provide username!")
        #Ensure that the user name does'nt already exists.
        elif len(con.execute("SELECT * FROM users WHERE username =?",request.form.get("username"))):
            return apology("Name already exist")
        else:
            username = request.form.get("username")

        #Ensure password was submited
        if not request.form.get("password"):
            return apology("Please Provide Password!")
        else:
            password = request.form.get("password")

        #Ensure confirm was submited
        if not request.form.get("confirm"):
            return apology("Please re-write the password!")

        #Ensure password == confirm
        else:
            confirm = request.form.get("confirm")
            if password != confirm:
                return apology("passwords don't match!")
            else:
                id_primkey = con.execute("INSERT INTO users (username,hash) VALUES(?,?)",username, generate_password_hash(password))
                # Remember which user has Reigsterd
                session["user_id"] = id_primkey

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
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username

        rows = con.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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









