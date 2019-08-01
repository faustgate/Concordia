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
                                'OptionGroupMemberships', 'DomainMemberships',
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

        self.refresh_main_table()

    def print_resource_details(self):
        self.details_layout.instanceIdValue.setText(self.selected_resource['InstanceId'])
        self.details_layout.instanceStateValue.setText(self.selected_resource['State'])
        self.details_layout.publicDNSValue.setText(self.selected_resource['PublicDnsName'])
        self.details_layout.privateDNSValue.setText(self.selected_resource['PrivateDnsName'])
        if 'PublicIpAddress' in self.selected_resource:
            self.details_layout.publicIPValue.setText(self.selected_resource['PublicIpAddress'])
        else:
            self.details_layout.publicIPValue.setText("-")
        self.details_layout.privateIPValue.setText(self.selected_resource['PrivateIpAddress'])
        self.details_layout.VPCIDValue.setText(self.selected_resource['VpcId'])
        self.details_layout.SubnetIDValue.setText(self.selected_resource['SubnetId'])
        self.details_layout.rootDeviceIdValue.setText(self.selected_resource['RootDeviceName'])
        self.details_layout.rootDeviceTypeValue.setText(self.selected_resource['RootDeviceType'])

    def get_aws_resources(self):
        response = self.client.describe_db_instances()
        self.set_resources_data(response['DBInstances'], 'DBInstanceIdentifier')

    def get_selected_instance_ids(self):
        ids = set()
        if len(self.tableWidget.selectedItems()) > 0:
            selected_instances = self.tableWidget.selectedItems()
            for instance in selected_instances:
                ids.add(self.instances[instance.row()]['InstanceId'])
            return list(ids)

    def stop_instances(self):
        self.client.stop_instances(InstanceIds=self.get_selected_instance_ids())

    def start_instances(self):
        self.client.start_instances(InstanceIds=self.get_selected_instance_ids())
