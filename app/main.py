import os

import sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology


isStudent = None

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
con = sqlite3.connect('school.db', check_same_thread=False)
db = con.cursor()


def listify(obj):
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


@app.route("/homeStaff", methods=["GET", "POST"])
@login_required
def homestaff():
    if request.method == "GET":
        rows = listify(db.execute(
            "SELECT name, department, ch,midterm,activities, final FROM teaches t, courses c WHERE (t.cid = c.cid AND t.staffId = :id)", {"id": session["user_id"]}))
        return render_template("index.html", msg="home_staff", name=session["user_username"], courses=rows)
    else:
        course = request.form.get("add_course")
        ass = request.form.get("add_assignment")
        marks = request.form.get("add_marks")
        person = listify(db.execute(
            "SELECT * FROM teachingStaff WHERE staffId = :id", {"id": session["user_id"]}))
        if course is not None:
            courses = listify(db.execute(
                "SELECT * FROM Courses WHERE department IN ( :department , 'asu' )", {"department": person[0]['department']}))
            return render_template("index.html", msg="courses_section", courses=courses)
        elif ass is not None:
            rows = listify(db.execute(
                "SELECT name FROM teaches t, courses c WHERE (t.cid = c.cid AND t.staffId = :ID)", {"ID": session["user_id"]}))
            return render_template("index.html", msg="add_assignment", courses=rows)
        else:
            rows = listify(db.execute(
                "SELECT name FROM teaches t, courses c WHERE (t.cid = c.cid AND t.staffId = :ID)", {"ID": session["user_id"]}))
            return render_template("index.html", msg="add_marks", courses=rows)


@app.route("/homeStudent", methods=["GET", "POST"])
@login_required
def homestudent():
    if request.method == "GET":
        rows = listify(db.execute(
            "SELECT name, department, ch,midterm,activities, final FROM register t, courses c WHERE (t.register_cid = c.cid AND t.register_sid == :id)", {"id": session["user_id"]}))
        # if len(rows) == 0:
        #   rows == "nothing Registered Yet"
        assignments = listify(db.execute(
            "SELECT * FROM register r,assign a,courses c WHERE (r.register_cid = a.cid AND c.cid = r.register_cid AND register_sid = :sid)", {"sid": session["user_id"]}))
        # return apology(assignments)
        return render_template("index.html", msg="home_student", name=session["user_username"], courses=rows, assignments=assignments)
    else:
        register = request.form.get("registerCourse")
        view = request.form.get("viewCourses")
        person = listify(db.execute(
            "SELECT * FROM student WHERE sid = :id", {"id": session["user_id"]}))
        if register is not None:
            courses = listify(db.execute(
                "SELECT * FROM Courses WHERE department IN ( :department , 'asu' )", {"department": person[0]['department']}))
            return render_template("index.html", msg="register_courses", courses=courses)
        else:
            courses = listify(db.execute(
                "SELECT * FROM courses c, register r WHERE (c.cid = r.register_cid AND r.register_sid = :id)", {"id": session["user_id"]}))
            return render_template("index.html", msg="current_courses", courses=courses)


@app.route("/addCourse", methods=["GET", "POST"])
@login_required
def addCourse():
    if request.method == "GET":
        return apology("to do")
    else:
        global isStudent
        courseId = request.form.get("course")
        # print(isStudent)
        # return apology(isStudent)
        if not isStudent:
            rows = listify(db.execute(
                "SELECT * FROM teaches WHERE (cid = :cid AND staffId = :id)", {"cid": courseId, "id": session["user_id"]}))
        else:
            rows = listify(db.execute(
                "SELECT * FROM register WHERE (register_cid = :cid AND register_sid = :id)", {"cid": courseId, "id": session["user_id"]}))
        # return apology(len(rows))
        if len(rows) != 0:
            return apology("Course is already selected!")
        else:
            if not isStudent:
                db.execute("INSERT INTO teaches (staffId,cid) VALUES(:staffID,:cid)", {
                           "staffID": session["user_id"], "cid": courseId})
                con.commit()
                return redirect("/homeStaff")
            else:
                db.execute("INSERT INTO register (register_sid,register_cid) VALUES(:sid,:cid)", {
                           "sid": session["user_id"], "cid": courseId})
                con.commit()
                return redirect("/homeStudent")


@app.route("/addAssignment", methods=["GET", "POST"])
@login_required
def addassignment():
    if request.method == "POST":
        course = request.form.get("course")
        des = request.form.get("description")
        date = request.form.get("date")
        if course == "":
            return apology("Please Select The Course")
        if des == "":
            return apology("Please Enter Description")
        if date == "":
            return apology("Please Enter The Due Date")
        rows = listify(db.execute(
            "SELECT cid FROM courses WHERE name = :name", {"name": course}))
        db.execute("INSERT INTO assign (staffId,cid,description,deadline) VALUES (:id,:cid,:des,:due)", {
                   "id": session["user_id"], "cid": rows[0]['cid'], "des": des, "due": date})
        con.commit()
        return redirect("/homeStaff")


@app.route("/addMarks", methods=["GET", "POST"])
@login_required
def addmarks():
    if request.method == "POST":
        course = request.form.get("course")
        if course == "":
            return apology("Please Select a Course")
        # To Do: better queries
        cid = listify(db.execute(
            "SELECT cid FROM courses WHERE name=:n", {"n": course}))
        cid = cid[0]['cid']
        rows = listify(db.execute("SELECT register_sid,grade,gradescore,register_midterm,register_activities,register_final,name FROM teaches t,register r,student s WHERE (t.cid = r.register_cid AND r.register_cid = :cid AND t.staffId = :id AND s.sid = r.register_sid)", {
                       "id": session["user_id"], "cid": cid}))
        return render_template("index.html", msg="show_students", students=rows)


@app.route("/changedMarks", methods=["GET", "POST"])
@login_required
def changemarks():
    if request.method == "POST":
        activities = request.form.get('student')
        return apology("To Do")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html", msg="register_student")
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
        users = listify(db.execute(
            "SELECT * FROM student WHERE username =:username", {"username": username}))
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
        if confirmation != password:
            return apology("The Passwords Don't Match!")
        else:
            if nationality == 'egyptian':
                db.execute('INSERT INTO student (name,address,dateOfBirth,nationality,nationalId,department,username,password) VALUES(:name,:address,:dateOfBirth,:nationality,:nationalID,:department,:username,:password)', {
                           "name": fullname, "address": address, "dateOfBirth": dob, "nationality": nationality, "nationalID": Id, "department": dept, "username": username, "password": generate_password_hash(password)})
                con.commit()
            else:
                db.execute('INSERT INTO student (name,address,dateOfBirth,nationality,passport,department,username,password) VALUES(:name,:address,:dateOfBirth,:nationality,:passport,:department,:username,:password)', {
                           "name": fullname, "address": address, "dateOfBirth": dob, "nationality": nationality, "passport": Id, "department": dept, "username": username, "password": generate_password_hash(password)})
                con.commit()

            user_data_list = listify(db.execute(
                "SELECT sid, username FROM student WHERE username =:username", {"username": username}))

            # Remember which user has Reigsterd
            session["user_id"] = user_data_list[0]["sid"]
            session["user_username"] = user_data_list[0]["username"]

            # Redirect the user to home page
            return redirect("/login")


@app.route("/register_staff", methods=["GET", "POST"])
def register_staff():
    if request.method == "GET":
        return render_template("register.html", msg="register_staff")
    else:
        fullname = request.form.get("fullname")
        username = request.form.get("username")
        degree = request.form.get("degree")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        dept = request.form.get("department")

        if fullname == "":
            return apology("Please Enter your Full name")
        if len(fullname) < 5:
            return apology("your name should be at least 5 characters long")
        if username == "":
            return apology("Please Enter your account")
        if len(username) < 5:
            return apology("your Account should be at least 5 characters long")
        users = listify(db.execute(
            "SELECT * FROM teachingStaff WHERE username =:username", {"username": username}))
        if len(users) != 0:
            return apology('Email Already Exists!')
        if degree == "":
            return apology("Please Select Your Degree")
        if dept == "":
            return apology("Please Choose Your Department")
        if password == "":
            return apology("Please Enter your Password")
        if len(password) < 8:
            return apology("Your Password Should Be At Least 8 Digits long")
        if confirm == "":
            return apology("Please Re-Enter your password")
        if confirm != password:
            return apology("The Passwords Don't Match!")
        else:
            db.execute('INSERT INTO teachingStaff (name,degree,username,password,department) VALUES(:name,:degree,:username,:password,:department)', {
                       "name": fullname, "degree": degree, "username": username, "password": generate_password_hash(password), "department": dept})
            con.commit()
            # Redirect the user to home page
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """
    global isStudent
    # Forget any user_id
    session.clear()

    # gets executed when the user submit the form
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")
        Type = request.form.get("type")
        if username == "":
            return apology("must provide username")
        if password == "":
            return apology("must provide Password")
        if Type == "":
            return apology("Please Select The Type")

        # Query database for username
        ''' اسم الداتا بيز الي انت حاطه غبي YA'''
        if Type == 'student':
            print("he is")
            isStudent = True
            rows = listify(db.execute("SELECT * FROM student WHERE username = :username",
                           {"username": request.form.get("username")}))
            # Remember which user has logged in
            session["user_id"] = rows[0]["sid"]
            session["user_username"] = rows[0]["name"]

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
                return apology("invalid username and/or password")
            # Redirect user to home page
            return redirect("/homeStudent")
        else:
            isStudent = False
            rows = listify(db.execute("SELECT * FROM teachingStaff WHERE username = :username",
                           {"username": request.form.get("username")}))
            # Remember which user has logged in
            session["user_id"] = rows[0]["staffId"]
            session["user_username"] = rows[0]["name"]

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
                return apology("invalid username and/or password")
            # Redirect user to home page
            return redirect("/homeStaff")

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
