import sys
import utils
from PyQt5.QtWidgets import *

from PyQt5 import uic
import os
import json
import curses
import boto3


dialog_creds_layout = uic.loadUiType("ui/creds.ui")[0]


class ConcordiaAWSCredentials(QDialog, dialog_creds_layout):
    def __init__(self, parent=None):
        super(QDialog, self).__init__(parent)
        self.setupUi(self)

        self.buttons.accepted.connect(self.on_ok_button)
        self.buttons.rejected.connect(self.on_cancel_button)

        self.aws_creds = self.get_saved_creds()

    def on_ok_button(self):
        if self.name_edit.text() != '' and self.access_key_edit.text() != '' and self.secret_key_edit.text() != '':
            try:
                client = boto3.client('ec2',
                                      aws_access_key_id=self.access_key_edit.text(),
                                      aws_secret_access_key=self.secret_key_edit.text(),
                                      region_name=self.default_region_edit.text())
                regions_list = client.describe_regions()
                self.aws_creds.append({'name': self.name_edit.text(),
                                       'access_key': self.access_key_edit.text(),
                                       'secret_key': self.secret_key_edit.text(),
                                       'region': self.default_region_edit.text()})
                self.save_creds()
                self.close()
            except Exception:
                self.show_message("Could not check provided credentials, "
                                  "please check.")

    def on_cancel_button(self):
        self.close()

    def show_message(self, message_text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(message_text)
        msg.setWindowTitle("Attention!")
        # msg.setDetailedText("The details are as follows:")

        msg.setStandardButtons(QMessageBox.Ok)

        # msg.buttonClicked.connect(msgbtn)
        msg.exec_()

    def get_saved_creds(self):
        try:
            with open(os.path.join(os.path.expanduser('~/.concordia'),
                                   'credentials.json'), 'r') as creds_file:
                return json.load(creds_file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            return []

    def save_creds(self):
        try:
            if not os.path.exists(os.path.expanduser('~/.concordia')):
                os.makedirs(os.path.expanduser('~/.concordia'))

            with open(os.path.join(os.path.expanduser('~/.concordia'),
                                   'credentials.json'), 'w') as creds_file:
                json.dump(self.aws_creds, creds_file)
        except FileNotFoundError:
            return []
