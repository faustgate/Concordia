from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import boto3

main_layout = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'key_pairs.ui'))[0]


class EC2KeyPairs(QWidget, main_layout):

    def __init__(self, aws_creds, parent=None):
        super(EC2KeyPairs, self).__init__(parent)
        self.non_filterable_fields = ['Attachments', 'Tags', 'CreateTime']

        self.main_table_fields = ['KeyName', 'KeyFingerprint']

        # self.layout = QHBoxLayout()
        self.setupUi(self)
        self.key_pairs_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'key_pairs_details.ui'))

        self.headers, self.key_pairs = self.get_ec2_ebs_key_pairs(aws_creds)

        self.fill_in_main_table()

        # self.tableView.setModel(tablemodel)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.horizontalHeader().setSectionsMovable(True)
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.itemSelectionChanged.connect(self.print_key_pair_details)

        self.scrollAreaWidgetContents.setLayout(self.gridLayout_2)

        self.tabWidget.addTab(self.key_pairs_layout, "Description")

        self.key_pairs_layout_height = 100

        # tbw = QLabel()
        # tbw.setText()

        # self.layout.addWidget(self.tableView)
        # self.setLayout(self.layout)

    def get_table_headers(self):
        headers = []
        for header in self.headers:
            if header not in self.main_table_fields:
                self.main_table_fields.append(header)

        for header in self.main_table_fields:
            if header not in self.non_filterable_fields:
                headers.append(header)
        return headers

    def print_key_pair_details(self):
        if len(self.tableWidget.selectedItems()) > 0:
            self.splitter.setSizes([self.splitter.sizes()[0], self.key_pairs_layout_height])
            selected_key_pair = self.key_pairs[self.tableWidget.selectedItems()[0].row()]
            self.key_pairs_layout.key_pairIdValue.setText(selected_key_pair['KeyName'])
            self.key_pairs_layout.key_pairStateValue.setText(selected_key_pair['KeyFingerprint'])
            # print(selected_row)
        else:
            self.splitter.setSizes([self.splitter.sizes()[0], 0])

    def fill_in_main_table(self):
        self.tableWidget.setRowCount(len(self.key_pairs))
        table_headers = self.get_table_headers()
        self.tableWidget.setColumnCount(len(table_headers))
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        row_pointer = 0
        for key_pair in self.key_pairs:
            column_pointer = 0
            for header in table_headers:
                item_value = key_pair[header] if header in key_pair and header.strip() != '' else '-'
                self.tableWidget.setItem(row_pointer,
                                         column_pointer,
                                         QTableWidgetItem(str(item_value)))
                column_pointer += 1
            row_pointer += 1

    def get_ec2_ebs_key_pairs(self, aws_creds):
        key_pairs = []
        key_pair_keys = set()
        client = boto3.client('ec2',
                              aws_access_key_id=aws_creds['access_key'],
                              aws_secret_access_key=aws_creds['secret_key'],
                              region_name=aws_creds['region'])
        response = client.describe_key_pairs()
        for key_pair in response['KeyPairs']:
            key_pair_keys.update(key_pair.keys())
            key_pairs.append(key_pair)
        return list(key_pair_keys), key_pairs
