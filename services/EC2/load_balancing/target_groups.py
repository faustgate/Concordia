from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import boto3

main_layout = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'target_groups.ui'))[0]


class EC2LoadBalancersTargetGroups(QWidget, main_layout):

    def __init__(self, aws_creds, parent=None):
        super(EC2LoadBalancersTargetGroups, self).__init__(parent)
        self.aws_creds = aws_creds
        self.non_filterable_fields = ['Matcher', 'LoadBalancersArns']

        self.main_table_fields = ['TargetGroupName', 'TargetType', 'Protocol',
                                  'Port', 'HealthCheckEnabled',
                                  'HealthCheckProtocol', 'HealthCheckPort',
                                  'HealthCheckPath',
                                  'HealthCheckIntervalSeconds',
                                  'HealthCheckTimeoutSeconds',
                                  'HealthyThresholdCount',
                                  'UnhealthyThresholdCount', 'VpcId',
                                  'TargetGroupArn']

        # self.layout = QHBoxLayout()
        self.setupUi(self)
        self.target_groups_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'target_groups_details.ui'))
        self.target_groups_targets_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'target_groups_targets.ui'))

        self.headers, self.target_groups = self.get_ec2_target_groups()

        self.fill_in_main_table()

        # self.tableView.setModel(tablemodel)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.horizontalHeader().setSectionsMovable(True)
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.itemSelectionChanged.connect(self.print_target_group_details)

        self.scrollAreaWidgetContents.setLayout(self.gridLayout_2)

        self.tabWidget.addTab(self.target_groups_layout, "Description")
        self.tabWidget.addTab(self.target_groups_targets_layout, "Targets")

        self.target_groups_layout_height = 100

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

    def print_target_group_details(self):
        if len(self.tableWidget.selectedItems()) > 0:
            self.splitter.setSizes([self.splitter.sizes()[0], self.target_groups_layout_height])
            selected_target_group = self.target_groups[self.tableWidget.selectedItems()[0].row()]
            self.print_target_group_targets(selected_target_group['TargetGroupArn'])
            self.target_groups_layout.target_groupIdValue.setText(selected_target_group['TargetGroupArn'])
            # self.target_groups_layout.target_groupStateValue.setText(selected_target_group['State'])
        else:
            self.splitter.setSizes([self.splitter.sizes()[0], 0])
        # print(selected_row)

    def print_target_group_targets(self, target_group_arn):
        client = boto3.client('elbv2',
                              aws_access_key_id=self.aws_creds['access_key'],
                              aws_secret_access_key=self.aws_creds['secret_key'],
                              region_name=self.aws_creds['region'])
        response = client.describe_target_health(TargetGroupArn=target_group_arn)
        targets_table_headers = ['Instance ID', 'Instance Port', 
                                   'Health Check Port', 'Status', 
                                   'Status Reason']
        self.target_groups_targets_layout.tblTargets.setRowCount(len(response['TargetHealthDescriptions']))
        self.target_groups_targets_layout.tblTargets.setColumnCount(len(targets_table_headers))
        self.target_groups_targets_layout.tblTargets.setHorizontalHeaderLabels(targets_table_headers)
        self.target_groups_targets_layout.tblTargets.horizontalHeader().setStretchLastSection(True)
        self.target_groups_targets_layout.tblTargets.resizeColumnsToContents()

        row_pointer = 0
        for target in response['TargetHealthDescriptions']:
            self.target_groups_targets_layout.tblTargets.setItem(row_pointer, 0, QTableWidgetItem(target['Target']['Id']))
            self.target_groups_targets_layout.tblTargets.setItem(row_pointer, 1, QTableWidgetItem(str(target['Target']['Port'])))
            self.target_groups_targets_layout.tblTargets.setItem(row_pointer, 2, QTableWidgetItem(target['HealthCheckPort']))
            self.target_groups_targets_layout.tblTargets.setItem(row_pointer, 3, QTableWidgetItem(target['TargetHealth']['State']))
            if 'Description' in target['TargetHealth']:
                self.target_groups_targets_layout.tblTargets.setItem(row_pointer, 4, QTableWidgetItem(target['TargetHealth']['Description']))
            else:
                self.target_groups_targets_layout.tblTargets.setItem(row_pointer, 4, QTableWidgetItem('-'))
            row_pointer += 1
        self.target_groups_targets_layout.tblTargets.resizeColumnsToContents()

    def fill_in_main_table(self):
        self.tableWidget.setRowCount(len(self.target_groups))
        table_headers = self.get_table_headers()
        self.tableWidget.setColumnCount(len(table_headers))
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        row_pointer = 0
        for target_group in self.target_groups:
            column_pointer = 0
            for header in table_headers:
                item_value = target_group[header] if header in target_group and header.strip() != '' else '-'
                self.tableWidget.setItem(row_pointer,
                                         column_pointer,
                                         QTableWidgetItem(str(item_value)))
                column_pointer += 1
            row_pointer += 1

    def get_ec2_target_groups(self):
        target_groups = []
        target_group_keys = set()
        client = boto3.client('elbv2',
                              aws_access_key_id=self.aws_creds['access_key'],
                              aws_secret_access_key=self.aws_creds['secret_key'],
                              region_name=self.aws_creds['region'])
        response = client.describe_target_groups()
        for target_group in response['TargetGroups']:
            target_group_keys.update(target_group.keys())
            target_groups.append(target_group)
        return list(target_group_keys), target_groups
