#!/usr/bin/python3
import argparse, boto3, sys

def ssm_get_parameter(name: str) -> dict:
  ssm_client = boto3.client('ssm')
  client_paginator = ssm_client.get_paginator('describe_parameters')
  paginator = client_paginator.paginate().build_full_result()

  for page in paginator['Parameters']:
    response = ssm_client.get_parameter(Name=page['Name'], WithDecryption=True)
    if name in response['Parameter']['Name']:
      return f"Name: {name}\nType: {response['Parameter']['Type']}\nValue: {response['Parameter']['Value']} "

def parser() -> dict:
  parser = argparse.ArgumentParser()
  parser.add_argument('--profile', type=str, required=True)
  parser.add_argument('--region', type=str, required=True)
  parser.add_argument('--name', type=str, required=True)
  return parser.parse_args()

def main():
  args: dict = parser()
  boto3.setup_default_session(profile_name=args.profile, region_name=args.region)
  print(ssm_get_parameter(args.name))

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'Unexpected error: {e}')
