from PyQt5.QtWidgets import QMessageBox
from flask import Flask, request, jsonify
import psycopg2
import base64
import json
import os
import logging
from utils import auth_required


server = Flask(__name__)

DBconnection = [None]
DBcursor = [None]
logging.basicConfig(level=logging.DEBUG, filename="server.log", filemode="w",
                    encoding="utf-8", format="%(asctime)s %(levelname)s %(message)s")


@server.route("/")
@auth_required
def index():
    return "<h1>Hello, World!</h1>"


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
        photo = new_data['photo']
        year = new_data['year']
        course = new_data['course']
        group = new_data['group']
        if year == "":
            year = "NULL"
        if course == "":
            course = "NULL"
        if group == "":
            group = "NULL"
        query = f"INSERT INTO students(id, name, year, photo, course, gruppa) " \
                f"VALUES({id_}, '{name}', {year}, '{photo}', {course}, {group}) " \
                f"ON CONFLICT (id) DO UPDATE SET name='{name}', year={year}, " \
                f"photo='{photo}', course={course}, gruppa={group} WHERE students.id={id_};"
        queryToDatabase(query, DBcursor)
        if photo:
            binary_photo = new_data['binary_photo']
            photo_data = base64.b64decode(binary_photo)
            with open("server_pictures/" + os.path.basename(photo), "wb") as file:
                file.write(photo_data)
        return jsonify(id=id_, name=name, year=year, picture=photo, course=course, gruppa=group), 201


@server.route('/delete-data', methods=['DELETE'])
def delete():
    if request.method == 'DELETE':
        new_data = request.get_json(force=True)
        name = new_data['name']
        query = f"DELETE FROM students WHERE name='{name}'"
        queryToDatabase(query, DBcursor)
        return "", 204


# @server.run(debug=True)
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


def queryToDatabase(query, cursor):
    cursor[0].execute(query)
    print("[INFO] Query was sent to the database")


def readFromDatabase(query, cursor):
    cursor[0].execute(query)
    records = cursor[0].fetchall()
    table = []
    for line in records:
        data = {"id": line[0], "name": line[1], "year": line[2], "photo": line[3], "course": line[4], "group": line[5]}
        for key in data:
            if data[key] is None:
                data[key] = ""
        table.append(data)
    result = json.dumps(table)
    return result
