from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import boto3

main_layout = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'amis.ui'))[0]


class EC2AMIs(QWidget, main_layout):

    def __init__(self, aws_creds, parent=None):
        super(EC2AMIs, self).__init__(parent)
        self.non_filterable_fields = ['BlockDeviceMappings', 'Tags']

        self.main_table_fields = ['Name', 'ImageId', 'State', 'ImageLocation',
                                  'Hypervisor', 'Description', 'RootDeviceName',
                                  'VirtualizationType', 'Tags', 'Architecture',
                                  'ImageType', 'Public', 'BlockDeviceMappings',
                                  'EnaSupport', 'RootDeviceType', 'OwnerId',
                                  'CreationDate', 'SriovNetSupport']

        # self.layout = QHBoxLayout()
        self.setupUi(self)
        self.images_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'details.ui'))

        self.headers, self.images = self.get_ec2_images(aws_creds)

        self.fill_in_main_table()

        # self.tableView.setModel(tablemodel)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.horizontalHeader().setSectionsMovable(True)
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.itemClicked.connect(self.print_image_details)

        self.scrollAreaWidgetContents.setLayout(self.gridLayout_2)

        self.tabWidget.addTab(self.images_layout, "Description")

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

    def print_image_details(self):
        selected_image = self.images[self.tableWidget.selectedItems()[0].row()]
        self.images_layout.imageIdValue.setText(selected_image['ImageId'])
        self.images_layout.imageStateValue.setText( selected_image['State'])
        # print(selected_row)

    def fill_in_main_table(self):
        self.tableWidget.setRowCount(len(self.images))
        table_headers = self.get_table_headers()
        self.tableWidget.setColumnCount(len(table_headers))
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        row_pointer = 0
        for image in self.images:
            column_pointer = 0
            for header in table_headers:
                item_value = image[header] if header in image and header.strip() != '' else '-'
                self.tableWidget.setItem(row_pointer,
                                         column_pointer,
                                         QTableWidgetItem(item_value))
                column_pointer += 1
            row_pointer += 1

    def get_ec2_images(self, aws_creds):
        images = []
        image_keys = set()
        client = boto3.client('ec2',
                              aws_access_key_id=aws_creds['access_key'],
                              aws_secret_access_key=aws_creds['secret_key'],
                              region_name=aws_creds['region'])
        response = client.describe_images(Filters=[
            {
                'Name': 'is-public',
                'Values': [
                    'false',
                ]
            },
        ])
        for image in response['Images']:
            if 'StateReason' in image:
                image['StateReason'] = image['StateReason']['Message']
            image_keys.update(image.keys())
            images.append(image)
        return list(image_keys), images
