from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import boto3

main_layout = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'instances.ui'))[0]


class EC2Instances(QWidget, main_layout):

    def __init__(self, aws_creds, parent=None):
        super(EC2Instances, self).__init__(parent)

        self.client = boto3.client('ec2',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])

        self.non_filterable_fields = ['CpuOptions', 'SecurityGroups',
                                      'NetworkInterfaces', 'ProductCodes',
                                      'BlockDeviceMappings', 'Tags',
                                      'Monitoring', 'IamInstanceProfile',
                                      'Placement', 'HibernationOptions',
                                      'CapacityReservationSpecification'
                                      ]

        self.main_table_fields = ['InstanceName', 'InstanceId', 'State',
                                  'InstanceType', 'LaunchTime', 'ImageId',
                                  'VirtualizationType', 'RootDeviceName',
                                  'RootDeviceType', 'KeyName', 'Architecture',
                                  'VpcId', 'SecurityGroups', 'PrivateDnsName',
                                  'AmiLaunchIndex', 'EnaSupport', 'Hypervisor',
                                  'BlockDeviceMappings', 'EbsOptimized', 'Tags',
                                  'NetworkInterfaces', 'PrivateIpAddress',
                                  'StateTransitionReason', 'PublicIpAddress',
                                  'StateReason', 'PublicDnsName', 'Placement',
                                  'ClientToken', 'SourceDestCheck', 'SubnetId',
                                  'CpuOptions', 'Monitoring', 'ProductCodes']

        # self.layout = QHBoxLayout()
        self.setupUi(self)
        self.instances_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'instances_details.ui'))

        self.splitter.splitterMoved.connect(self.on_splitter_size_change)
        self.btnStop.clicked.connect(self.stop_instances)
        self.btnStart.clicked.connect(self.start_instances)

        self.headers, self.instances = self.get_ec2_instances()

        self.fill_in_main_table()

        # self.tableView.setModel(tablemodel)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.horizontalHeader().setSectionsMovable(True)
        self.tableWidget.itemSelectionChanged.connect(self.print_instance_details)

        self.scrollAreaWidgetContents.setLayout(self.gridLayout_2)

        self.tabWidget.addTab(self.instances_layout, "Description")

        self.instances_layout_height = 300

    def on_splitter_size_change(self):
        self.instances_layout_height = self.splitter.sizes()[1]

    def get_table_headers(self):
        headers = []
        for header in self.headers:
            if header not in self.main_table_fields:
                self.main_table_fields.append(header)

        for header in self.main_table_fields:
            if header not in self.non_filterable_fields:
                headers.append(header)
        return headers

    def print_instance_details(self):
        if len(self.tableWidget.selectedItems()) > 0:
            self.splitter.setSizes([self.splitter.sizes()[0], self.instances_layout_height])
            selected_instance = self.instances[self.tableWidget.selectedItems()[0].row()]
            self.instances_layout.launchTimeValue.setText(selected_instance['LaunchTime'])
            self.instances_layout.instanceIdValue.setText(selected_instance['InstanceId'])
            self.instances_layout.instanceStateValue.setText(selected_instance['State'])
            self.instances_layout.AMIIdValue.setText(selected_instance['ImageId'])
            self.instances_layout.instanceTypeValue.setText(selected_instance['InstanceType'])
            self.instances_layout.stateTransitionReasonValue.setText(selected_instance['StateTransitionReason'])
            self.instances_layout.stateTransitionReasonMessageValue.setText(selected_instance['StateReason'])
            #self.instances_layout.capacityReservationValue.setText(selected_instance['CapacityReservationSpecification'])


            self.instances_layout.publicDNSValue.setText(selected_instance['PublicDnsName'])
            self.instances_layout.privateDNSValue.setText(selected_instance['PrivateDnsName'])
            if 'PublicIpAddress' in selected_instance:
                self.instances_layout.publicIPValue.setText(selected_instance['PublicIpAddress'])
            else:
                self.instances_layout.publicIPValue.setText("-")
            self.instances_layout.privateIPValue.setText(selected_instance['PrivateIpAddress'])
            self.instances_layout.VPCIDValue.setText(selected_instance['VpcId'])
            self.instances_layout.subnetIDValue.setText(selected_instance['SubnetId'])
            self.instances_layout.rootDeviceValue.setText(selected_instance['RootDeviceName'])
            self.instances_layout.rootDeviceTypeValue.setText(selected_instance['RootDeviceType'])
            # print(selected_row)
        else:
            self.splitter.setSizes([self.splitter.sizes()[0], 0])

    def fill_in_main_table(self):
        self.tableWidget.setRowCount(len(self.instances))
        table_headers = self.get_table_headers()
        self.tableWidget.setColumnCount(len(table_headers))
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        row_pointer = 0
        for instance in self.instances:
            column_pointer = 0
            for header in table_headers:
                item_value = instance[header] if header in instance and header.strip() != '' else '-'
                self.tableWidget.setItem(row_pointer,
                                         column_pointer,
                                         QTableWidgetItem(item_value))
                column_pointer += 1
            row_pointer += 1

    def get_ec2_instances(self):
        instances = []
        instance_keys = set()

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
                if 'LaunchTime' in instance:
                    instance['LaunchTime'] = '{} UTC'.format(instance['LaunchTime'].strftime("%Y-%m-%d %H:%M:%S"))
                for field in self.main_table_fields:
                    if field not in instance:
                        instance[field] = '-'
                instance_keys.update(instance.keys())
                instances.append(instance)
        return list(instance_keys), instances

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
