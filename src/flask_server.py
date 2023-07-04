from flask import Flask, request, jsonify
import psycopg2
from tabulate import tabulate

server = Flask(__name__)
DBconnection = [None]
DBcursor = [None]


@server.route('/')
def home():
    return "This is a home page"


@server.route('/get-data')
def get():
    query = "SELECT * FROM students"
    table = readFromDatabase(query, DBcursor)
    return table, 200


@server.route('/post-data', methods=['POST'])
def post():
    if request.method == 'POST':
        name = '"Soldatova Kira"'
        year = 2004
        course = 1
        group = 224
        query = f"INSERT INTO students(id, name, year, course, class) VALUES(6, {name}, {year}, {course}, {group});"
        writeToDatabase(query, cursor=DBcursor)
        return jsonify(id=6, name=name, year=year, course=course, group_=group), 201
        # new_data = request.get_json(force=True)
        # if new_data:
        # name = new_data["name"]
        # year = new_data["year"]
        # course = new_data["course"]
        # group = new_data["group"]
        # print("JSON: ", name, year, course, group)
        # query = f"INSERT INTO students(id, name, year, course, group_) VALUES(6, {name}, {year}, {course}, {group});"
        # writeToDatabase(query, cursor=DBcursor)
        # return jsonify(new_data), 201
        # return None


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
    return tabulate(table, headers=["id", "name", "year", "photo", "course", "group_"], tablefmt='orgtbl')
