from flask import Flask, request, redirect, url_for, jsonify
import psycopg2
from tabulate import tabulate

server = Flask(__name__)
DBconnection = [None]
DBcursor = [None]
data = {"language": "Python",
        "framework": "Flask",
        "versions": {
            "python": "3.9.0",
            "flask": "1.1.2"
        },
        "examples": ["query", "form", "json"],
        "boolean_test": True}


@server.route('/')
def home():
    return "This is a home page"


@server.route('/get-data')
def get():
    query = "SELECT * FROM students"
    table = readFromDatabase(query, DBcursor)
    return table, 200


@server.route('/post-data')
def post():
    new_data = request.get_data()
    return jsonify(new_data), 201


def connect_to_postgesql(connection, cursor):
    connection[0] = psycopg2.connect(dbname='postgres1', user='user',
                                     password='pyro127', host='localhost', port='5432')
    connection[0].autocommit = True
    cursor[0] = connection[0].cursor()
    print("[INFO] PostgreSQL connection established")


def shutdown_DB_connection(connection):
    connection[0].close()
    print("[INFO] PostgreSQL connection closed")


def writeToDatabase(query, cursor):
    cursor[0].execute(query)
    records = cursor[0].fetchall()
    print("[INFO] Data was added to the database")


def readFromDatabase(query, cursor):
    cursor[0].execute(query)
    records = cursor[0].fetchall()
    table = []
    for line in records:
        table.append([*line])
    cursor[0].close()
    return tabulate(table, headers=["id", "name", "year", "photo", "course", "class"], tablefmt='orgtbl')
