import argparse, boto3, csv, json, time, ast

def sqs_add_to_queue(url: str, message: str) -> dict:
  sqs_client = boto3.client('sqs')

  return sqs_client.send_message(
    QueueUrl=url,
    MessageBody=message,
    MessageGroupId='send_notification'
  )

def parser() -> dict:
  parser = argparse.ArgumentParser()
  parser.add_argument('--profile', type=str, required=True)
  parser.add_argument('--region', type=str, required=True)
  parser.add_argument('--url', type=str, required=True)
  parser.add_argument('--file', type=str, required=True)
  parser.add_argument('--timer', type=int, required=True)
  parser.add_argument('--lines', type=int, required=True)
  return parser.parse_args()

def main():
  args: dict = parser()
  boto3.setup_default_session(profile_name=args.profile, region_name=args.region)
  filename = args.file
  count: int = 0
  counter: int = 0

  with open(filename, 'r') as csvfile:
    datareader = csv.DictReader(csvfile)

    for row in datareader:
      count += 1
      counter += 1
      
      message = json.dumps({"event": "send_denied_notification_email", "payload": {"AAN": ast.literal_eval(row["template"]),"applicationId": row["application_id"]}})
      print(f"Sending message - {count}: {message}")
      #print(sqs_add_to_queue(args.url, json.loads(json.dumps(message))))
      #need validation of adding to the queue: status = sqs_add_to_queue() ? continue : waiter
      
      if counter == args.lines:
        time.sleep(args.timer)
        counter = 0

if __name__ == '__main__':
  try:
    main()
  except Exception as e:
    print(f'Unexpected error: {e}')
