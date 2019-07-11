from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import boto3

main_layout = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'volumes.ui'))[0]


class EC2EBSVolumes(QWidget, main_layout):

    def __init__(self, aws_creds, parent=None):
        super(EC2EBSVolumes, self).__init__(parent)
        self.non_filterable_fields = ['Attachments', 'Tags', 'CreateTime']

        self.main_table_fields = ['VolumeId', 'AvailabilityZone', 'Encrypted',
                                  'Size', 'SnapshotId', 'State', 'Iops',
                                  'VolumeType']

        # self.layout = QHBoxLayout()
        self.setupUi(self)
        self.volumes_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'volumes_details.ui'))

        self.headers, self.volumes = self.get_ec2_ebs_volumes(aws_creds)

        self.fill_in_main_table()

        # self.tableView.setModel(tablemodel)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.horizontalHeader().setSectionsMovable(True)
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.itemSelectionChanged.connect(self.print_volume_details)

        self.scrollAreaWidgetContents.setLayout(self.gridLayout_2)

        self.tabWidget.addTab(self.volumes_layout, "Description")

        self.volumes_layout_height = 100

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

    def print_volume_details(self):
        if len(self.tableWidget.selectedItems()) > 0:
            self.splitter.setSizes([self.splitter.sizes()[0], self.volumes_layout_height])
            selected_volume = self.volumes[self.tableWidget.selectedItems()[0].row()]
            self.volumes_layout.volumeIdValue.setText(selected_volume['VolumeId'])
            self.volumes_layout.volumeStateValue.setText(selected_volume['State'])
        else:
            self.splitter.setSizes([self.splitter.sizes()[0], 0])
            # print(selected_row)

    def fill_in_main_table(self):
        self.tableWidget.setRowCount(len(self.volumes))
        table_headers = self.get_table_headers()
        self.tableWidget.setColumnCount(len(table_headers))
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        row_pointer = 0
        for volume in self.volumes:
            column_pointer = 0
            for header in table_headers:
                item_value = volume[header] if header in volume and header.strip() != '' else '-'
                self.tableWidget.setItem(row_pointer,
                                         column_pointer,
                                         QTableWidgetItem(str(item_value)))
                column_pointer += 1
            row_pointer += 1

    def get_ec2_ebs_volumes(self, aws_creds):
        volumes = []
        volume_keys = set()
        client = boto3.client('ec2',
                              aws_access_key_id=aws_creds['access_key'],
                              aws_secret_access_key=aws_creds['secret_key'],
                              region_name=aws_creds['region'])
        response = client.describe_volumes()
        for volume in response['Volumes']:
            volume_keys.update(volume.keys())
            volumes.append(volume)
        return list(volume_keys), volumes
