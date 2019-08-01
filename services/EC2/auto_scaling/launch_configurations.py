import os
import boto3
from concordia_resources_table import ResourcesTable


class EC2LaunchConfigurations(ResourcesTable):
    def __init__(self, aws_creds, statusbar=None, parent=None):
        super(EC2LaunchConfigurations, self).__init__(statusbar, parent)

        self.client = boto3.client('autoscaling',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])
        self.set_hidden_fields(['ClassicLinkVPCSecurityGroups', 'BlockDeviceMappings',
                                      'SecurityGroups', 'InstanceMonitoring',
                                      'CreatedTime'])

        self.set_main_table_fields(['LaunchConfigurationName', 'ImageId',
                                  'InstanceType', 'KeyName', 'EbsOptimized',
                                  'LaunchConfigurationARN', 'IpAddressType'])

        self.set_details_layout(os.path.join(os.path.dirname(__file__), 'launch_configurations_details.ui'))

    def print_resource_details(self):
        self.details_layout.launch_configurationIdValue.setText(self.selected_resource['LaunchConfigurationName'])

    def get_aws_resources(self):
        response = self.client.describe_launch_configurations()
        self.set_resources_data(response['LaunchConfigurations'], 'LaunchConfigurationARN')
