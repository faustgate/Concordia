from PyQt5 import uic
from PyQt5.QtWidgets import *
import os
import boto3
from concordia_resources_table import ResourcesTable


class EC2SecurityGroups(ResourcesTable):
    def __init__(self, aws_creds, statusbar=None, parent=None):
        super(EC2SecurityGroups, self).__init__(statusbar, parent)
        self.client = boto3.client('ec2',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])
        self.set_hidden_fields(['Attachments', 'Tags', 'CreateTime',
                                'IpPermissions', 'IpPermissionsEgress'])

        self.set_main_table_fields(['GroupId', 'GroupName',
                                    'Description', 'VpcId', 'OwnerId'])

        self.set_details_layout(os.path.join(os.path.dirname(__file__), 'security_groups_details.ui'))

        self.security_groups_inbound = uic.loadUi(os.path.join(os.path.dirname(__file__), 'security_groups_inbound.ui'))
        self.security_groups_outbound = uic.loadUi(os.path.join(os.path.dirname(__file__), 'security_groups_outbound.ui'))
        self.tabWidget.addTab(self.security_groups_inbound, "Inbound")
        self.tabWidget.addTab(self.security_groups_outbound, "Outbound")

    def print_resource_details(self):
        self.details_layout.securityGroupIdValue.setText(self.selected_resource['GroupId'])
        self.print_sg_rules(self.selected_resource['IpPermissions'], self.security_groups_inbound.tblInboundRules)
        self.print_sg_rules(self.selected_resource['IpPermissionsEgress'], self.security_groups_outbound.tblOutboundRules)
       
    def print_sg_rules(self, rule_set, out_widget):
        rules_table_headers = ['Protocol', 'Port Range', 'Source']
        out_widget.setRowCount(len(rule_set))
        out_widget.setColumnCount(len(rules_table_headers))
        out_widget.setHorizontalHeaderLabels(rules_table_headers)
        out_widget.horizontalHeader().setStretchLastSection(True)
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

    def get_aws_resources(self):
        response = self.client.describe_security_groups()
        self.set_resources_data(response['SecurityGroups'], 'GroupId')
