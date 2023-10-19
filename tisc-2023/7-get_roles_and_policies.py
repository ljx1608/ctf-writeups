import json
from pathlib import Path

import boto3
import botocore.exceptions

session = boto3.Session(profile_name="tisc-2023")
sts = session.client("sts")
try:
    sts.get_caller_identity()
except botocore.exceptions.ClientError:
    print("Credentials are NOT valid.")
    print("Run get_keys.py (if necessary), `curl -k https://13.213.29.24/ --cert client.crt --key client.key`, then `aws configure --profile tisc-2023`.")
    exit(0)


iam = session.client("iam")

roles = iam.list_roles()["Roles"]
json.dump(roles, open("list-roles.json", "w"), indent=2, default=str)

for role in roles:
    if "aws-service-role" in role["Path"]:
        continue

    print("-" * 80)
    print(role["RoleName"])

    Path(f"roles/{role['RoleName']}").mkdir(parents=True, exist_ok=True)

    print("Inline Policies:")
    role_policies = iam.list_role_policies(RoleName=role["RoleName"])["PolicyNames"]
    for policy in role_policies:
        print(policy)
        policy_doc = iam.get_role_policy(RoleName=role["RoleName"], PolicyName=policy)["PolicyDocument"]
        json.dump(
            policy_doc,
            open(f"roles/{role['RoleName']}/role_{policy}.json", "w"),
            indent=2,
            default=str
        )

    print("Managed Policies:")
    attached_policies = iam.list_attached_role_policies(RoleName=role["RoleName"])["AttachedPolicies"]
    for policy in attached_policies:
        print(policy["PolicyName"])
        default_version_id = iam.get_policy(PolicyArn=policy["PolicyArn"])["Policy"]["DefaultVersionId"]
        policy_doc = iam.get_policy_version(PolicyArn=policy["PolicyArn"], VersionId=default_version_id)["PolicyVersion"]["Document"]
        json.dump(
            policy_doc,
            open(f"roles/{role['RoleName']}/attached_{policy['PolicyName']}.json", "w"),
            indent=2,
            default=str
        )
