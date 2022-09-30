#!/usr/bin/python3
import boto3
import argparse
import logging

def ws_get_directory() -> str:
  client = boto3.client("workspaces")
  paginator = client.get_paginator("describe_workspace_directories")
  for page in paginator.paginate():
    if 'Directories' not in  page:
      continue
    for directory in page['Directories']:
      yield directory

def ds_get_trusts(ID: str) -> str:
  client = boto3.client("ds")
  paginator = client.get_paginator("describe_trusts")
  for page in paginator.paginate(DirectoryId = ID):
    if not page['Trusts']:
      continue
    yield page

def create_tags(site: str) -> list:
  return (
           [
             {'Key': 'COST-CENTER', 'Value': 'SSL'}, \
             {'Key': 'SITE', 'Value': site.upper()}, \
             {'Key': 'OWNER', 'Value': 'IT-SERVICEDESK'}, \
             {'Key': 'BUSINESS-AREA', 'Value': 'PRODUCT'}
           ]
         )
  

def ws_create_workspace(directoryId: str, userName: str, bundleId: str, ebsKey:str, tags: list) -> dict:
  client = boto3.client("workspaces")
  workspace :dict = { 
                      'DirectoryId': directoryId, 
                      'UserName': f"URL\{userName}", 
                      'BundleId': bundleId, 
                      'VolumeEncryptionKey': ebsKey, 
                      'UserVolumeEncryptionEnabled': True,
                      'RootVolumeEncryptionEnabled': True,
                      'WorkspaceProperties': {
                        'RunningMode': 'AUTO_STOP',
                        'RunningModeAutoStopTimeoutInMinutes': 60,
                        'RootVolumeSizeGib': 80,
                        'UserVolumeSizeGib': 50
                        },
                        'Tags': tags,
                      }
  return client.create_workspaces(Workspaces = [workspace])
  
def parser() -> dict:
  parser = argparse.ArgumentParser()
  parser.add_argument('--profile', type=str,required=True)
  parser.add_argument('--region', type=str, required=True)
  parser.add_argument('--username', type=str, required=True)
  parser.add_argument('--site', type=str, required=True)
  return parser.parse_args()

def main():
  args = parser()
  directoryId: str = ""
  ebsKey: str = "KEY"
  bundleId: str = "BUNDLE"
  log = logging.getLogger()
  log.setLevel(logging.INFO)
  logging.basicConfig(format='%(asctime)s %(message)s ', datefmt='%Y-%m-%d %H:%M:%S')
  boto3.setup_default_session(profile_name=args.profile, region_name=args.region)

  # Find directory id from the new account:
  for directory in ws_get_directory():
    for trusts in ds_get_trusts(directory['DirectoryId']):
      for trust in trusts['Trusts']:
        if 'AD_URL' in trust['RemoteDomainName']:
          directoryId = trust['DirectoryId']

  # Create Workspace:
  if not directoryId:
    raise Exception('The directory id assigned to AD_URL has not been found.')
  else:
    log.info('Creating workspace: ')
    creation: dict = ws_create_workspace(directoryId, args.username, bundleId, ebsKey, create_tags('US'))
    log.info('Successfully created provisioning requests for: ' + str(creation['PendingRequests']))
    
    if creation['FailedRequests']:
      log.info('Failed to create provisioning requests for: ' + str(creation['FailedRequests']))
    
if __name__ == '__main__':
  main()
