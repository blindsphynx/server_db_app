from PyQt5.QtCore import QByteArray, QDataStream, QIODevice
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtNetwork import QHostAddress, QTcpServer


class Server(QDialog):
    def __init__(self):
        super().__init__()
        self.tcpServer = None

    def sessionOpened(self):
        self.tcpServer = QTcpServer(self)
        port = 8000
        address = QHostAddress('127.0.0.1')
        if not self.tcpServer.listen(address, port):
            print("cannot listen!")
            self.close()
            return
        self.tcpServer.newConnection.connect(self.dealCommunication)

    def dealCommunication(self):
        clientConnection = self.tcpServer.nextPendingConnection()
        block = QByteArray()
        out = QDataStream(block, QIODevice.ReadWrite)
        # We are using PyQt5 so set the QDataStream version accordingly.
        out.setVersion(QDataStream.Qt_5_0)
        out.writeUInt16(0)
        message = "message from server!"
        message = bytes(message, encoding='ascii')
        # now use the QDataStream and write the byte array to it.
        out.writeString(message)
        out.device().seek(0)
        out.writeUInt16(block.size() - 2)

        clientConnection.waitForReadyRead()
        received_data = clientConnection.readAll()
        # in this case we print to the terminal could update text of a widget if we wanted.
        print(str(received_data, encoding='ascii'))
        # get the connection ready for clean up
        clientConnection.disconnected.connect(clientConnection.deleteLater)
        clientConnection.write(block)
        clientConnection.disconnectFromHost()

