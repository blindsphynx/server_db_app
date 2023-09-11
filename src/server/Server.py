import base64
import configparser
import json
import logging.config
import os
import psycopg2
from flask import Flask, request, jsonify, g
from flask_httpauth import HTTPBasicAuth

server = Flask(__name__)
app_context = server.app_context()
app_context.push()
DBcursor = [None]
cur_folder = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(cur_folder, "settings.ini")


def get_config_parser():
    config_parser = getattr(g, 'config', None)
    if config_parser is None:
        config_parser = g.config = configparser.RawConfigParser()
    return config_parser


@server.before_request
def load():
    g.config = get_config_parser()
    g.config.read(ini_file)
    g.database_name = g.config.get("section_server", "dbname")
    g.database_user = g.config.get("section_server", "db_user")
    g.database_password = g.config.get("section_server", "db_password")
    g.host = g.config.get("section_server", "host")
    g.port = g.config.get("section_server", "port")
    g.username = g.config.get("section_server", "client_username")
    g.hashed_password = g.config.get("section_server", "hash")
    g.credentials = dict({g.username: g.hashed_password})

    try:
        g.db_connection = psycopg2.connect(dbname=g.database_name, user=g.database_user,
                                           password=g.database_password, host=g.host, port=g.port)
        g.db_connection.autocommit = True
        g.cursor = g.db_connection.cursor()
        logger.info("Database connection established")
    except psycopg2.OperationalError:
        logger.error("Unable to connect to the database")


logging.config.fileConfig(ini_file)
logger = logging.getLogger("root")
auth = HTTPBasicAuth()


def post_data(data):
    id_ = data['id']
    name = data['name']
    photo = data['photo']
    year = data['year']
    course = data['course']
    group = data['group']
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
    with app_context:
        queryToDatabase(query, g.cursor)
    if photo:
        binary_photo = data["binary_photo"]
        photo_data = base64.b64decode(binary_photo)
        with open("server_pictures/" + os.path.basename(photo), "wb") as file:
            file.write(photo_data)
    logger.info("POST request executed")
    return jsonify(id=id_, name=name, year=year, picture=photo, course=course, gruppa=group), 201


@auth.verify_password
def verify_password(user, password):
    if user in g.credentials and g.credentials.get(user) == password:
        return user


@server.route("/")
@auth.login_required
def index():
    if auth.current_user():
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
    with app_context:
        records = readFromDatabase(query, g.cursor)
    table = sqlDataToJSON(records)
    logger.info("GET request executed")
    return table, 200


@server.route('/post-data', methods=['POST'])
def post():
    new_data = request.get_json(force=True)
    res = post_data(new_data)
    return res


@server.route('/edit-data', methods=['PUT'])
def edit():
    new_data = request.get_json(force=True)
    res = post_data(new_data)
    return res


@server.route("/delete-data", methods=["DELETE"])
def delete():
    if request.method == "DELETE":
        new_data = request.get_json(force=True)
        name = new_data["name"]
        query = f"DELETE FROM students WHERE name='{name}'"
        with app_context:
            queryToDatabase(query, g.cursor)
        logger.info("DELETE request executed")
        return "", 204


def queryToDatabase(query, cursor):
    cursor.execute(query)
    logger.info("Query was sent to the database")


def readFromDatabase(query, cursor):
    cursor.execute(query)
    logger.info("Data was received from the database")
    return cursor.fetchall()


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
