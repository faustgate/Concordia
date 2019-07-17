from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import boto3

main_layout = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'launch_configurations.ui'))[0]


class EC2LaunchConfigurations(QWidget, main_layout):

    def __init__(self, aws_creds, parent=None):
        super(EC2LaunchConfigurations, self).__init__(parent)
        self.aws_creds = aws_creds
        self.non_filterable_fields = ['ClassicLinkVPCSecurityGroups', 'BlockDeviceMappings',
                                      'SecurityGroups', 'InstanceMonitoring',
                                      'CreatedTime']

        self.main_table_fields = ['LaunchConfigurationName', 'ImageId',
                                  'InstanceType', 'KeyName', 'EbsOptimized',
                                  'LaunchConfigurationArn', 'IpAddressType']

        # self.layout = QHBoxLayout()
        self.setupUi(self)
        self.launch_configurations_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'launch_configurations_details.ui'))
        # self.launch_configurations_listeners_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'launch_configurations_listeners.ui'))

        self.headers, self.launch_configurations = self.get_ec2_launch_configurations(aws_creds)

        self.fill_in_main_table()

        # self.tableView.setModel(tablemodel)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.horizontalHeader().setSectionsMovable(True)
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.itemSelectionChanged.connect(self.print_launch_configuration_details)

        self.scrollAreaWidgetContents.setLayout(self.gridLayout_2)

        self.tabWidget.addTab(self.launch_configurations_layout, "Description")
        # self.tabWidget.addTab(self.launch_configurations_listeners_layout, "Listeners")

        self.launch_configurations_layout_height = 100

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

    def print_launch_configuration_details(self):
        if len(self.tableWidget.selectedItems()) > 0:
            self.splitter.setSizes([self.splitter.sizes()[0], self.launch_configurations_layout_height])
            selected_launch_configuration = self.launch_configurations[self.tableWidget.selectedItems()[0].row()]
            self.launch_configurations_layout.launch_configurationIdValue.setText(selected_launch_configuration['LaunchConfigurationName'])
            # self.launch_configurations_layout.launch_configurationStateValue.setText(selected_launch_configuration['State'])
        else:
            self.splitter.setSizes([self.splitter.sizes()[0], 0])
        # print(selected_row)

    def fill_in_main_table(self):
        self.tableWidget.setRowCount(len(self.launch_configurations))
        table_headers = self.get_table_headers()
        self.tableWidget.setColumnCount(len(table_headers))
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        row_pointer = 0
        for launch_configuration in self.launch_configurations:
            column_pointer = 0
            for header in table_headers:
                item_value = launch_configuration[header] if header in launch_configuration and header.strip() != '' else '-'
                self.tableWidget.setItem(row_pointer,
                                         column_pointer,
                                         QTableWidgetItem(str(item_value)))
                column_pointer += 1
            row_pointer += 1

    def get_ec2_launch_configurations(self, aws_creds):
        launch_configurations = []
        launch_configuration_keys = set()
        client = boto3.client('autoscaling',
                              aws_access_key_id=self.aws_creds['access_key'],
                              aws_secret_access_key=self.aws_creds['secret_key'],
                              region_name=self.aws_creds['region'])
        response = client.describe_launch_configurations()
        for launch_configuration in response['LaunchConfigurations']:
            launch_configuration_keys.update(launch_configuration.keys())
            launch_configurations.append(launch_configuration)
        return list(launch_configuration_keys), launch_configurations
