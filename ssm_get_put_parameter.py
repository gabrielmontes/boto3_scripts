#!/usr/bin/python3
import argparse, boto3, sys, re

def ssm_get_parameter(name: str, profile: str, region: str) -> dict:
  boto3.setup_default_session(profile_name=profile, region_name=region)
  ssm_client = boto3.client('ssm')
  client_paginator = ssm_client.get_paginator('describe_parameters')
  paginator = client_paginator.paginate().build_full_result()

  for page in paginator['Parameters']:
    response = ssm_client.get_parameter(Name=page['Name'])
    if name in response['Parameter']['Name']:
      yield { "name": response['Parameter']['Name'], "value": response['Parameter']['Value'], "type": response['Parameter']['Type']}

def ssm_put_parameter(value: dict, profile: str, region: str) -> dict:
  boto3.setup_default_session(profile_name=profile, region_name=region)
  ssm_client = boto3.client('ssm')
  
  return ssm_client.put_parameter(
    Name=value['name'],
    Value=value['value'],
    Type=value['type'],
    Tier='Standard',
    DataType='text')

def parser() -> dict:
  parser = argparse.ArgumentParser()
  parser.add_argument('--fromProfile', type=str, required=True)
  parser.add_argument('--fromRegion', type=str, required=True)
  parser.add_argument('--toProfile', type=str, required=True)
  parser.add_argument('--toRegion', type=str, required=True)
  parser.add_argument('--name', type=str, required=True)
  return parser.parse_args()

def main():
  args: dict = parser()
  for value in ssm_get_parameter(args.name, args.fromProfile, args.fromRegion):
    print(ssm_put_parameter(value, args.toProfile, args.toRegion))

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'Unexpected error: {e}')
