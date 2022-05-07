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