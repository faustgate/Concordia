from PyQt5 import uic
from PyQt5.QtWidgets import *
import os
import boto3
from concordia_resources_table import ResourcesTable


class EC2LoadBalancersTargetGroups(ResourcesTable):
    def __init__(self, aws_creds, statusbar=None, parent=None):
        super(EC2LoadBalancersTargetGroups, self).__init__(statusbar, parent)

        self.client = boto3.client('elbv2',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])
        self.set_hidden_fields(['Matcher', 'LoadBalancersArns'])

        self.set_main_table_fields(['TargetGroupName', 'TargetType',
                                    'Protocol', 'Port', 'HealthCheckEnabled',
                                    'HealthCheckProtocol', 'HealthCheckPort',
                                    'HealthCheckPath',
                                    'HealthCheckIntervalSeconds',
                                    'HealthCheckTimeoutSeconds',
                                    'HealthyThresholdCount',
                                    'UnhealthyThresholdCount', 'VpcId',
                                    'TargetGroupArn'])

        self.set_details_layout(os.path.join(os.path.dirname(__file__), 'target_groups_details.ui'))
        self.target_groups_targets_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'target_groups_targets.ui'))
        self.tabWidget.addTab(self.target_groups_targets_layout, "Targets")

    def print_resource_details(self):
        self.print_target_group_targets(self.selected_resource['TargetGroupArn'])
        self.details_layout.target_groupIdValue.setText(self.selected_resource['TargetGroupArn'])
           
    def print_target_group_targets(self, target_group_arn):
        response = self.client.describe_target_health(TargetGroupArn=target_group_arn)
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

    def get_aws_resources(self):
        response = self.client.describe_target_groups()
        self.set_resources_data(response['TargetGroups'], 'TargetGroupArn')
