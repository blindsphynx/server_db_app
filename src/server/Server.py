from cryptography.fernet import Fernet
from flask import Flask, request, jsonify
import psycopg2
import base64
import json
import os
import logging.config
import configparser

server = Flask(__name__)
DBconnection = [None]
DBcursor = [None]

config = configparser.RawConfigParser()
cur_folder = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(cur_folder, "settings.ini")
config.read(ini_file)

logging.config.fileConfig(ini_file)
logger = logging.getLogger("root")
database_name = config.get("section_server", "dbname")
database_user = config.get("section_server", "db_user")
database_password = config.get("section_server", "db_password")
host = config.get("section_server", "host")
port = config.get("section_server", "port")

username = config.get("section_server", "client_username")
password = config.get("section_server", "client_password")
secret_path = os.path.join(cur_folder, "secret.enc")
with open(secret_path, "rb") as f:
    secret = f.read()


def decode_password(encoded_password, key):
    bytes_password = Fernet(key).decrypt(encoded_password)
    decoded_password = base64.b64decode(bytes_password)
    return decoded_password.decode('ascii')


@server.route("/")
def index():
    auth = request.authorization.parameters
    client_login = auth["username"]
    client_password = decode_password(auth["password"], secret)
    if client_login == username and password == client_password:
        logger.info("Client was authenticated")
        return "Auth successful", 200
    logger.info("Authentication failed")
    return "Access denied", 401


@server.route("/home")
def home():
    return "This is a home page"


@server.route('/get-data')
def get():
    query = "SELECT * FROM students"
    records = readFromDatabase(query, DBcursor)
    table = sqlDataToJSON(records)
    logger.info("GET request executed")
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
        logger.info("POST request executed")
        return jsonify(id=id_, name=name, year=year, picture=photo, course=course, gruppa=group), 201


@server.route("/delete-data", methods=["DELETE"])
def delete():
    if request.method == "DELETE":
        new_data = request.get_json(force=True)
        name = new_data["name"]
        query = f"DELETE FROM students WHERE name='{name}'"
        queryToDatabase(query, DBcursor)
        logger.info("DELETE request executed")
        return "", 204


def connect_to_postgresql(connection, cursor):
    try:
        connection[0] = psycopg2.connect(dbname=database_name, user=database_user,
                                         password=database_password, host=host, port=port)
        connection[0].autocommit = True
        cursor[0] = connection[0].cursor()
    except psycopg2.OperationalError:
        logger.error("Unable to connect to the database")


def queryToDatabase(query, cursor):
    cursor[0].execute(query)
    logger.info("Query was sent to the database")


def readFromDatabase(query, cursor):
    cursor[0].execute(query)
    logger.info("Data was received from the database")
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
