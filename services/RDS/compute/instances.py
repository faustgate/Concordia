from PyQt5.QtCore import *
import os
import boto3
from concordia_resources_table import ResourcesTable


class RDSInstances(ResourcesTable):
    data_downloaded = pyqtSignal()

    def __init__(self, aws_creds, statusbar=None, parent=None):
        super(RDSInstances, self).__init__(statusbar, parent)

        self.client = boto3.client('rds',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])

        self.set_hidden_fields(['Endpoint', 'DBSecurityGroups',
                                'VpcSecurityGroups', 'DBParameterGroups',
                                'DBSubnetGroup', 'ReadReplicaDBInstanceIdentifiers',
                                'OptionGroupMemberships',
                                'InstanceCreateTime', 'LatestRestorableTime',
                                'PendingModifiedValues'])

        self.set_main_table_fields(['DBInstanceIdentifier', 'DBInstanceClass',
                                    'DBInstanceStatus', 'AvailabilityZone',
                                    'MultiAZ', 'SecondaryAvailabilityZone',
                                    'Engine', 'EngineVersion',
                                    'AutoMinorVersionUpgrade',
                                    'MasterUsername',  'AllocatedStorage',
                                    'PreferredBackupWindow',
                                    'BackupRetentionPeriod',
                                    'PreferredMaintenanceWindow',
                                    'LicenseModel'])

        self.set_details_layout(os.path.join(os.path.dirname(__file__), 'instances_details.ui'))

        # self.btnStop.clicked.connect(self.stop_instances)
        # self.btnStart.clicked.connect(self.start_instances)

    def print_resource_details(self):
        self.details_layout.instanceIdValue.setText(self.selected_resource['DBInstanceIdentifier'])

    def get_aws_resources(self):
        # response = self.client.describe_db_clusters()
        response = self.client.describe_db_instances()
        self.set_resources_data(response['DBInstances'], 'DBInstanceIdentifier')

    def get_selected_instance_ids(self):
        ids = set()
        if len(self.tableWidget.selectedItems()) > 0:
            selected_instances = self.tableWidget.selectedItems()
            for instance in selected_instances:
                ids.add(self.resources_data[instance.row()]['DBInstanceIdentifier'])
            return list(ids)

    def get_selected_instance_arns(self):
        arns = set()
        if len(self.resources_table.selectedItems()) > 0:
            selected_instances = self.resources_table.selectedItems()
            for instance in selected_instances:
                arns.add(self.resources_data[instance.row()]['DBInstanceArn'])
            return list(arns)

    def print_details(self):
        sel_items = self.resources_table.selectedItems()
        if len(sel_items) in range(0, len(self.resources_data[0])):
            self.resources_data[sel_items[0].row()]['Tags'] = self.get_selected_instance_tags()
        super(RDSInstances, self).print_details()

    def get_selected_instance_tags(self):
        selected_instance_arn = self.get_selected_instance_arns()
        if len(selected_instance_arn) == 1:
            sel_inst_arn = self.get_selected_instance_arns()[0]
            return self.client.list_tags_for_resource(ResourceName=sel_inst_arn)['TagList']

    def stop_instances(self):
        self.client.stop_instances(InstanceIds=self.get_selected_instance_ids())

    def start_instances(self):
        self.client.start_instances(InstanceIds=self.get_selected_instance_ids())
