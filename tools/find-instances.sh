#!/bin/bash
# To limit only to running instances:
#
#     --filters "Name=instance-state-name,Values=running"

aws --profile blog ec2 describe-instances \
    --query 'Reservations[*].Instances[*].[InstanceId, InstanceType, State.Name, KeyName, PublicIpAddress, PublicDnsName]' \
    --output table
