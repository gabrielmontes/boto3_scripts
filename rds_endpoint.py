#!/usr/bin/python3 
import boto3
import argparse

def parser() -> dict:
  parser = argparse.ArgumentParser()
  parser.add_argument('--profile', type=str, required=True)
  parser.add_argument('--region', type=str, required=True)
  return parser.parse_args()

def main():
  args: dict = parser()
  boto3.setup_default_session(profile_name=args.profile, region_name=args.region)
  rds_client = boto3.client('rds')
  response: dict = rds_client.describe_db_instances()
  for i in response['DBInstances']:
    print(i['Endpoint'])

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'Unexpected error: {e}')
