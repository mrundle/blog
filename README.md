# Description

The goal of this CDK is to setup up a Wordpress server on an ec2 instance, via AWS CDK.

Right now, the CDK stack just creates an EC2 instance.

## TODO

* Set up billing alarm
* Set up wordpress
* Set up deployment stack?

https://docs.aws.amazon.com/codedeploy/latest/userguide/tutorials-wordpress-configure-content.html

# Setup

## AWS CDK

### Install
```
brew install aws-cdk
cdk bootstrap aws://account-number/region
mkdir cdk/ && cd cdk/
cdk init app --language python
source .venv/bin/activate
python -m pip install -r requirements.txt
```

The actual CDK stack definition is located at `cdk/cdk/cdk_stack.py`.

### Build and Deploy

Note that `blog` is a profile set up in `~/.aws/{credentials,config}`:
```
cdk synth
```

To see what changes would be made:
```
cdk --profile diff
```

To actually deploy:
```
cdk --profile blog deploy
```

### Host login

```
tools/ssh-to-instance.sh
```
