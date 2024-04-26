import yaml
import pulumi
import subprocess

data = subprocess.run(["sops", "-d", "config.yaml"], stdout=subprocess.PIPE)
config = yaml.safe_load(data.stdout)

for k, v in config.items():
    pulumi.export(k, pulumi.Output.secret(v))
