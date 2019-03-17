from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os
import boto3

main_layout = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'instances.ui'))[0]


class RDSInstances(QWidget, main_layout):

    def __init__(self, aws_creds, parent=None):
        super(RDSInstances, self).__init__(parent)
        self.non_filterable_fields = ['Endpoint', 'DBSecurityGroups',
                                      'VpcSecurityGroups', 'DBParameterGroups',
                                      'DBSubnetGroup', 'ReadReplicaDBInstanceIdentifiers',
                                      'OptionGroupMemberships', 'DomainMemberships',
                                      'InstanceCreateTime', 'LatestRestorableTime',
                                      'PendingModifiedValues'
                                      ]

        # self.layout = QHBoxLayout()
        self.setupUi(self)
        self.instances_layout = uic.loadUi(os.path.join(os.path.dirname(__file__), 'details.ui'))

        self.headers, self.instances = self.get_rds_instances(aws_creds)

        self.fill_in_main_table()

        # self.tableView.setModel(tablemodel)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.itemClicked.connect(self.print_instance_details)

        self.scrollAreaWidgetContents.setLayout(self.gridLayout_2)

        self.tabWidget.addTab(self.instances_layout, "Description")


        # tbw = QLabel()
        # tbw.setText()

        # self.layout.addWidget(self.tableView)
        # self.setLayout(self.layout)

    def get_table_headers(self):
        headers = []
        for header in self.headers:
            if header not in self.non_filterable_fields:
                headers.append(header)
        return headers

    def print_instance_details(self):
        selected_instance = self.instances[self.tableWidget.selectedItems()[0].row()]
        self.instances_layout.instanceIdValue.setText(selected_instance['InstanceId'])
        self.instances_layout.instanceStateValue.setText(selected_instance['State'])
        self.instances_layout.publicDNSValue.setText(selected_instance['PublicDnsName'])
        self.instances_layout.privateDNSValue.setText(selected_instance['PrivateDnsName'])
        if 'PublicIpAddress' in selected_instance:
            self.instances_layout.publicIPValue.setText(selected_instance['PublicIpAddress'])
        else:
            self.instances_layout.publicIPValue.setText("-")
        self.instances_layout.privateIPValue.setText(selected_instance['PrivateIpAddress'])
        self.instances_layout.VPCIDValue.setText(selected_instance['VpcId'])
        self.instances_layout.SubnetIDValue.setText(selected_instance['SubnetId'])
        self.instances_layout.rootDeviceIdValue.setText(selected_instance['RootDeviceName'])
        self.instances_layout.rootDeviceTypeValue.setText(selected_instance['RootDeviceType'])
        #print(selected_row)

    def fill_in_main_table(self):
        self.tableWidget.setRowCount(len(self.instances))
        table_headers = self.get_table_headers()
        self.tableWidget.setColumnCount(len(table_headers))
        self.tableWidget.setHorizontalHeaderLabels(table_headers)
        row_pointer = 0
        for instance in self.instances:
            column_pointer = 0
            for header in table_headers:
                item_value = instance[header] if header in instance else '-'
                self.tableWidget.setItem(row_pointer,
                                         column_pointer,
                                         QTableWidgetItem(item_value))
                column_pointer += 1
            row_pointer += 1

    def get_rds_instances(self, aws_creds):
        instances = []
        instance_keys = set()
        client = boto3.client('rds',
                              aws_access_key_id=aws_creds['access_key'],
                              aws_secret_access_key=aws_creds['secret_key'],
                              region_name=aws_creds['region'])
        response = client.describe_db_instances()
        for instance in response['DBInstances']:
            # for tag in instance['Tags']:
            #     if tag['Key'] == 'Name':
            #         instance['InstanceName'] = tag['Value']
            #         break
            # if 'StateReason' in instance:
            #     instance['StateReason'] = instance['StateReason']['Message']
            instance_keys.update(instance.keys())
            instances.append(instance)
        return list(instance_keys), instances
