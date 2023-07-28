from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QLineEdit, QPushButton, QMessageBox


class LoginWidget(QWidget):
    signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(400, 120)

        layout = QGridLayout()
        label_name = QLabel('<font size="4"> Username: </font>')
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter your username")
        layout.addWidget(label_name, 0, 0)
        layout.addWidget(self.username, 0, 1)

        label_password = QLabel('<font size="4"> Password: </font>')
        self.password = QLineEdit()
        self.password.setPlaceholderText("Enter your password")
        layout.addWidget(label_password, 1, 0)
        layout.addWidget(self.password, 1, 1)

        button_login = QPushButton("Log in")
        button_login.setFixedWidth(60)
        button_login.clicked.connect(self.__logInClicked)
        layout.addWidget(button_login, 2, 1, 1, 2)
        layout.setRowMinimumHeight(2, 75)
        self.setLayout(layout)

    @pyqtSlot()
    def __logInClicked(self):
        if self.username.text() and self.password.text():
            self.signal.emit()
            print("emit login signal")
            self.close()
        else:
            QMessageBox.critical(
                None,
                "Error",
                "Incorrect username or password"
            )
