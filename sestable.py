import os
import boto3

def lambda_handler(event, context):
    sesClient=boto3.client('ses')
    email = ""
    for i in event['results']:
        
        email += '<tr><td style="border:1px solid #dddddd;text-align:left; padding:8px;">'+i['service_name']+'</td> <td style="border:1px solid #dddddd;text-align:left; padding:8px;">'+i['invoiced_cost']+"</td></tr>"
        
    final_email = '<table><tr><th  style="border:1px solid #dddddd;text-align:left; padding:8px;">Service_Name</th><th style="border:1px solid #dddddd;text-align:left; padding:8px;">Cost</th></tr>'+email+'</table>'
    print(final_email)
    sesClient.send_email(
    Source='nikhil.linga@reancloud.com',
    Destination={
        'ToAddresses': [
            'nikhil.linga@reancloud.com'
        ]
    },
    Message={
        'Subject': {
            'Data': 'Test invoice '
        },
        'Body': {

            'Html': {
                'Data': final_email
            }
        }
    },
   )
   
