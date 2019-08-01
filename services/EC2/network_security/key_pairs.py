import os
import boto3
from concordia_resources_table import ResourcesTable


class EC2KeyPairs(ResourcesTable):
    def __init__(self, aws_creds, statusbar=None, parent=None):
        super(EC2KeyPairs, self).__init__(statusbar, parent)

        self.client = boto3.client('ec2',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])

        self.set_main_table_fields(['KeyName', 'KeyFingerprint'])

        self.set_details_layout(os.path.join(os.path.dirname(__file__), 'key_pairs_details.ui'))

    def print_resource_details(self):
        self.details_layout.key_pairIdValue.setText(self.selected_resource['KeyName'])
        self.details_layout.key_pairStateValue.setText(self.selected_resource['KeyFingerprint'])

    def get_aws_resources(self):
        response = self.client.describe_key_pairs()
        self.set_resources_data(response['KeyPairs'], 'KeyName')
