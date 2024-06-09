from aws_cdk import (
    # Duration,
    Stack,
    aws_s3 as s3,
    aws_ec2 as ec2,
    aws_iam as iam,
    # aws_sqs as sqs,
    aws_rds as rds,
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

        self.BLOG_VPC_CIDR = "10.0.0.0/16"
        self.MYSQL_PORT = 3306

        self.bucket = None
        self.blog_instance = None

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
        self.bucket = s3.Bucket(
            self,
            "blog-contents",
            versioned=False,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True)

    def setup_ec2(self):
        # create vpc
        vpc = ec2.Vpc(self, "blog-host-vpc",
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr(self.BLOG_VPC_CIDR),
            vpc_name="blog-host-vpc",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="blog-host-public-subnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                ),
                ec2.SubnetConfiguration(
                    name="blog-host-private-subnet",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24,
                )
            ],
        )

        # add gateway/interface endpoints
        vpc.add_gateway_endpoint("s3", service=ec2.GatewayVpcEndpointAwsService.S3)
        # XXX/NOTE: interface endpoints are pretty pricey?
        #vpc.add_interface_endpoint("ssm", service=ec2.InterfaceVpcEndpointAwsService.SSM)
        #vpc.add_interface_endpoint("ec2messages", service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES)
        #vpc.add_interface_endpoint("ssmmessages", service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES)

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
        self.blog_instance = ec2.Instance(
            self,
            "blog-host-instance",
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type = ec2.SubnetType.PUBLIC,
            ),
            security_group=sg,
            associate_public_ip_address=True,
            key_name=keypair.key_name,
        )

        # s3 bucket grants
        self.blog_instance.role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=["arn:aws:s3:::*"],
            actions=["s3:ListAllMyBuckets"],
        ))
        self.blog_instance.role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=[self.bucket.bucket_arn],
            actions=["s3:ListBucket"],
        ))
        self.blog_instance.role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            resources=[f"{self.bucket.bucket_arn}/*"],
            actions=[
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:PutObjectAcl"
            ]
        ))
        #instance.role.add_to_policy(iam.PolicyStatement(
        #    effect=iam.Effect.ALLOW,
        #    resources=["*"],
        #    actions=[
        #        "ec2messages:*",
        #        "ssmmessages:*",
        #        "ssm:UpdateInstanceInformation",
        #    ]
        #))

        CfnOutput(self, "InstanceId", value=self.blog_instance.instance_id)

        #
        # set up rds instance
        #
        db = rds.DatabaseInstance(
            self,
            "blog_database",
            engine = rds.DatabaseInstanceEngine.MYSQL,
            vpc = vpc,
            vpc_subnets = ec2.SubnetSelection(
                subnet_type = ec2.SubnetType.PRIVATE_ISOLATED,
            ),
            credentials = rds.Credentials.from_generated_secret("Admin"),
            instance_type = ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3,
                ec2.InstanceSize.MICRO),
            port = self.MYSQL_PORT,
            allocated_storage = 80,
            multi_az = False,
            removal_policy = RemovalPolicy.DESTROY,
            deletion_protection = False,
            publicly_accessible = False,
        )
        # XXX/TODO use separate security group
        db.connections.allow_from(
            ec2.Peer.ipv4(self.BLOG_VPC_CIDR),
            ec2.Port.tcp(self.MYSQL_PORT),
            description="mysql db connection",
        )
        CfnOutput(self, "db_endpoint", value=db.db_instance_endpoint_address)

