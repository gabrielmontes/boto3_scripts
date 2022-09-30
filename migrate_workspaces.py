#!/usr/bin/python3
import boto3
import argparse
import logging
import time

# Replace:
# AD_URL
# EBS_KEY_NAME


def ws_create_workspaces(profile: str, region: str, provision: dict) -> dict:
  
  """ Ws_create_workspaces.
      Return dict of new workspaces.
  """

  boto3.setup_default_session(profile_name=profile, region_name=region)
  client = boto3.client("workspaces")
  return {} #client.create_workspaces(Workspaces=provision)


def ws_get_workspaces(profile: str, region: str) -> dict:
  
  """ Ws_get_workspaces.
      Return workspaces from the selected account.
  """

  boto3.setup_default_session(profile_name=profile, region_name=region)
  client = boto3.client("workspaces")
  paginator = client.get_paginator("describe_workspaces")
  for result in paginator.paginate():
    if 'Workspaces' not in result:
      continue
    for workspace in result["Workspaces"]:
      yield workspace

def ws_get_workspaces_state(profile:str, region: str, directoryId: str, users: list) -> bool:
  
  """ Ws_get_workspaces_state:
      Return boolean once the users are with available status.
  """

  boto3.setup_default_session(profile_name=profile, region_name=region)
  client = boto3.client("workspaces")
  response: dict = client.describe_workspaces(WorkspaceIds = users)
  result: dict = {}

  for value in response['Workspaces']:
    result.update({value['WorkspaceId']: False})
    if value['State'] == 'AVAILABLE':
      result.update({value['WorkspaceId']: True})
  
  return all(value == True for value in result.values())

def ws_get_tag(profile: str, region: str, workspace: str) -> list:
  
  """ Ws_get_tag: 
      Return tags from the user in PROD account.
  """
  
  boto3.setup_default_session(profile_name=profile, region_name=region)
  client = boto3.client("workspaces")
  return client.describe_tags(ResourceId=workspace)

def ws_get_directory(profile: str,region: str) -> str:
  
  """ Ws_get_directory:
      Return directories ID from the account.
  """
  
  boto3.setup_default_session(profile_name=profile, region_name=region)
  client = boto3.client("workspaces")
  paginator = client.get_paginator("describe_workspace_directories")
  for page in paginator.paginate():
    if 'Directories' not in  page:
      continue
    for directory in page['Directories']:
      yield directory

def ds_get_trusts(profile: str,region: str, ID: str) -> str:
  
  """ ds_get_trusts:
      return trusts from the new account.
  """
  
  boto3.setup_default_session(profile_name=profile, region_name=region)
  client = boto3.client("ds")
  paginator = client.get_paginator("describe_trusts")
  for page in paginator.paginate(DirectoryId = ID):
    if not page['Trusts']:
      continue
    yield page

def ws_data(directoryId: str, userName: str, bundleId: str, ebsKey:str, tags: list) -> dict:
  """ ws_data: 
      return dictionary with new workspace values:
  """

  workspace: dict = {
                      'DirectoryId': directoryId,
                      'UserName': f"AD_URL\{userName}",
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
  return workspace                      

def find_duplicate_workspaces(usWorkspaces: list, loansWorkspaces: list) -> set:
  
  """ Find_duplicate_workspaces: 
      Return duplicates between us and loans account.
  """

  usSet: set = set(usWorkspaces)
  loansSet: set = set(loansWorkspaces)
  return usSet.intersection(loansSet)

def parser() -> dict:
  """ Parser object: 
      This enables us to use the parameters from the cli.
  """

  parser = argparse.ArgumentParser()
  parser.add_argument('--fromProfile', type=str,required=True)
  parser.add_argument('--toProfile', type=str,required=True)
  parser.add_argument('--region', type=str, required=True)
  return parser.parse_args()

def main():
  args = parser()
  directoryId: str = ""
  loansUsers: dict = {}
  usUsers: dict = {}
  ebsKey: str = "EBS_KEY_NAME"
  bundleId: str = "BUNDLE_ID"
  log = logging.getLogger()
  log.setLevel(logging.INFO)
  logging.basicConfig(format='%(asctime)s %(message)s ', datefmt='%Y-%m-%d %H:%M:%S')

  # Find directory id from the new account:
  for directory in ws_get_directory(args.toProfile, args.region):
    for trusts in ds_get_trusts(args.toProfile, args.region, directory['DirectoryId']):
      for trust in trusts['Trusts']:
        if 'AD_URL' in trust['RemoteDomainName']:
          directoryId = trust['DirectoryId']

  # Create lists of users from both accounts:
  for usWorkspace in ws_get_workspaces(args.fromProfile, args.region):
    usUsers.update({usWorkspace['UserName']: usWorkspace['WorkspaceId']})
  for loansWorkspace in ws_get_workspaces(args.toProfile, args.region):
    loansUsers.update({loansWorkspace['UserName']: loansWorkspace['WorkspaceId']})

  # Find duplicates and remove them from us list:
  for duplicate in find_duplicate_workspaces(usUsers.keys(), loansUsers.keys()):
    usUsers.pop(duplicate)
  
  # Create Workspace:
  if not directoryId:
    raise Exception('The directory id assigned to AD_URL has not been found.')
  else:
    tags: list = []
    provision: list = []
    provision_count: int = 1
    workspacesId: list = []
    log.info("Creating workspace:")
    
    """ Loop to iterate over the US users without users already created in the
        the loans account. 
        
        1) We need to retrieve the tags from the PROD account to create them in the
        loans account.

        2) We will send 24 requests to create the workspaces, with retrieved values 
        from PROD account, nothing is hardcoded.

        3) We are going to  send the request with 24 new workspaces, and wait until
        the new workspaces are in the state of available.
        
        4) If the current 24 new workspaces are not avaible, we wait and retry 5 
        minutes later.

        5) Once the workspaces are available, we continue looping over the rest of
        the users.
    """
    
    for user, workspaceId in usUsers.items():
      tags = ws_get_tag(args.fromProfile, args.region, usUsers[user])
      provision.append(ws_data(directoryId,user,bundleId, ebsKey, tags['TagList']))
      provision_count += 1
      workspacesId.append(workspaceId)

      if provision_count > 10:
        #creation: dict = ws_create_workspaces(provision)
        log.info('Successfully created provisioning requests for: ' + str(creation['PendingRequests']))
        if creation['FailedRequests']:
          log.info('Failed to create provisioning requests for: ' + str(creation['FailedRequests'])))

        while True:
          log.info('Workspaces not available yet.')
          result: bool = False
          result = ws_get_workspaces_state(args.fromProfile, args.region, 'd-926723b804', workspacesId) 
          
          if result:
            log.info('The new workspaces have been created, now will continue.')
            provision_count = 0
            provision = []
            workspacesId = []
            time.sleep(100)
            break
          
if __name__ == '__main__':
  main()
