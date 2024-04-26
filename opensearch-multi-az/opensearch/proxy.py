import pulumi
import pulumi_aws as aws
from vpc import vpc, pub_nets_ids, opensearch_sg, alb_sg
from config import config, name, common

ssh_key = aws.ec2.KeyPair(
    name,
    key_name=name,
    public_key=common.require_output("opensearch_public_ssh_key"),
)

proxy_root_ebs = {
    "deleteOnTermination": True,
    "volume_size": config.require("volume_proxy_size"),
    "volumeType": "gp3",
    "encrypted": True,
}

proxy_instance = aws.ec2.Instance(
    f"{name}-proxy",
    ami=config.require("ami_id"),
    instance_type=config.require("proxy_instance_type"),
    subnet_id=pub_nets_ids[0],
    key_name=ssh_key.key_name,
    vpc_security_group_ids=[opensearch_sg],
    root_block_device=proxy_root_ebs,
    tags={"Name": f"{name}-proxy"},
)

proxy_eip= aws.ec2.Eip(
    f"{name}-proxy",
    instance=proxy_instance.id,
    tags={"Name": f"{name}-proxy"},
)

certs = aws.acm.Certificate(
    f"{name}-acm",
    domain_name="*.scwlabs.com",
    validation_method="DNS",
    tags={"name": "scwlabs.com"},
)


alb = aws.lb.LoadBalancer(
    f"{name}-alb",
    name=f"{name}-alb",
    load_balancer_type="application",
    security_groups=[alb_sg.id],
    subnets=[pub_nets_ids[0], pub_nets_ids[1], pub_nets_ids[2]],
)

lb_target_group = aws.lb.TargetGroup(
    f"{name}-target-group",
    port=80,
    protocol="HTTP",
    vpc_id=vpc,
    target_type="instance",
)

http_listener = aws.lb.Listener(
    f"{name}-http-listener",
    load_balancer_arn=alb.arn,
    port=80,
    default_actions=[
        {
            "type": "redirect",
            "redirect": {
                "port": "443",
                "protocol": "HTTPS",
                "status_code": "HTTP_301",
            },
        }
    ],
)

https_listener = aws.lb.Listener(
    f"{name}-https-listener",
    load_balancer_arn=alb.arn,
    port=443,
    protocol="HTTPS",
    ssl_policy="ELBSecurityPolicy-2016-08",
    certificate_arn=certs.arn,
    default_actions=[
        {
            "type": "forward",
            "target_group_arn": lb_target_group.arn,
        }
    ],
)

instance_attachment = aws.lb.TargetGroupAttachment(
    f"{name}-target-group-attachment",
    target_group_arn=lb_target_group.arn,
    target_id=proxy_instance.id,
    port=80,
)

pulumi.export("public_ip", proxy_instance.public_ip)
pulumi.export("alb_dns_name", alb.dns_name)
pulumi.export("certificate_arn", certs.arn)
 
