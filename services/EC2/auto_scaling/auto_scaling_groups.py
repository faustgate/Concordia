import os
import boto3
from concordia_resources_table import ResourcesTable


class EC2ASGs(ResourcesTable):
    def __init__(self, aws_creds, statusbar=None, parent=None):
        super(EC2ASGs, self).__init__(statusbar, parent)

        self.client = boto3.client('autoscaling',
                                   aws_access_key_id=aws_creds['access_key'],
                                   aws_secret_access_key=aws_creds['secret_key'],
                                   region_name=aws_creds['region'])
        self.set_hidden_fields(['Instances', 'Tags', 'EnabledMetrics'])

        self.set_main_table_fields(['AutoScalingGroupName', 'MinSize',
                                    'DesiredCapacity', 'MaxSize',
                                    'LaunchConfigurationName',
                                    'AutoScalingGroupARN', 'DefaultCooldown',
                                    'HealthCheckType', 'AvailabilityZones',
                                    'HealthCheckGracePeriod', 'EnabledMetrics',
                                    'VPCZoneIdentifier', 'SuspendedProcesses',
                                    'NewInstancesProtectedFromScaleIn',
                                    'ServiceLinkedRoleARN', 'LoadBalancerNames',
                                    'TargetGroupARNs', 'TerminationPolicies'])

        self.set_details_layout(os.path.join(os.path.dirname(__file__), 'auto_scaling_groups_details.ui'))

    def print_resource_details(self):
        self.details_layout.auto_scaling_groupIdValue.setText(self.selected_resource['AutoScalingGroupName'])

    def get_aws_resources(self):
        asgs = self.client.describe_auto_scaling_groups()['AutoScalingGroups']
        for asg in asgs:
            for header in ['AvailabilityZones', 'LoadBalancerNames',
                           'TargetGroupARNs', 'SuspendedProcesses',
                           'TerminationPolicies']:
                if header in asg:
                    asg[header] = ','.join(asg[header])
        self.set_resources_data(asgs, 'AutoScalingGroupARN')
