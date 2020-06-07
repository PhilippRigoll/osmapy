# -*- coding: utf-8 -*-

import lxml.etree as ET
from PySide2.QtWidgets import QDialog, QGridLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QMessageBox

from osmapy.utils.config import config


class ChangesetForm(QDialog):
    def __init__(self, parent):
        super(ChangesetForm, self).__init__()
        self.parent = parent

        self.status_codes = {200: "Success",
                             400: "Bad request",
                             401: "Login was unsuccessful",
                             404: "Not found",
                             403: "User has been blocked",
                             405: "Method Not Allowed",
                             409: "Conflict"}

    def show(self):
        # reset layout
        QDialog().setLayout(self.layout())

        osm_change = ET.tostring(self.parent.changeset.create_osmChange(-1), pretty_print=True).decode()

        self.setWindowTitle("Upload changes")

        label1 = QLabel("osmChange file:")
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(osm_change)

        label2 = QLabel("Comment:")
        self.comment = QLineEdit()

        label3 = QLabel("Username:")
        self.username = QLineEdit()

        label4 = QLabel("Password:")
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)

        button = QPushButton("Submit Changes")

        layout = QGridLayout()
        layout.addWidget(label1, 0, 0, 1, 2)
        layout.addWidget(text, 1, 0, 1, 2)
        layout.addWidget(label2, 2, 0, 1, 1)
        layout.addWidget(self.comment, 2, 1, 1, 1)
        layout.addWidget(label3, 3, 0, 1, 1)
        layout.addWidget(self.username, 3, 1, 1, 1)
        layout.addWidget(label4, 4, 0, 1, 1)
        layout.addWidget(self.password, 4, 1, 1, 1)
        layout.addWidget(button, 5, 0, 1, 2)
        self.setLayout(layout)

        if "login_name" in config:
            self.username.setText(config.login_name)
        if "password" in config:
            self.password.setText(config.password)

        button.clicked.connect(self.click)
        super().show()

    def click(self):
        if self.username.text() == "":
            box = QMessageBox()
            box.setText("Please enter your username!")
            box.setIcon(QMessageBox.Icon.Warning)
            box.exec()
            return
        if self.password.text() == "":
            box = QMessageBox()
            box.setText("Please enter your password!")
            box.setIcon(QMessageBox.Icon.Warning)
            box.exec()
            return
        if self.comment.text() == "":
            box = QMessageBox()
            box.setText("Please enter a comment!")
            box.setIcon(QMessageBox.Icon.Warning)
            box.exec()
            return

        status_codes = self.parent.changeset.submit(self.comment.text(), self.username.text(), self.password.text())

        self.parent.viewer.load_elements()
        self.hide()

        if status_codes == 200:
            box = QMessageBox()
            box.setWindowTitle("Success")
            box.setText("Successfully uploaded changes!")
            box.setIcon(QMessageBox.Icon.Information)
            box.exec()
        else:
            box = QMessageBox()
            box.setWindowTitle("ERROR")
            box.setText(f"Error:\n{self.status_codes[status_codes]}")
            box.setIcon(QMessageBox.Icon.Critical)
            box.exec()


