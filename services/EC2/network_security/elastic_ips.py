from PyQt5 import uic
import os
import boto3
from concordia_resources_table import ResourcesTable


class EC2ElasticIPs(ResourcesTable):
    def __init__(self, aws_creds, statusbar=None, parent=None):
        super(EC2ElasticIPs, self).__init__(statusbar, parent)

        self.client = boto3.client('ec2',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])

        self.set_hidden_fields(['Attachments', 'Tags', 'CreateTime',
                                'IpPermissions', 'IpPermissionsEgress'])

        self.set_main_table_fields(['PublicIp', 'AllocationId', 'AssociationId',
                                    'InstanceId', 'Domain', 'NetworkInterfaceId',
                                    'NetworkInterfaceOwnerId', 'PrivateIpAddress',
                                    'PublicIpv4Pool'])

        self.set_details_layout(os.path.join(os.path.dirname(__file__), 'elastic_ips_details.ui'))

        self.refresh_main_table()

    def print_resource_details(self):
        self.details_layout.securityGroupIdValue.setText(self.selected_resource['AllocationId'])
        
    def get_aws_resources(self):
        elastic_ips = []
        response = self.client.describe_addresses()
        for elastic_ip in response['Addresses']:
            self.resources_data_keys.update(elastic_ip.keys())
            elastic_ips.append(elastic_ip)
        self.set_resources_data(elastic_ips, 'AllocationId')
