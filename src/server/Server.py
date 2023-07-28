from PyQt5.QtWidgets import QMessageBox
from cryptography.fernet import Fernet
from flask import Flask, request, jsonify, make_response, session
import psycopg2
import base64
import json
import os
import logging
import configparser

server = Flask(__name__)
server.secret_key = "27eduQA09"

DBconnection = [None]
DBcursor = [None]

config = configparser.ConfigParser()
config.read('settings.ini')
log_level = config.get('section_log', 'level')
file = config.get('section_log', 'filename')
mode = config.get('section_log', 'filemode')
encoding = config.get('section_log', 'encoding')
logging.basicConfig(level=log_level, filename=file, filemode=mode, encoding=encoding)
with open("secret.enc", "rb") as f:
    secret = f.read()


def decode_password(encoded_password, key):
    bytes_password = Fernet(key).decrypt(encoded_password)
    decoded_password = base64.b64decode(bytes_password)
    return decoded_password.decode('ascii')


@server.route("/")
def index():
    session["username"] = config.get('section_auth', 'username')
    session["password"] = config.get('section_auth', 'password')
    auth = request.authorization.parameters
    client_password = decode_password(auth["password"], secret)
    if auth["username"] == session.get("username") and client_password == session.get("password"):
        print("auth successful")
        session["logged"] = True
        return "<h1>auth successful</h1>"
    else:
        print("Access denied")
        session["logged"] = False
        return make_response("<h1>Access denied!</h1>", 401, {'WWW-Authenticate': 'Basic realm="Login required!"'})


@server.route('/home')
def home():
    return "This is a home page"


@server.route('/get-data')
def get():
    # if session["logged"]:
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


def connect_to_postgesql(connection, cursor):
    connection[0] = psycopg2.connect(dbname='postgres1', user='user',
                                     password='pyro127', host='localhost', port='5432')
    connection[0].autocommit = True
    cursor[0] = connection[0].cursor()
    if connection[0] is None:
        QMessageBox.critical(
            None,
            "Error!",
            "Unable to connect a database\n\n"
            "Database Error: %s" % connection[0].DataError().databaseText(),
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
        if data["photo"]:
            path = os.path.curdir + "/server_pictures/" + data["photo"]
            image = ""
            with open(path, "rb") as img:
                image = base64.encodebytes(img.read()).decode("utf-8")
            data.update({"binary_photo": image})
        table.append(data)
    result = json.dumps(table)
    return result
