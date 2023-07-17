import json
from PyQt5.QtWidgets import QMessageBox
from flask import Flask, request, jsonify
import psycopg2

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
        id_ = new_data['id']
        name = new_data['name']
        year = new_data['year']
        photo = new_data['photo']
        course = new_data['course']
        group = new_data['group']
        query = f"INSERT INTO students(id, name, year, photo, course, gruppa) " \
                f"VALUES({id_}, '{name}', {year}, '{photo}', {course}, {group});"
        # query = "DELETE FROM students WHERE name='Kira'"
        writeToDatabase(query, DBcursor)
        return jsonify(id=6, name=name, year=year, picture=photo, course=course, gruppa=group), 201


def connect_to_postgesql(connection, cursor):
    connection[0] = psycopg2.connect(dbname='postgres1', user='user',
                                     password='pyro127', host='localhost', port='5432')
    connection[0].autocommit = True
    cursor[0] = connection[0].cursor()
    if not connection[0]:
        QMessageBox.critical(
            None,
            "Error!",
            "Unable to connect a database\n\n"
            "Database Error: %s" % connection[0].lastError().databaseText(),
        )
        return False
    print("[INFO] PostgreSQL connection established")
    return True


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
        data = {"id": line[0], "name": line[1], "year": line[2], "photo": line[3], "course": line[4], "group": line[5]}
        table.append(data)
    result = json.dumps(table)
    return result
