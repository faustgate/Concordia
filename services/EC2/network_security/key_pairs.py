from PyQt5 import uic
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

        self.refresh_main_table()

    def print_resource_details(self):
        self.details_layout.key_pairIdValue.setText(self.selected_resource['KeyName'])
        self.details_layout.key_pairStateValue.setText(self.selected_resource['KeyFingerprint'])

    def get_aws_resources(self):
        key_pairs = []
        response = self.client.describe_key_pairs()
        for key_pair in response['KeyPairs']:
            self.resources_data_keys.update(key_pair.keys())
            key_pairs.append(key_pair)
        self.set_resources_data(key_pairs, 'KeyName')
