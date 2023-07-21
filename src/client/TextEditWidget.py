from PyQt5.QtCore import QSize, pyqtSignal, pyqtSlot, QRegExp
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QLineEdit, QWidget
import json
import base64
import os
import qtawesome as qta


def infoMessageBox(title, message):
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Information)
    msgBox.setText(message)
    msgBox.setWindowTitle(title)
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.buttonClicked.connect(msgBox.close)
    returnValue = msgBox.exec()
    if returnValue == QMessageBox.Ok:
        print("OK clicked")


class TextEdit(QWidget):
    signal = pyqtSignal()

    def __init__(self, cells, row, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit record")
        self.setFixedWidth(1000)
        self.setFixedHeight(400)
        self.cells = cells
        self.row = row + 1
        self.editField1 = QLineEdit(self)
        self.editField2 = QLineEdit(self)
        self.editField3 = QLineEdit(self)
        self.editField4 = QLineEdit(self)

        reg_ex_text = QRegExp("\D+")
        text_validator = QRegExpValidator(reg_ex_text, self.editField1)
        self.editField1.setValidator(text_validator)

        reg_ex_num = QRegExp("[0-9]+.?")
        num_validator = QRegExpValidator(reg_ex_num, self.editField2)
        self.editField2.setValidator(num_validator)
        self.editField3.setValidator(num_validator)
        self.editField4.setValidator(num_validator)

        self.image = QLabel()
        icon = qta.icon("fa5s.camera", color='blue')
        self.image.setPixmap(icon.pixmap(QSize(24, 24)))
        self.imageName = QLabel(self.cells["photo"])
        self.saveButton = QPushButton("Save")
        self.cancelButton = QPushButton("Cancel")
        self.uploadImageButton = QPushButton("Upload new photo")

        self.__setLayouts()
        self.__setValues()
        self.saveButton.clicked.connect(self.__saveButtonClicked)
        self.cancelButton.clicked.connect(self.__cancelButtonClicked)
        self.uploadImageButton.clicked.connect(self.__uploadButtonClicked)
        self.ImagePath = self.cells["photo"]

    def __setLayouts(self):
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

    def __setValues(self):
        self.editField1.setText(self.cells["name"])
        self.editField2.setText(self.cells["year"])
        self.editField3.setText(self.cells["course"])
        self.editField4.setText(self.cells["group"])

    @pyqtSlot()
    def __saveButtonClicked(self):
        if self.editField1.text():
            string = ""
            if self.ImagePath:
                with open(self.ImagePath, "rb") as img:
                    string = base64.b64encode(img.read()).decode('utf-8')
            newData = {"id": self.row, "name": self.editField1.text(),
                       "year": self.editField2.text(), "photo": os.path.basename(self.ImagePath),
                       "course": self.editField3.text(), "group": self.editField4.text(),
                       "binary_photo": string}
            json_object = json.dumps(newData, indent=4)
            with open("save.json", "w") as outfile:
                outfile.write(json_object)
            infoMessageBox(title="Saving", message="Data was saved")
            self.signal.emit()
            print("emit save signal")
        else:
            QMessageBox.critical(
                None,
                "Error while saving",
                "Required field 'name'"
            )

    def __cancelButtonClicked(self):
        self.editField1.setText(self.cells["name"])
        self.editField2.setText(self.cells["year"])
        self.editField3.setText(self.cells["course"])
        self.editField4.setText(self.cells["group"])
        infoMessageBox(title="Cancel", message="Changes were canceled")

    def __uploadButtonClicked(self):
        image = QFileDialog.getOpenFileName(None, 'OpenFile', '', "Image file(*.jpg)")
        self.ImagePath = image[0]
        self.imageName.setText(self.ImagePath)
