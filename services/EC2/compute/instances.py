from PyQt5.QtCore import *
import os
import boto3
from concordia_resources_table import ResourcesTable


class EC2Instances(ResourcesTable):
    data_downloaded = pyqtSignal()

    def __init__(self, aws_creds, statusbar=None, parent=None):
        super(EC2Instances, self).__init__(statusbar, parent)

        self.client = boto3.client('ec2',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])

        self.set_hidden_fields(['CpuOptions', 'SecurityGroups', 'Monitoring',
                                'NetworkInterfaces', 'ProductCodes', 'Tags',
                                'CapacityReservationSpecification',
                                'IamInstanceProfile', 'Placement',
                                'HibernationOptions', 'BlockDeviceMappings'])

        self.set_main_table_fields(['InstanceName', 'InstanceId', 'State',
                                    'InstanceType', 'LaunchTime', 'ImageId',
                                    'VirtualizationType', 'RootDeviceName',
                                    'RootDeviceType', 'KeyName', 'Hypervisor',
                                    'Architecture', 'VpcId', 'AmiLaunchIndex',
                                    'PrivateDnsName', 'EnaSupport', 'SubnetId',
                                    'EbsOptimized', 'PrivateIpAddress',
                                    'StateReason', 'PublicIpAddress',
                                    'StateTransitionReason', 'PublicDnsName',
                                    'SourceDestCheck', 'CpuOptions'])

        self.set_details_layout(os.path.join(os.path.dirname(__file__), 'instances_details.ui'))

        # self.btnStop.clicked.connect(self.stop_instances)
        # self.btnStart.clicked.connect(self.start_instances)

    def print_resource_details(self):
        self.details_layout.launchTimeValue.setText(self.selected_resource['LaunchTime'])
        self.details_layout.instanceIdValue.setText(self.selected_resource['InstanceId'])
        self.details_layout.instanceStateValue.setText(self.selected_resource['State'])
        self.details_layout.AMIIdValue.setText(self.selected_resource['ImageId'])
        self.details_layout.instanceTypeValue.setText(self.selected_resource['InstanceType'])
        self.details_layout.stateTransitionReasonValue.setText(self.selected_resource['StateTransitionReason'])
        self.details_layout.stateTransitionReasonMessageValue.setText(self.selected_resource['StateReason'])
        #self.instances_layout.capacityReservationValue.setText(self.selected_resource['CapacityReservationSpecification'])
        self.details_layout.publicDNSValue.setText(self.selected_resource['PublicDnsName'])
        self.details_layout.privateDNSValue.setText(self.selected_resource['PrivateDnsName'])
        if 'PublicIpAddress' in self.selected_resource:
            self.details_layout.publicIPValue.setText(self.selected_resource['PublicIpAddress'])
        else:
            self.details_layout.publicIPValue.setText("-")
        self.details_layout.privateIPValue.setText(self.selected_resource['PrivateIpAddress'])
        self.details_layout.VPCIDValue.setText(self.selected_resource['VpcId'])
        self.details_layout.subnetIDValue.setText(self.selected_resource['SubnetId'])
        self.details_layout.rootDeviceValue.setText(self.selected_resource['RootDeviceName'])
        self.details_layout.rootDeviceTypeValue.setText(self.selected_resource['RootDeviceType'])

    def get_aws_resources(self):
        instances = []
        response = self.client.describe_instances()
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instance['State'] = instance['State']['Name']
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        instance['InstanceName'] = tag['Value']
                        break
                if 'StateReason' in instance:
                    instance['StateReason'] = instance['StateReason']['Message']
                instances.append(instance)
        self.set_resources_data(instances, 'InstanceId')

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
