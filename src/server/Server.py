import sys

from PyQt5.QtWidgets import QMessageBox, QApplication
from cryptography.fernet import Fernet
from flask import Flask, request, jsonify
import psycopg2
import base64
import json
import os
import logging
import configparser

server = Flask(__name__)
DBconnection = [None]
DBcursor = [None]

config = configparser.ConfigParser()
config.read('settings.ini')
server.secret_key = config.get("section_server", "secret_key")
database_name = config.get("section_server", "dbname")
database_user = config.get("section_server", "user")
database_password = config.get("section_server", "password")
host = config.get("section_server", "host")
port = config.get("section_server", "port")
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
    query = "SELECT * FROM users"
    records = readFromDatabase(query, DBcursor)
    auth = request.authorization.parameters
    client_login = auth["username"]
    client_password = decode_password(auth["password"], secret)
    for rec in records:
        if client_login == rec[1] and rec[2] == client_password:
            print("auth successful")
            return "Auth successful", 200
        else:
            print("Access denied")
            return "Access denied", 401


@server.route("/home")
def home():
    return "This is a home page"


@server.route('/get-data')
def get():
    query = "SELECT * FROM students"
    records = readFromDatabase(query, DBcursor)
    table = sqlDataToJSON(records)
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
            binary_photo = new_data["binary_photo"]
            photo_data = base64.b64decode(binary_photo)
            with open("server_pictures/" + os.path.basename(photo), "wb") as file:
                file.write(photo_data)
        return jsonify(id=id_, name=name, year=year, picture=photo, course=course, gruppa=group), 201


@server.route("/delete-data", methods=["DELETE"])
def delete():
    if request.method == "DELETE":
        new_data = request.get_json(force=True)
        name = new_data["name"]
        query = f"DELETE FROM students WHERE name='{name}'"
        queryToDatabase(query, DBcursor)
        return "", 204


def connect_to_postgesql(connection, cursor):
    connection[0] = psycopg2.connect(dbname=database_name, user=database_user,
                                     password=database_password, host=host, port=port)
    connection[0].autocommit = True
    cursor[0] = connection[0].cursor()


def queryToDatabase(query, cursor):
    cursor[0].execute(query)
    print("[INFO] Query was sent to the database")


def readFromDatabase(query, cursor):
    cursor[0].execute(query)
    return cursor[0].fetchall()


def sqlDataToJSON(records):
    table = []
    for line in records:
        data = {"id": line[0], "name": line[1], "year": line[2], "photo": line[3], "course": line[4], "group": line[5]}
        for key in data:
            if data[key] is None:
                data[key] = ""
        if data["photo"]:
            path = os.path.curdir + "/server_pictures/" + data["photo"]
            with open(path, "rb") as img:
                image = base64.encodebytes(img.read()).decode("utf-8")
            data.update({"binary_photo": image})
        table.append(data)
    result = json.dumps(table)
    return result
