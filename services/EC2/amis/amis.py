import os
import boto3
from concordia_resources_table import ResourcesTable


class EC2AMIs(ResourcesTable):
    def __init__(self, aws_creds, statusbar=None, parent=None):
        super(EC2AMIs, self).__init__(statusbar, parent)

        self.client = boto3.client('ec2',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])

        self.set_hidden_fields(['BlockDeviceMappings', 'Tags'])

        self.set_main_table_fields(['Name', 'ImageId', 'State', 'ImageLocation',
                                    'Hypervisor', 'Description', 'RootDeviceName',
                                    'VirtualizationType', 'Tags', 'Architecture',
                                    'ImageType', 'Public', 'BlockDeviceMappings',
                                    'EnaSupport', 'RootDeviceType', 'OwnerId',
                                    'CreationDate', 'SriovNetSupport'])

        self.set_details_layout(os.path.join(os.path.dirname(__file__), 'details.ui'))

    def print_resource_details(self):
        self.details_layout.imageIdValue.setText(self.selected_resource['ImageId'])
        self.details_layout.imageStateValue.setText(self.selected_resource['State'])

    def get_aws_resources(self):
        response = self.client.describe_images(Filters=[
            {
                'Name': 'is-public',
                'Values': [
                    'false',
                ]
            },
        ])
        self.set_resources_data(response['Images'], 'ImageId')
