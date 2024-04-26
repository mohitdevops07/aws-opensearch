import pulumi

config = pulumi.Config()
name = pulumi.get_project()
common = pulumi.StackReference("organization/common-config/common-config")
opensearch_user = common.require_output("opensearch_user")
opensearch_password = common.require_output("opensearch_password")
testopensearch_public_ssh_key = common.require_output("testopensearch_public_ssh_key")
