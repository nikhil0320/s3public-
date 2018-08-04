import os
import boto3
import requests
import json
import logging
from xhtml2pdf import pisa
import datetime

logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(os.environ.get('logLevel', 'INFO')))

s3 = boto3.resource('s3')
api_url = 'https://app.cloudability.com/api/1/reporting/cost/run.json'

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
def convertHtmlToPdf(sourceHtml, outputFilename):
    resultFile = open(outputFilename, "w+b")

    pisaStatus = pisa.CreatePDF(sourceHtml,dest=resultFile)
    resultFile.close()
    return pisaStatus.err

def lambda_handler(event, context):
    invoicelist = []
    Bucket = 'bucketforinventory'
    message = json.loads(event["Messages"][0]["Body"])
    accounts = message['WBS_Detils']['Account_No']
    email = message['WBS_Detils']['Email']
    for i in accounts:
        AWSDetails = ''
        params = set_params(i)
        response = requests.get(api_url, params)
        output = json.loads(response.text)
        for j in output['results']:
            AWSDetails+= f'<tr><td>{j["service_name"]}</td><td>{j["invoiced_cost"]}</td></tr>'
        applicationNumber = '764859'
        ApplicationName = 'Test-APP'
        WBSNo = message['WBS_Detils']['WBSNumber']
        SponserPPMD = 'Demo-SpN-PPMD'
        startDate = output['meta']['dates']['start'].strip('T')
        endDate = output['meta']['dates']['end'].strip('T')
        period = f'{startDate}-{endDate}'
        AllTotal =  "$500.25"
        ThirdPartySoftware = "100"
        total = output['meta']['aggregates'][0]['value']
        todayDate = str(datetime.date.today())
        ThirdPartySoftwareTotal = "None"
        sourceHtml = "<!DOCTYPE html> <html> <head> <style> table { font-family: arial, sans-serif; border-collapse: collapse; width: 100%; } tr,td { border: 1px solid black; text-align: left; padding: 5px; } th { border: 1px solid black; text-align: center; padding: 5px;} </style> </head> <body> <p>Your team has incurred the following costs this quarter.Your WBS will be charged by the end of the week</p> <table> <tbody> <tr> <th colspan=2>CBCAP Quarterly Invoice</th> </tr> <tr> <td>InvoiceDate</td><td>"+todayDate+"</td> </tr> <tr> <td>Application Number</td> <td>"+applicationNumber+"</td> </tr> <tr> <td>Application Name</td> <td>"+ApplicationName+"</td> </tr> <tr> <td>WBS</td><td>"+WBSNo+"</td> </tr> <tr> <td>Sponser PPMD </td> <td>"+SponserPPMD+"</td> </tr> <tr> <td>Billing Period</td> <td>"+period+"</td> </tr> <tr> <td colspan=2></td> </tr> <tr> <th style = "'float:left; border:none'">Estimate Total</th> <th>"+AllTotal+"</th> </tr> <tr> <td colspan=2></td> </tr> <tr> <td colspan=2>Hosting Details:</td> </tr> <tr> <td colspan=2>"+AWSDetails+"</td> </tr> <tr> <td colspan=2></td> </tr> <tr> <td>Hosting Total</td> <td>"+total+"</td> </tr> <tr> <td colspan=2>3rd party licence details:</td> </tr> <tr> <td colspan=2>"+ThirdPartySoftware+"</td> </tr> <tr> <td>3rd party licenceTotal</td> <td>"+ThirdPartySoftwareTotal+"</td> </tr> </tbody> </table> <p>copyrights</p> </body> </html>"
        outputFilename = f'/tmp/{i}.pdf'
        convertHtmlToPdf(sourceHtml, outputFilename)
        invoice = f'invoice/{i}.pdf'
        s3.meta.client.upload_file(outputFilename , Bucket, invoice)
        invoicelist.append(invoice)
        print(invoicelist)
    #Details = '{"Email":"'+email+'","Bucket":"'+Bucket+'","Invoices":'+str(invoicelist)+'}'
    return email, Bucket, invoicelist






