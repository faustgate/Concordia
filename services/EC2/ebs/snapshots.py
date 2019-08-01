from PyQt5.QtCore import *
import os
import boto3
from concordia_resources_table import ResourcesTable


class EC2EBSSnapshots(ResourcesTable):
    data_downloaded = pyqtSignal()

    def __init__(self, aws_creds, statusbar=None, parent=None):
        super(EC2EBSSnapshots, self).__init__(statusbar, parent)

        self.client = boto3.client('ec2',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])

        self.set_hidden_fields(['Attachments', 'Tags', 'CreateTime'])

        self.set_main_table_fields(['SnapshotId', 'Description', 'Encrypted',
                                    'VolumeSize', 'VolumeId', 'State', 'OwnerId',
                                    'Progress'])

        self.set_details_layout(os.path.join(os.path.dirname(__file__), 'snapshots_details.ui'))

    def print_resource_details(self):
        self.details_layout.snapshotIdValue.setText(self.selected_resource['SnapshotId'])
        self.details_layout.snapshotStateValue.setText(self.selected_resource['State'])

    def get_aws_resources(self):
        response = self.client.describe_snapshots(OwnerIds=['self'])
        self.set_resources_data(response['Snapshots'], 'SnapshotId')
