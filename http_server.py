from PyQt5.QtCore import QByteArray, QDataStream, QIODevice
from PyQt5.QtNetwork import QHostAddress, QTcpServer
from tabulate import tabulate
import sys
import psycopg2


class Server(QTcpServer):
    def __init__(self):
        super().__init__()
        self.port = 8000
        self.address = QHostAddress('127.0.0.1')
        self.connection = None
        self.cursor = None

    def run(self):
        if not self.listen(self.address, self.port):
            print("Connection is not established")
            # print("Server has been stopped")
            self.close()
            return
        self.newConnection.connect(self.dealCommunication)

    def dealCommunication(self):
        clientConnection = self.nextPendingConnection()

    def connect_to_postgesql(self):
        self.connection = psycopg2.connect(dbname='postgres1', user='user', password='pyro127',
                                           host='localhost', port='5432')
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        print("[INFO] PostgreSQL connection established")

    def shutdown_DB_connection(self):
        self.connection.close()
        print("[INFO] PostgreSQL connection closed")

    def writeToDatabase(self, query):
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        print("[INFO] Data were added to the database")

    def readFromDatabase(self, query):
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        table = []
        for line in records:
            table.append([*line])
        print(tabulate(table, headers=["id", "name", "year", "photo", "course", "class"], tablefmt='orgtbl'))
        self.cursor.close()


if __name__ == '__main__':
    server = Server()
    server.run()
    server.connect_to_postgesql()
    my_query = "SELECT * FROM students"
    server.readFromDatabase(my_query)
    server.shutdown_DB_connection()
    # sys.exit(server.close())
