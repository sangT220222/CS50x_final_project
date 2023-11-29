from flask import redirect, render_template, session

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# API link : https://api.spoonacular.com/recipes/complexSearch
# API key : ca38a5949eac429382c9501131ec7d24


