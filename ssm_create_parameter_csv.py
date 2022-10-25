#!/usr/bin/python3
import argparse, boto3, sys, csv

def ssm_create_parameter(name: str, value: str, variant: str) -> dict:
  ssm_client = boto3.client('ssm')

  return ssm_client.put_parameter(
    Name=name,
    Value=value,
    Type=variant,
    Tier='Standard',
    DataType='text')

def parser() -> dict:
  parser = argparse.ArgumentParser()
  parser.add_argument('--profile', type=str, required=True)
  parser.add_argument('--region', type=str, required=True)
  parser.add_argument('--file', type=str, required=True)
  return parser.parse_args()

def main():
  args: dict = parser()
  boto3.setup_default_session(profile_name=args.profile, region_name=args.region)
  filename = args.file

  with open(filename, 'r') as csvfile:
    datareader = csv.DictReader(csvfile)
    for row in datareader:
      print(f"Creating parameter: {row['name']}\nStatus: {ssm_create_parameter(row['name'], row['value'], row['type'])}")

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'Unexpected error: {e}')
