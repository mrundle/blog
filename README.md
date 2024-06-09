# Description

The goal of this CDK is to setup up a Wordpress server on an ec2 instance, via AWS CDK.

Right now, the CDK stack just creates an EC2 instance.

## TODO

* Set up billing alarm
* Automate wordpress setup
* Set up deployment stack?

https://docs.aws.amazon.com/linux/al2/ug/hosting-wordpress.html#install-wordpress
https://docs.aws.amazon.com/codedeploy/latest/userguide/tutorials-wordpress-configure-content.html
https://aws.amazon.com/tutorials/deploy-wordpress-with-amazon-rds

Import/export:
* https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/SQLServer.Procedural.Importing.html

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
cdk --profile blog diff
```

To actually deploy:
```
cdk --profile blog deploy
```

To destroy the stack:

```
cdk --profile blog destroy
```

### Host login

```
tools/ssh-to-instance.sh
```

## Domain / DNS

* Using Squarespace domains, formerly Google Domains
* Configured the DNS 'A' entry to point to the EC2 instance IP

## Wordpress

Followed tutorials for setup on the AWS Instance. This was essentially all manual.
The one thing I did via AWS was set up an RDS instance. Configuration:

```
CREATE DATABASE wordpress;
CREATE USER 'wordpress' IDENTIFIED BY 'wordpress-pass';
GRANT ALL PRIVILEGES ON wordpress.* TO wordpress;
FLUSH PRIVILEGES;
EXIT;
```

## SSL/HTTPS Cert

Using the LetsEncrypt CA via Certbot: https://certbot.eff.org/

```
sudo yum install -y certbot python3-certbot-apache
sudo certbot --apache
```
