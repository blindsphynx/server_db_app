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
        new_data = request.get_json(force=True)
        name = new_data['name']
        year = new_data['year']
        picture = new_data['picture']
        course = new_data['course']
        gruppa = new_data['gruppa']
        query = f"INSERT INTO students(id, name, year, photo, course, gruppa) " \
                f"VALUES(6, '{name}', {year}, '{picture}', {course}, {gruppa});"
        writeToDatabase(query, cursor=DBcursor)
        return jsonify(id=6, name=name, year=year, picture=picture, course=course, gruppa=gruppa), 201


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
    print("[INFO] Data was added to the database")


def readFromDatabase(query, cursor):
    cursor[0].execute(query)
    records = cursor[0].fetchall()
    table = []
    for line in records:
        table.append([*line])
    cursor[0].close()
    return tabulate(table, headers=["id", "name", "year", "photo", "course", "group"], tablefmt='orgtbl')
