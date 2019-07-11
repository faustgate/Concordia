from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import boto3

main_layout = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'security_groups.ui'))[0]


class EC2SecurityGroups(QWidget, main_layout):

    def __init__(self, aws_creds, parent=None):
        super(EC2SecurityGroups, self).__init__(parent)
        self.non_filterable_fields = ['Attachments', 'Tags', 'CreateTime',
                                      'IpPermissions', 'IpPermissionsEgress']

        self.main_table_fields = ['GroupId', 'GroupName', 'Description', 'VpcId',
                                  'OwnerId']

        # self.layout = QHBoxLayout()
        self.setupUi(self)
        self.security_groups_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'security_groups_details.ui'))
        self.security_groups_inbound = uic.loadUi(os.path.join(os.path.dirname(__file__), 'security_groups_inbound.ui'))
        self.security_groups_outbound = uic.loadUi(os.path.join(os.path.dirname(__file__), 'security_groups_outbound.ui'))
        self.security_groups_inbound.tblInboundRules.horizontalHeader().setStretchLastSection(True)
        self.security_groups_inbound.tblInboundRules.horizontalHeader().setStretchLastSection(True)

        self.headers, self.security_groups = self.get_ec2_security_groups(aws_creds)

        self.fill_in_main_table()

        # self.tableView.setModel(tablemodel)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.horizontalHeader().setSectionsMovable(True)
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.itemSelectionChanged.connect(self.print_security_group_details)

        self.scrollAreaWidgetContents.setLayout(self.gridLayout_2)

        self.tabWidget.addTab(self.security_groups_layout, "Description")
        self.tabWidget.addTab(self.security_groups_inbound, "Inbound")
        self.tabWidget.addTab(self.security_groups_outbound, "Outbound")
        #self.tabWidget.addTab(self.security_groups_layout, "Tags")

        self.security_groups_layout_height = 300

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

    def print_security_group_details(self):
        if len(self.tableWidget.selectedItems()) > 0:
            self.splitter.setSizes([self.splitter.sizes()[0], self.security_groups_layout_height])
            selected_security_group = self.security_groups[self.tableWidget.selectedItems()[0].row()]
            self.security_groups_layout.securityGroupIdValue.setText(selected_security_group['GroupId'])
            self.print_sg_rules(selected_security_group['IpPermissions'], self.security_groups_inbound.tblInboundRules)
            self.print_sg_rules(selected_security_group['IpPermissionsEgress'], self.security_groups_outbound.tblOutboundRules)
        else:
            self.splitter.setSizes([self.splitter.sizes()[0], 0])

    def print_sg_rules(self, rule_set, out_widget):
        rules_table_headers = ['Protocol', 'Port Range', 'Source']
        out_widget.setRowCount(len(rule_set))
        out_widget.setColumnCount(len(rules_table_headers))
        out_widget.setHorizontalHeaderLabels(rules_table_headers)
        row_pointer = 0
        for rule in rule_set:
            if rule['IpProtocol'] == '-1':
                out_widget.setItem(row_pointer, 0, QTableWidgetItem('All'))
                out_widget.setItem(row_pointer, 1, QTableWidgetItem('All'))
            else:
                out_widget.setItem(row_pointer, 0, QTableWidgetItem(rule['IpProtocol']))
                if rule['FromPort'] == rule['ToPort']:
                    out_widget.setItem(row_pointer, 1, QTableWidgetItem(str(rule['FromPort'])))
                else:
                    out_widget.setItem(row_pointer, 1, QTableWidgetItem('{0} - {1}'.format(rule['FromPort'], rule['ToPort'])))

            if len(rule['IpRanges']) > 0:
                allowed_cidrs = []
                for cidr in rule['IpRanges']:
                    allowed_cidrs.append(cidr['CidrIp'])
                out_widget.setItem(row_pointer, 2, QTableWidgetItem(','.join(allowed_cidrs)))
            elif len(rule['Ipv6Ranges']) > 0:
                allowed_v6cidrs = []
                for cidr in rule['Ipv6Ranges']:
                    allowed_v6cidrs.append(cidr['CidrIpv6'])
                out_widget.setItem(row_pointer, 2, QTableWidgetItem(','.join(allowed_v6cidrs)))
            else:
                allowed_sgs = []
                for sg in rule['UserIdGroupPairs']:
                    allowed_sgs.append(sg['GroupId'])
                out_widget.setItem(row_pointer, 2, QTableWidgetItem(','.join(allowed_sgs)))
            row_pointer += 1

    def fill_in_main_table(self):
        self.tableWidget.setRowCount(len(self.security_groups))
        table_headers = self.get_table_headers()
        self.tableWidget.setColumnCount(len(table_headers))
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        row_pointer = 0
        for security_group in self.security_groups:
            column_pointer = 0
            for header in table_headers:
                item_value = security_group[header] if header in security_group and header.strip() != '' else '-'
                self.tableWidget.setItem(row_pointer,
                                         column_pointer,
                                         QTableWidgetItem(str(item_value)))
                column_pointer += 1
            row_pointer += 1

    def get_ec2_security_groups(self, aws_creds):
        security_groups = []
        security_group_keys = set()
        client = boto3.client('ec2',
                              aws_access_key_id=aws_creds['access_key'],
                              aws_secret_access_key=aws_creds['secret_key'],
                              region_name=aws_creds['region'])
        response = client.describe_security_groups()
        for security_group in response['SecurityGroups']:
            security_group_keys.update(security_group.keys())
            security_groups.append(security_group)
        return list(security_group_keys), security_groups
