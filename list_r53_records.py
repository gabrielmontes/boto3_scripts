#!/usr/bin/python3
import boto3
import argparse

def r53_list_records(domain: str) -> dict:
  route53 = boto3.client('route53')
  paginate_hosted_zones = route53.get_paginator('list_hosted_zones')
  paginate_resource_record_sets = route53.get_paginator('list_resource_record_sets')

  for zone_page in paginate_hosted_zones.paginate():
    for zone in zone_page['HostedZones']:
      if domain == zone['Name'].lower().rstrip('.'):
        for record_page in paginate_resource_record_sets.paginate(HostedZoneId = zone['Id']):
          for record in record_page['ResourceRecordSets']:
            if record.get('ResourceRecords'):
              for target in record['ResourceRecords']:
                yield record['Name'], record['TTL'], 'IN', record['Type'], target['Value']
            elif record.get('AliasTarget'):
                yield record['Name'], 300, 'IN', record['Type'], record['AliasTarget']['DNSName'], '; ALIAS'

def parser() -> dict:
  parser = argparse.ArgumentParser()
  parser.add_argument('--profile', type=str,required=True)
  parser.add_argument('--region', type=str, required=True)
  parser.add_argument('--domain', type=str, required=True)
  return parser.parse_args()

def main():
  args = parser()
  boto3.setup_default_session(profile_name=args.profile, region_name=args.region)
  for record in r53_list_records(args.domain):
    print(record)

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'Unexpected error: {e}')
