from PyQt5.QtCore import QByteArray, QDataStream, QIODevice
from PyQt5.QtNetwork import QHostAddress, QTcpServer, QTcpSocket
from tabulate import tabulate
import psycopg2


class Server(QTcpServer):
    def __init__(self):
        super().__init__()
        self.port = 8000
        self.address = QHostAddress('127.0.0.1')
        self.connection = None
        self.cursor = None

    def enableNewConnection(self):
        if self.hasPendingConnections():
            print("Incoming Connection...")
            self.dealCommunication()
            # self.newConnection.connect(self.dealCommunication)

    def run(self):
        if self.listen(self.address, self.port):
            print(f"Server is listening on port: {self.port}")
            if self.waitForNewConnection(10000):
                self.enableNewConnection()
        else:
            print("Server couldn't wake up")

    def dealCommunication(self):
        print("Client connection established")
        clientConnection = self.nextPendingConnection()
        print(f"Connection is open: {clientConnection.isOpen()}")
        clientConnection.waitForReadyRead(1000)

        block = QByteArray()
        out = QDataStream(block, QIODevice.ReadWrite)

        out.setVersion(QDataStream.Qt_5_0)
        out.writeUInt16(0)
        message = "message from server!"
        message = bytes(message, encoding='ascii')

        out.writeString(message)
        out.device().seek(0)
        out.writeUInt16(block.size() - 2)

        clientConnection.waitForReadyRead(1000)
        received_data = clientConnection.readAll()
        print(str(received_data, encoding='ascii'))

        clientConnection.disconnected.connect(clientConnection.deleteLater)
        clientConnection.write(block)
        clientConnection.disconnectFromHost()

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
        print("[INFO] Data was added to the database")

    def readFromDatabase(self, query):
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        table = []
        for line in records:
            table.append([*line])
        print(tabulate(table, headers=["id", "name", "year", "photo", "course", "class"], tablefmt='orgtbl'))
        self.cursor.close()
