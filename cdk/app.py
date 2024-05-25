#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk.cdk_stack import CdkStack

# Note: for now, just specify the role via `cdk --profile <aws-profile-name>`
# It can also be done other ways: https://docs.aws.amazon.com/cdk/latest/guide/environments.html
# env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),
# env=cdk.Environment(account='account-id', region='us-blah-N'),

app = cdk.App()
CdkStack(app, "CdkStack")
app.synth()
