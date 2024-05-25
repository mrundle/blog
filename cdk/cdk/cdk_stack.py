from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_ec2 as ec2,
    # aws_sqs as sqs,
    RemovalPolicy,
    CfnTag,
    CfnOutput,
)
from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "CdkQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )

        self.setup_s3()
        self.setup_ec2()
        self.setup_billing_alarm()

    def setup_billing_alarm(self):
        # TODO
        pass

    def setup_s3(self):
        # note that the bucket name will actually be created by cdk,
        # and won't be exactly "mrundle-blog-bucket"
        #bucket = s3.Bucket(self, "mrundle-blog-bucket", versioned=False)
        bucket = s3.Bucket(
            self,
            "blog-contents",
            versioned=False,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True)

    def setup_ec2(self):
        # create vpc
        vpc = ec2.Vpc(self, "blog-host-vpc",
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            vpc_name="blog-host-vpc",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="blog-host-public-subnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
        )

        # create security group
        sg = ec2.SecurityGroup(
            self, "blog-host-sg", vpc=vpc, allow_all_outbound=True,
        )
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "allow ssh access"),
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "allow http access"),
        sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "allow https access"),

        # create Key Pair
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/CfnKeyPair.html
        keypair = ec2.CfnKeyPair(
            self,
            "blog-host-keypair",
            key_name="blog-host-keypair"
        )

        # create EC2 instance
        # https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_ec2/README.html
        # https://docs.aws.amazon.com/linux/al2023/ug/what-is-amazon-linux.html
        instance = ec2.Instance(
            self,
            "blog-host-instance",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            vpc=vpc,
            security_group=sg,
            associate_public_ip_address=True,
            key_name=keypair.key_name,
        )

        CfnOutput(self, "InstanceId", value=instance.instance_id)
