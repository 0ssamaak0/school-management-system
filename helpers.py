from functools import wraps
from flask import session, request, redirect, url_for, render_template

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



def apology(message):
    ''' عازين نعدل دي عشان شكله بشعYA'''

    return render_template("apology.html", msg = message)


class Student:
    def __init__(self,sid ,name, address, dob, GPA, nationality, national_id, passport, department, advisor_id ):
        self.sid = sid
        self.name = name
        self.address = address
        self.dob = dob
        self.GPA = GPA
        self.nationality = nationality
        self.national_id = national_id
        self.passport = passport
        self.department = department
        self.advisor_id = advisor_id


class Staff:
    def __init__(self,staff_id,name,degree,salary):
        self.staff_id = staff_id
        self.name = name
        self.degree = degree
        self.salary = salary


class TeachingStaff(Staff):
    def __init__(self, staff_id, name, degree, salary, courses_number):
        super().__init__(staff_id, name, degree, salary)
        self.courses_number = courses_number


class Advisors(Staff):
    def __init__(self, staff_id, name, degree, salary,office_hours,students_advised):
        super().__init__(staff_id, name, degree, salary)
        self.office_hours = office_hours
        self.students_advised = students_advised


class Courses():
    def __init__(self,cid,name,department,CH,midterm,activities,final):
        self.cid = cid
        self.department = department
        self.name = name
        self.Ch = CH
        self.midterm = midterm
        self.activities = activities
        self.final = final
        self.total = midterm + activities + final