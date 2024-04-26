import pulumi
import pulumi_aws as aws
from vpc import priv_nets_ids, opensearch_sg
from config import config, name, opensearch_user, opensearch_password

env = config.require("env")

domain = aws.opensearch.Domain(
    name,
    domain_name=f"{name}-{env}",
    engine_version=config.require("engine_version"),
    cluster_config=aws.opensearch.DomainClusterConfigArgs(
        instance_type=config.require("instance_type"),
        # zone_awareness_enabled=True,
        instance_count=config.require("nodes_count"),
        multi_az_with_standby_enabled=False,
    ),
    ebs_options=aws.opensearch.DomainEbsOptionsArgs(
        ebs_enabled=True,
        volume_size=config.require("volume_size"),
        volume_type="gp3",
    ),
    software_update_options=aws.opensearch.DomainSoftwareUpdateOptionsArgs(
        auto_software_update_enabled=False,
    ),
    vpc_options=aws.opensearch.DomainVpcOptionsArgs(
        subnet_ids=[
            priv_nets_ids[0],
        ],
        security_group_ids=[opensearch_sg.id],
    ),
    advanced_security_options=aws.opensearch.DomainAdvancedSecurityOptionsArgs(
        enabled=True,
        internal_user_database_enabled=True,
        master_user_options=aws.opensearch.DomainAdvancedSecurityOptionsMasterUserOptionsArgs(
            master_user_name=opensearch_user,
            master_user_password=opensearch_password,
        ),
    ),
    domain_endpoint_options=aws.opensearch.DomainDomainEndpointOptionsArgs(
        enforce_https=True,
        tls_security_policy="Policy-Min-TLS-1-2-2019-07",
    ),
    node_to_node_encryption=aws.opensearch.DomainNodeToNodeEncryptionArgs(
        enabled=True,
    ),
    encrypt_at_rest=aws.opensearch.DomainEncryptAtRestArgs(
        enabled=True,
    ),
    tags={
        "Domain": f"{env}",
    },
)
domain_arn = config.require("domain_policy_arn")
policy_arn = domain_arn + "/*"

domain_policy = (
    aws.opensearch.DomainPolicy(
        f"{name}-doamin-policy",
        domain_name=domain.domain_name,
        access_policies=f"""{{
            "Version": "2012-10-17",
            "Statement": [
                {{
                    "Effect": "Allow",
                    "Principal": {{
                        "AWS": "*"
                    }},
                    "Action": "es:*",
                    "Resource": "{policy_arn}"
                }}
            ]
        }}""",
    ),
)


pulumi.export("opensearch_domain_arn", domain.arn)
pulumi.export("opensearch_domain_endpoint", domain.endpoint)
