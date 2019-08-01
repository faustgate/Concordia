import sys

import utils
from PySide2.QtWidgets import *

import os
import json
import boto3

from concordia_aws_credentials import ConcordiaAWSCredentials

dialog_creds_manager_layout = utils.loadUiType("ui/creds_manager.ui")[0]


class ConcordiaAWSCredentialsManager(QDialog, dialog_creds_manager_layout):
    def __init__(self, parent=None):
        super(ConcordiaAWSCredentialsManager, self).__init__(parent)
        self.setupUi(self)

        self.creds_dialog = ConcordiaAWSCredentials()

        self.buttons.accepted.connect(self.on_ok_button)
        self.buttons.rejected.connect(self.on_cancel_button)

        self.aws_creds = []
        self.load_saved_creds()

        self.btnAdd.clicked.connect(self.add_creds)
        self.btnDelete.clicked.connect(self.delete_creds)

        # self.dialogShown = QtCore.pyqtSignal()
        # self.dialogShown.connect(self.load_saved_creds)

    def showEvent(self, event):
        super(QDialog, self).showEvent(event)
        self.load_saved_creds()

    def on_ok_button(self):
        was_error = False
        for row in range(self.tableWidget.rowCount()):
            cur_creds = {'name': self.tableWidget.item(row, 0).text(),
                         'access_key': self.tableWidget.item(row, 1).text(),
                         'secret_key': self.tableWidget.item(row, 2).text(),
                         'region': self.tableWidget.item(row, 3).text()}
            try:
                client = boto3.client('ec2',
                                      aws_access_key_id=cur_creds['access_key'],
                                      aws_secret_access_key=cur_creds['secret_key'],
                                      region_name=cur_creds['region'])
                regions_list = client.describe_regions()
                self.aws_creds[row] = cur_creds
            except Exception:
                self.show_message("Could not use provided credentials ({}), "
                                  "please check.".format(cur_creds['name']))
                was_error = True
        if not was_error:
            self.save_creds()
            self.close()

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

    def load_saved_creds(self):
        self.aws_creds = self.creds_dialog.get_saved_creds()
        self.tableWidget.setRowCount(len(self.aws_creds))
        table_headers = ["Name", "Access Key", "Secret Key", "Default Region"]
        self.tableWidget.setColumnCount(len(table_headers))
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        row_pointer = 0
        for cred in self.aws_creds:
            self.tableWidget.setItem(row_pointer, 0, QTableWidgetItem(cred['name']))
            self.tableWidget.setItem(row_pointer, 1, QTableWidgetItem(cred['access_key']))
            self.tableWidget.setItem(row_pointer, 2, QTableWidgetItem(cred['secret_key']))
            self.tableWidget.setItem(row_pointer, 3, QTableWidgetItem(cred['region']))
            row_pointer += 1

    def add_creds(self):
        self.creds_dialog.exec_()
        self.load_saved_creds()

    def delete_creds(self):
        selected_rows = set()
        if len(self.tableWidget.selectedItems()) > 0:
            selected_creds = self.tableWidget.selectedItems()
            for creds in selected_creds:
                selected_rows.add(creds.row())
        for row_num in selected_rows:
            self.aws_creds.pop(row_num)
        self.save_creds()
        self.load_saved_creds()

    def save_creds(self):
        try:
            if not os.path.exists(os.path.expanduser('~/.concordia')):
                os.makedirs(os.path.expanduser('~/.concordia'))

            with open(os.path.join(os.path.expanduser('~/.concordia'),
                                   'credentials.json'), 'w') as creds_file:
                json.dump(self.aws_creds, creds_file)
        except FileNotFoundError:
            return []
