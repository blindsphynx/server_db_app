from flask import Flask, request, redirect, url_for, json

server = Flask(__name__)
data = {"language": "Python",
        "framework": "Flask",
        "versions": {
         "python": "3.9.0",
         "flask": "1.1.2"
        },
        "examples": ["query", "form", "json"],
        "boolean_test": True}


@server.route('/')
def hello():
    return "Hello from localhost"


if __name__ == '__main__':
    server.run(port=8000)
