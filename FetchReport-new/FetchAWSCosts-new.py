import os
import boto3
import requests
import json
import logging
from xhtml2pdf import pisa
import datetime
from jinja2 import Environment, FileSystemLoader

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(os.environ.get('logLevel', 'INFO')))

j2_env = Environment(loader=FileSystemLoader(THIS_DIR), trim_blocks=True)

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
    #message = json.loads(event["Messages"][0]["Body"])
    accounts = event['WBS_Detils']['Account_No']
    email = event['WBS_Detils']['Email']
    for i in accounts:
        AWSDetails = ''
        params = set_params(i)
        response = requests.get(api_url, params)
        output = response.json()
#        output = json.loads(response.text)
        for j in output['results']:
            if j["invoiced_cost"] == '$0.00':
                pass
            else:
                AWSDetails+= f'<tr><td>{j["service_name"]}</td><td class=costs>{j["invoiced_cost"]}</td></tr>'
        applicationNumber = '764859'
        ApplicationName = 'Test-APP'
        WBSNo = event['WBS_Detils']['WBSNumber']
        SponserPPMD = 'Demo-SpN-PPMD'
        InvoiceNumber = '3'
        sDate = datetime.datetime.strptime(output['meta']['dates']['start'].split('T')[0],'%Y-%m-%d')
        startDate = sDate.strftime('%B %Y')
        eDate = datetime.datetime.strptime(output['meta']['dates']['end'].split('T')[0],'%Y-%m-%d')
        endDate = eDate.strftime('%B %Y')
        period = f'{startDate} - {endDate}'
        AllTotal = "$500.56"
        ThirdPartySoftware = "<tr><td>Tablue</td><td class=costs >$100</td></tr>"
        total = output['meta']['aggregates'][0]['value']
        todayDate = str(datetime.date.today())
        ThirdPartySoftwareTotal = "$100"
        sourceHtml = j2_env.get_template('template2.html').render(todayDate=todayDate,
                                                                  applicationNumber=applicationNumber,
                                                                  ApplicationName=ApplicationName,
                                                                  AWSDetails=AWSDetails,
                                                                  WBSNo=WBSNo,
                                                                  SponserPPMD=SponserPPMD,
                                                                  InvoiceNumber=InvoiceNumber,
                                                                  period=period,
                                                                  AllTotal=AllTotal,
                                                                  total=total,
                                                                  ThirdPartySoftware=ThirdPartySoftware,
                                                                  ThirdPartySoftwareTotal=ThirdPartySoftwareTotal)
        outputFilename = f'/tmp/{i}.pdf'
        convertHtmlToPdf(sourceHtml, outputFilename)
        invoice = f'invoice/{i}.pdf'
        s3.meta.client.upload_file(outputFilename , Bucket, invoice)
        invoicelist.append(invoice)
    #Details = '{"Email":"'+email+'","Bucket":"'+Bucket+'","Invoices":'+str(invoicelist)+'}'
    return email, Bucket, invoicelist

