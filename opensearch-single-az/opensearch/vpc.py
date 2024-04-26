import pulumi
import ipaddress
import pulumi_aws as aws
from config import name

pub_nets_ids = []
priv_nets_ids = []
zones = aws.get_availability_zones(state="available")


def return_ipv6_cidr(ipv6_block, index):
    cidrs = list(ipaddress.ip_network(ipv6_block).subnets(new_prefix=64))
    return f"{cidrs[index]}"


common_tags = {
    "vpc": "opensearch-vpc",
    "pub_subnet": "opensearch-pub_subnet",
    "priv_subnet": "opensearch-priv_subnet",
    "pub_route_table": "opensearch-pub_route_table",
    "priv_route_table": "opensearch-priv_route_table",
    "ig": "opensearch-ig",
    "sg": "opensearch-sg",
}

vpc = aws.ec2.Vpc(
    name,
    cidr_block="VPC_CIDR_BLOCK",
    assign_generated_ipv6_cidr_block=True,
    tags={"Name": f"{common_tags['vpc']}"},
)

azs = zones.names[:3]
for i, az in enumerate(azs + azs, 1):
    t = "pub" if i % 2 == 0 else "priv"
    subnet = aws.ec2.Subnet(
        f"{name}-{t}-{az}",
        vpc_id=vpc.id,
        availability_zone=az,
        cidr_block=f"172.41.{i}.0/24",
        assign_ipv6_address_on_creation=True,
        ipv6_cidr_block=vpc.ipv6_cidr_block.apply(
            lambda c, j=i: return_ipv6_cidr(c, j)
        ),
        tags=(
            {"kubernetes.io/role/elb": "1", "Name": f"{common_tags['pub_subnet']}"}
            if t == "pub"
            else {"Name": f"{common_tags['priv_subnet']}"}
        ),
    )
    priv_nets_ids.append(subnet.id) if t == "priv" else pub_nets_ids.append(subnet.id)

internet_gw = aws.ec2.InternetGateway(
    name, vpc_id=vpc.id, tags={"Name": f"{common_tags['ig']}"}
)

private_route_table = aws.ec2.RouteTable(
    f"{name}-private",
    vpc_id=vpc.id,
    tags={"Name": f"{common_tags['priv_route_table']}"},
)

public_route_table = aws.ec2.RouteTable(
    f"{name}-public",
    vpc_id=vpc.id,
    routes=[
        aws.ec2.RouteTableRouteArgs(
            cidr_block="0.0.0.0/0",
            gateway_id=internet_gw.id,
        ),
    ],
    tags={"Name": f"{common_tags['pub_route_table']}"},
)

for idx, net_id in enumerate(priv_nets_ids):
    association = aws.ec2.RouteTableAssociation(
        f"{name}-priv-{idx+1}",
        subnet_id=net_id,
        route_table_id=private_route_table.id,
    )

for idx, net_id in enumerate(pub_nets_ids):
    association = aws.ec2.RouteTableAssociation(
        f"{name}-pub-{idx+1}",
        subnet_id=net_id,
        route_table_id=public_route_table.id,
    )

opensearch_sg = aws.ec2.SecurityGroup(
    f"{name}-domain-sg",
    name=f"{name}-domain-sg",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=22,
            to_port=22,
            cidr_blocks=["SSH_IP"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=0,
            to_port=65535,
            cidr_blocks=["VPC_CIDR_BLOCK"],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
    tags={"Name": f"{common_tags['sg']}"},
)


alb_sg = aws.ec2.SecurityGroup(
    f"{name}-alb-sg",
    name=f"{name}-alb-sg",
    vpc_id=vpc.id,
    ingress=[
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=80,
            to_port=80,
            cidr_blocks=["0.0.0.0/0"],
        ),
        aws.ec2.SecurityGroupIngressArgs(
            protocol="tcp",
            from_port=443,
            to_port=443,
            cidr_blocks=["0.0.0.0/0"],
        ),
    ],
    egress=[
        aws.ec2.SecurityGroupEgressArgs(
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
        )
    ],
    tags={"Name": f"{common_tags['sg']}"},
)

