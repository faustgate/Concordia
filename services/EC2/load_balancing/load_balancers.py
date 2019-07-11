from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import boto3

main_layout = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'load_balancers.ui'))[0]


class EC2LoadBalancers(QWidget, main_layout):

    def __init__(self, aws_creds, parent=None):
        super(EC2LoadBalancers, self).__init__(parent)
        self.aws_creds = aws_creds
        self.non_filterable_fields = ['AvailabilityZones', 'State',
                                      'SecurityGroups', 'CreatedTime']

        self.main_table_fields = ['LoadBalancerName', 'DNSName', 'Type',
                                  'VpcId', 'Scheme', 'CanonicalHostedZoneId',
                                  'LoadBalancerArn', 'IpAddressType']

        # self.layout = QHBoxLayout()
        self.setupUi(self)
        self.load_balancers_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'load_balancers_details.ui'))
        self.load_balancers_listeners_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'load_balancers_listeners.ui'))

        self.headers, self.load_balancers = self.get_ec2_load_balancers(aws_creds)

        self.fill_in_main_table()

        # self.tableView.setModel(tablemodel)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.horizontalHeader().setSectionsMovable(True)
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.itemSelectionChanged.connect(self.print_load_balancer_details)

        self.scrollAreaWidgetContents.setLayout(self.gridLayout_2)

        self.tabWidget.addTab(self.load_balancers_layout, "Description")
        self.tabWidget.addTab(self.load_balancers_listeners_layout, "Listeners")

        self.load_balancers_layout_height = 100

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

    def print_load_balancer_details(self):
        if len(self.tableWidget.selectedItems()) > 0:
            self.splitter.setSizes([self.splitter.sizes()[0], self.load_balancers_layout_height])
            selected_load_balancer = self.load_balancers[self.tableWidget.selectedItems()[0].row()]
            self.print_load_balancer_listeners(selected_load_balancer['LoadBalancerArn'])
            self.load_balancers_layout.load_balancerIdValue.setText(selected_load_balancer['LoadBalancerName'])
            # self.load_balancers_layout.load_balancerStateValue.setText(selected_load_balancer['State'])
        else:
            self.splitter.setSizes([self.splitter.sizes()[0], 0])
        # print(selected_row)

    def print_load_balancer_listeners(self, load_balancer_arn):
        client = boto3.client('elbv2',
                              aws_access_key_id=self.aws_creds['access_key'],
                              aws_secret_access_key=self.aws_creds['secret_key'],
                              region_name=self.aws_creds['region'])
        response = client.describe_listeners(LoadBalancerArn=load_balancer_arn)
        listeners_table_headers = ['ListenerArn', 'Protocol', 'Port', 'Default Actions']
        self.load_balancers_listeners_layout.tblListeners.setRowCount(len(response['Listeners']))
        self.load_balancers_listeners_layout.tblListeners.setColumnCount(len(listeners_table_headers))
        self.load_balancers_listeners_layout.tblListeners.setHorizontalHeaderLabels(listeners_table_headers)
        self.load_balancers_listeners_layout.tblListeners.horizontalHeader().setStretchLastSection(True)

        row_pointer = 0
        for listener in response['Listeners']:
            default_actions = []
            for default_action in listener['DefaultActions']:
                if default_action['Type'] == 'redirect':
                    action = 'redirect ({0}) to {1}://{2}:{3}/{4}?{5}'.format(
                        default_action['RedirectConfig']['StatusCode'].replace('HTTP_', ''),
                        default_action['RedirectConfig']['Protocol'],
                        default_action['RedirectConfig']['Host'],
                        default_action['RedirectConfig']['Port'],
                        default_action['RedirectConfig']['Path'],
                        default_action['RedirectConfig']['Query']).lower()
                elif default_action['Type'] == 'fixed-response':
                    action = 'return fixed response ({0}) ' \
                             'with message "{1}" and type "{2}"'.format(
                        default_action['FixedResponseConfig']['StatusCode'],
                        default_action['FixedResponseConfig']['MessageBody'],
                        default_action['FixedResponseConfig']['ContentType']
                    ).lower()
                elif default_action['Type'] == 'forward':
                    action = 'forward to {0}'.format(
                        default_action['TargetGroupArn']
                    ).lower()
                else:
                    action = 'Unknown (please post a bug)'
                default_actions.append(action)
            self.load_balancers_listeners_layout.tblListeners.setItem(row_pointer, 0, QTableWidgetItem(listener['ListenerArn']))
            self.load_balancers_listeners_layout.tblListeners.setItem(row_pointer, 1, QTableWidgetItem(str(listener['Port'])))
            self.load_balancers_listeners_layout.tblListeners.setItem(row_pointer, 2, QTableWidgetItem(listener['Protocol']))
            self.load_balancers_listeners_layout.tblListeners.setItem(row_pointer, 3, QTableWidgetItem('\n'.join(default_actions)))
            row_pointer += 1

    def fill_in_main_table(self):
        self.tableWidget.setRowCount(len(self.load_balancers))
        table_headers = self.get_table_headers()
        self.tableWidget.setColumnCount(len(table_headers))
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        row_pointer = 0
        for load_balancer in self.load_balancers:
            column_pointer = 0
            for header in table_headers:
                item_value = load_balancer[header] if header in load_balancer and header.strip() != '' else '-'
                self.tableWidget.setItem(row_pointer,
                                         column_pointer,
                                         QTableWidgetItem(str(item_value)))
                column_pointer += 1
            row_pointer += 1

    def get_ec2_load_balancers(self, aws_creds):
        load_balancers = []
        load_balancer_keys = set()
        client = boto3.client('elbv2',
                              aws_access_key_id=self.aws_creds['access_key'],
                              aws_secret_access_key=self.aws_creds['secret_key'],
                              region_name=self.aws_creds['region'])
        response = client.describe_load_balancers()
        for load_balancer in response['LoadBalancers']:
            load_balancer_keys.update(load_balancer.keys())
            load_balancers.append(load_balancer)
        return list(load_balancer_keys), load_balancers
