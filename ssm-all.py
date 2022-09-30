#!/usr/bin/python3
import argparse
import boto3
import sys

def ssm_get_instances(profile: str, region: str) -> dict:
  ssm_client = boto3.client('ssm')
  token: str = ''
  while token is not None:
    page: dict = ssm_client.describe_instance_information(NextToken=token)
    yield page
    token = page.get('NextToken')

def parser() -> dict:
  parser = argparse.ArgumentParser()
  parser.add_argument('--profile', type=str, required=True)
  parser.add_argument('--region', type=str, required=True)
  return parser.parse_args()

def main():
  args: dict = parser()
  boto3.setup_default_session(profile_name=args.profile, region_name=args.region)
  count:int = 1 

  for page in ssm_get_instances(args.profile, args.region):
    for instance in page['InstanceInformationList']:
      try:
        print(instance)
        #print(f"{count}, {instance['InstanceId']},"\
        #f"{instance['PlatformName']},"\
        #f"{instance['PlatformVersion']},"\
        #f"{instance['PingStatus']},"\
        #f"{instance['AssociationStatus']}")
      except KeyError:
        print(f"{count}, {instance['InstanceId']}, {instance['PingStatus']}")
      count += 1

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'Unexpected error: {e}')
