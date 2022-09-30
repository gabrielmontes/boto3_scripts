#!/usr/bin/python3
# Check ssm agent by ec2 state.
# Usage ./ssmReport.py --profile=profile --state=(pending|running|shutting-down|terminated|stopping|stopped)
import boto3
import argparse
import sys

def ec2_describe_instances(state: str) -> dict:
  client = boto3.client('ec2')
  filters =  [{'Name': 'instance-state-name', 'Values': [state]}]
  paginator = client.get_paginator("describe_instances")
  for result in paginator.paginate(Filters = filters):
    for instances in result["Reservations"]:
      for instance in instances["Instances"]:
        yield instance

def ssm_describe_instance_information(instanceID: str) -> dict:
  client = boto3.client('ssm')
  filters = [{'Key': 'InstanceIds', 'Values': [instanceID]}]
  return client.describe_instance_information(Filters = filters)['InstanceInformationList']

def ec2_get_instance_name(instanceDict: dict) -> str:
  for tag in instanceDict['Tags']:
    if tag['Key'] == 'Name':
      return tag['Value']

def parser() -> dict:
  parser = argparse.ArgumentParser(description=(f'Usage: {sys.argv[0]} --profile=profile --state=state'))
  parser.add_argument('--state', type=str, required=True)
  parser.add_argument('--profile', type=str,required=True)
  parser.add_argument('--region', type=str, required=True)
  return parser.parse_args()

def main():
  args = parser()
  boto3.setup_default_session(profile_name=args.profile, region_name=args.region)
  
  for instance in ec2_describe_instances(args.state):
    if not (ssm_describe_instance_information(instance['InstanceId'])):
      name = ec2_get_instance_name(instance)
      if not name:
        print(f"Instance id: {instance['InstanceId']}")
      else:
        print(f"Instance id: {instance['InstanceId']} Name: {name}")

if __name__ == '__main__':
  main()
