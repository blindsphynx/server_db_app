import sys
import requests
import json
import qtawesome as qta
from PyQt5.QtCore import pyqtSignal, QObject, QSize, QDir, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, \
    QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QAbstractItemView, QMessageBox, QFileDialog


class Communicate(QObject):
    buttonClicked = pyqtSignal()


class TextEdit(QWidget):
    def __init__(self, cells, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit record")
        self.setFixedWidth(900)
        self.setFixedHeight(400)
        self.cells = cells
        self.editField1 = QLineEdit(self)
        self.editField2 = QLineEdit(self)
        self.editField3 = QLineEdit(self)
        self.editField4 = QLineEdit(self)
        self.image = QLabel()
        icon = qta.icon("fa5s.camera", color='blue')
        self.image.setPixmap(icon.pixmap(QSize(24, 24)))
        self.imageName = QLabel(self.cells["photo"])
        self.saveButton = QPushButton("Save")
        self.cancelButton = QPushButton("Cancel")
        self.uploadImageButton = QPushButton("Upload new photo")
        self.communicate = Communicate()
        self.emitSignal()

        self.setLayouts()
        self.setValues()
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)
        self.cancelButton.clicked.connect(self.uploadButtonClicked)

    def emitSignal(self):
        self.communicate.buttonClicked.connect(self.saveButtonClicked)
        self.show()

    def buttonPressEvent(self, event):
        self.communicate.buttonClicked.emit()

    def setLayouts(self):
        mainLayout = QVBoxLayout()
        labelsLayout = QVBoxLayout()
        fieldsLayout = QVBoxLayout()
        commonLayout1 = QHBoxLayout()
        buttonsLayout = QHBoxLayout()
        imageLayout = QHBoxLayout()

        label1 = QLabel("Name:")
        label2 = QLabel("Year:")
        label3 = QLabel("Photo:")
        label4 = QLabel("Course:")
        label5 = QLabel("Group:")

        labelsLayout.addWidget(label1)
        labelsLayout.addWidget(label2)
        labelsLayout.addWidget(label3)
        labelsLayout.addWidget(label4)
        labelsLayout.addWidget(label5)

        fieldsLayout.addWidget(self.editField1)
        fieldsLayout.addWidget(self.editField2)
        imageLayout.addWidget(self.image)
        imageLayout.addWidget(self.imageName)
        imageLayout.addWidget(self.uploadImageButton)
        fieldsLayout.addLayout(imageLayout)
        fieldsLayout.addWidget(self.editField3)
        fieldsLayout.addWidget(self.editField4)

        buttonsLayout.addWidget(self.saveButton)
        buttonsLayout.addWidget(self.cancelButton)

        commonLayout1.addLayout(labelsLayout)
        commonLayout1.addLayout(fieldsLayout)
        mainLayout.addLayout(commonLayout1)
        mainLayout.addLayout(buttonsLayout)
        self.setLayout(mainLayout)

    def setValues(self):
        self.editField1.setText(self.cells["name"])
        self.editField2.setText(self.cells["year"])
        self.editField3.setText(self.cells["course"])
        self.editField4.setText(self.cells["group"])

    def saveButtonClicked(self):
        if self.editField1.text():
            newData = {"name": self.editField1.text(), "year": self.editField2.text(),
                       "photo": "",
                       "course": self.editField3.text(), "group": self.editField4.text()}
            json_object = json.dumps(newData, indent=4)
            with open("save.json", "w") as outfile:
                outfile.write(json_object)
            self.infoMessageBox(title="Saving", message="Data was saved")
        else:
            QMessageBox.critical(
                None,
                "Error while saving",
                "Required field 'name'"
            )

    def cancelButtonClicked(self):
        self.editField1.setText(self.cells["name"])
        self.editField2.setText(self.cells["year"])
        self.editField3.setText(self.cells["course"])
        self.editField4.setText(self.cells["group"])
        self.infoMessageBox(title="Cancel", message="Changes were canceled")

    @pyqtSlot()
    def uploadButtonClicked(self):
        image = QFileDialog.getOpenFileName(None, 'OpenFile', '', "Image file(*.jpg)")
        imagePath = image[0]
        pixmap = QPixmap(imagePath)
        self.label.setPixmap(pixmap)
        self.label.adjustSize()
        print(imagePath)

    def infoMessageBox(self, title, message):
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(message)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.buttonClicked.connect(msgBox.close)
        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            print("cancel OK clicked")


def getImageLabel(path):
    with open(path, "rb") as image:
        file = image.read()
        b = bytearray(file)
    try:
        imglabel = QLabel(" ")
        imglabel.setScaledContents(True)
        pixmap = QPixmap()
        pixmap.loadFromData(b, 'jpg')
        imglabel.setPixmap(pixmap)
        imglabel.setFixedWidth(150)
        return imglabel
    except Exception as err:
        print(err)


class MyTable(QTableWidget):
    def __init__(self, tableData, parent=None):
        super().__init__(parent)
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["Name", "Year", "Photo", "Course", "Group"])
        self.data = tableData
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

    def addNewRow(self):
        rowCount = self.rowCount()
        self.insertRow(rowCount)

    def removeOneRow(self):
        selected = self.selectedItems()
        if selected:
            newData = {"name": self.editField1.text(), "year": self.editField2.text(),
                       "course": self.editField3.text(), "group": self.editField4.text()}
            json_object = json.dumps(newData, indent=4)
            with open("delete.json", "w") as outfile:
                outfile.write(json_object)
            self.removeRow(self.currentRow())

    def showTable(self):
        records = len(self.data)
        for i in range(records):
            rows = self.rowCount()
            self.setRowCount(rows + 1)
            for num in range(records):
                self.setItem(num, 0, QTableWidgetItem(str(self.data[num]["name"])))
                self.setItem(num, 1, QTableWidgetItem(str(self.data[num]["year"])))
                if self.data[num]["photo"]:
                    item = getImageLabel(self.data[num]["photo"])
                    self.setCellWidget(num, 2, item)
                else:
                    self.setItem(num, 2, QTableWidgetItem(str(self.data[num]["photo"])))
                self.setItem(num, 3, QTableWidgetItem(str(self.data[num]["course"])))
                self.setItem(num, 4, QTableWidgetItem(str(self.data[num]["group"])))
        self.resizeColumnsToContents()


class DatabaseClient(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.subwindow = None
        self.setWindowTitle("Database Students")
        self.resize(1100, 500)
        self.host = "http://localhost:8000/"

        mainLayout = QHBoxLayout()
        table = self.getRequest().json()
        self.view = MyTable(table)
        mainLayout.addWidget(self.view)

        self.setLayout(mainLayout)
        buttonLayout = QVBoxLayout()
        self.view.showTable()

        newButton = QPushButton("New record")
        newButton.clicked.connect(self.view.addNewRow)
        buttonLayout.addWidget(newButton)

        removeButton = QPushButton("Remove")
        removeButton.clicked.connect(self.view.removeOneRow)
        buttonLayout.addWidget(removeButton)

        editButton = QPushButton("Edit")
        editButton.clicked.connect(self.createSubwindow)
        buttonLayout.addWidget(editButton)

        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def createSubwindow(self):
        cells = {}
        fields = ["name", "year", "course", "group"]
        selected = self.view.selectedItems()
        path = self.view.data[self.view.currentRow()]["photo"]
        print(path)
        if selected:
            for i in range(len(selected)):
                cells.update({fields[i]: self.view.selectedItems()[i].text()})
            cells.update({"photo": path})
        else:
            for i in range(len(fields)):
                cells.update({fields[i]: ""})
        print(cells)
        self.subwindow = TextEdit(cells)
        self.subwindow.show()

    def getRequest(self):
        req = requests.get(self.host + "/get-data")
        return req

    def postRequest(self, new_data):
        hdrs = {"Content-Type": "application/json; charset=utf-8", "Accept": "application/json"}
        req = requests.post(self.host + "/post-data", json=new_data, headers=hdrs)
        # print(req.headers)


if __name__ == '__main__':
    f = open("file.json")
    data = json.load(f)
    app = QApplication(sys.argv)
    client = DatabaseClient()
    client.show()
    # client.postRequest(data)
    sys.exit(app.exec_())
