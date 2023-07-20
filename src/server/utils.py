from functools import wraps
from flask import make_response, request, current_app


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == "user" and auth.password == "pyro127":
            return f(*args, **kwargs)
        return make_response("<h1>Access denied!</h1>", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})
    return decorated
