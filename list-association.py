#!/usr/bin/python3
import argparse
import boto3

#filters = [{"Key":"InstanceId","Values":["i-04ec90bad4199a1bb","i-0596183e58a5b351d","i-01e07bdd990d3cb25","i-00629fb8ad833af7b","i-04ea72810683a4d56","i-0009b0591873f97b7","i-02a2f94b30f779958","i-057d8513d674ea1fa","i-04d0627424b974dbd","i-002faaa451cbe4cb1","i-0009fe064b45cbd51","i-0036785cd5ac4d9f6","i-050a7f56584592262","i-053b736138a371d26","i-01ccd315d7a7eb2a9","i-00a8f1a0d0fc3d35b","i-0171c6a5683ed515e","i-052dc7cc0472a977d","i-008f6e3339671aeea","i-00eb5719cadb2a8ad","i-014cb9895e165c2f8","i-06a5715b8331a5c02","i-019e23d64975033ca","i-051a43e2ec6cde7f0","i-01b8d0df3af7b15d2","i-0694d1220827c586c","i-0453d9e15ba343c2f","i-00a88abf66163710b","i-058d144520eaa79c1","i-0642b512cb72f50ff","i-01c132a7d3c37bca4","i-0693334609361bf7b","i-03ab481cd942341d0","i-0019aa5fe74996c92","i-036a3cd7a28135ce1","i-039857f956832838e","i-0440047ed55886f3d","i-0500c68b1f376b101","i-0131868870fb7c2b6","i-0483f958fb0eea519","i-065fdd3f80e79a4c3","i-00277bd7543955555","i-02fd140fe6459ca10","i-01b0884ee505f2e9d","i-0304d505a3cc0c185","i-00edeecf7afe75616","i-005b97131727d7d6a","i-02fb2bc22a03835d1","i-0406f91306e4ff774","i-03a433dcd02507425"],"Type":"Equal"},{"Key":"ComplianceType","Values":["Patch"],"Type":"Equal"}]


filters = [{"Key":"InstanceId","Values":["i-00277bd7543955555","i-02fd140fe6459ca10","i-01b0884ee505f2e9d","i-0304d505a3cc0c185","i-00edeecf7afe75616","i-005b97131727d7d6a","i-02fb2bc22a03835d1","i-0406f91306e4ff774","i-03a433dcd02507425"],"Type":"Equal"},{"Key":"ComplianceType","Values":["Patch"],"Type":"Equal"}]
def ssm_get_association_status(filters: dict) -> dict:
  client = boto3.client("ssm")
  return client.list_compliance_summaries(Filters = filters)


def parser() -> dict:
  parser = argparse.ArgumentParser()
  parser.add_argument('--profile', type=str, required=True)
  parser.add_argument('--region', type=str, required=True)
  return parser.parse_args()

def main():
  args: dict = parser()
  boto3.setup_default_session(profile_name=args.profile, region_name=args.region)
  print(ssm_get_association_status(filters))


if __name__ == '__main__':
  main()
