import boto3
import requests
import json
sqsClient = boto3.client('sqs')

api_url = 'https://app.cloudability.com/api/1/reporting/cost/run'

def set_params(accountnumber):
    parameters = {
        'auth_token':'rhfqSzcX2SmGmqNR2utg',
        'start_date':'beginning of last quarter',
       'end_date':'end of last quarter',
        'dimensions':' service_name',
      'metrics':'invoiced_cost',
        'sort_by':'invoiced_cost',
      'order':'desc',
    'filters':'service_name!=AWS CloudTrail,vendor_account_identifier=='+ accountnumber
    }
    return parameters

def lambda_handler(event, context):
    
    print(event)
    #queueUrl = 	"https://sqs.us-east-1.amazonaws.com/639015715993/cloudabiltyqueue"
    #rh = event["Messages"][0]["ReceiptHandle"]
    message = json.loads(event["Messages"][0]["Body"])
    accounts = message['WBS_Detils']['Account_No']
    for i in accounts:
        params = set_params(i)
        response = requests.get(api_url, params)
        output = response.text
        f = open('output.txt', 'w')
        f.write(str(output))
        f.close()

