from PyQt5 import uic
from PyQt5.QtWidgets import *
import os
import boto3
from concordia_resources_table import ResourcesTable


class EC2LoadBalancers(ResourcesTable):
    def __init__(self, aws_creds, statusbar=None, parent=None):
        super(EC2LoadBalancers, self).__init__(statusbar, parent)

        self.client = boto3.client('elbv2',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])

        self.set_hidden_fields(['AvailabilityZones', 'State',
                                'SecurityGroups', 'CreatedTime'])

        self.set_main_table_fields(['LoadBalancerName', 'DNSName', 'Type',
                                  'VpcId', 'Scheme', 'CanonicalHostedZoneId',
                                  'LoadBalancerArn', 'IpAddressType'])

        self.set_details_layout(os.path.join(os.path.dirname(__file__), 'load_balancers_details.ui'))
        self.load_balancers_listeners_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'load_balancers_listeners.ui'))
        self.tabWidget.addTab(self.load_balancers_listeners_layout, "Listeners")

    def print_resource_details(self):
        self.print_load_balancer_listeners(self.selected_resource['LoadBalancerArn'])
        self.details_layout.load_balancerIdValue.setText(self.selected_resource['LoadBalancerName'])

    def print_load_balancer_listeners(self, load_balancer_arn):
        response = self.client.describe_listeners(LoadBalancerArn=load_balancer_arn)
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

    def get_aws_resources(self):
        response = self.client.describe_load_balancers()
        self.set_resources_data(response['LoadBalancers'], 'LoadBalancerArn')
