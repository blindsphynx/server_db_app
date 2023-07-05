from PyQt5.QtWidgets import QMessageBox
from flask import Flask, request, jsonify
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from tabulate import tabulate

server = Flask(__name__)
DBconnection = [QSqlDatabase.addDatabase("QPSQL")]


@server.route('/')
def home():
    return "This is a home page"


@server.route('/get-data')
def get():
    query = QSqlQuery("SELECT * FROM students")
    table = readFromDatabase(query)
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


def connect_to_postgesql(connection):
    connection[0] = QSqlDatabase.addDatabase("QPSQL")
    connection[0].setDatabaseName("postgres1")
    connection[0].setHostName('localhost')
    connection[0].setUserName('user')
    connection[0].setPassword('pyro127')
    if not connection.open():
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


def readFromDatabase(query):
    pass
