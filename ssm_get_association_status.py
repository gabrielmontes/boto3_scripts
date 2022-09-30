#!/usr/bin/python3
import argparse
import boto3

def ssm_get_instances(profile) -> dict:
  ssm_client = profile.client('ssm')
  token: str = ''
  while token is not None:
    page: dict = ssm_client.describe_instance_information(NextToken=token)       
    yield page
    token = page.get('NextToken')

def ssm_get_association_status(profile, instanceid: str) -> dict:
  client = profile.client("ssm")
  return client.describe_instance_associations_status(InstanceId = instanceid)

def parser() -> dict:
  parser = argparse.ArgumentParser()
  parser.add_argument('--profile', type=str, required=True)
  parser.add_argument('--region', type=str, required=True)
  return parser.parse_args()

def main():
  args: dict = parser()
  fromProfile = boto3.setup_default_session(profile_name=args.profile, region_name=args.region)
  failedInstances: list = []

  for page in ssm_get_instances(fromProfile):
    for instance in page['InstanceInformationList']:
      try:
        if instance['AssociationStatus'] == 'Failed':
          failedInstances.append(instance['InstanceId'])
      except KeyError:
        continue

  for instance in failedInstances:
    print(f"Checking instance: {instance}")
    for association in  ssm_get_association_status(fromProfile,instance)['InstanceAssociationStatusInfos']:
      print(f"Association name: {association['Name']} - Status: {association['Status']}")
    print('-' * 15)
    
if __name__ == '__main__':
  main()
