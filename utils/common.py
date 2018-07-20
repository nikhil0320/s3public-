#!/usr/bin/env python
"""
common AWS utility functions
"""
import os
import json
import boto3
from utils.logger import LoggerUtils as logger


def get_config(bucket, key):
    """
    Read json configurations stored on S3

    Args:
        bucket (string): Bucket name
        key (string): configuration file/path

    returns:
        configuration (json): configuration
    """
    try:
        s3 = boto3.resource('s3')
        obj = s3.Object(bucket, key)
        configuration = json.loads(obj.get()['Body'].read())
        return configuration
    except Exception as error:
        logger.error('Unexpected error occured while reading object from S3'
                     f'Error: {error}')
        raise error

def get_aws_client(resourceType, accountId, awsRegion, roleName,
                   sessionName):
    """
    This function Assumes role and returns a client

    Args:
        resourceType (string): Resource type to initilize (Ex: ec2, s3)
        accountId (string): Target account Id to assume role
        awsRegion (string): AWS region to initilize service
        roleName (string): Role name to assume
        sessionName (string): Assume role session name

    Returns:
        serviceClient (botocore client): botocore resource client

    """
    stsClient = boto3.client('sts')
    try:
        roleArn = f'arn:aws:iam::{accountId}:role/{roleName}'
        role = stsClient.assume_role(RoleArn=roleArn,
                                     RoleSessionName=sessionName)
        accessKey = role['Credentials']['AccessKeyId']
        secretKey = role['Credentials']['SecretAccessKey']
        sessionToken = role['Credentials']['SessionToken']
        serviceClient = boto3.client(resourceType, region_name=awsRegion,
                                     aws_access_key_id=accessKey,
                                     aws_secret_access_key=secretKey,
                                     aws_session_token=sessionToken)
        return serviceClient
    except Exception as error:
        logger.error('Unexpected Error occured while assuming role for'
                     f'Account: {accountId}, Error: {error}')
        raise error

def get_aws_resource(resourceType, accountId, awsRegion, roleName,
                     sessionName):
    """
    This function Assumes role based and returns a resource object

    Args:
        resourceType (string): Resource type to initilize (Ex: ec2, s3)
        accountId (string): Target account Id to assume role
        awsRegion (string): AWS region to initilize service
        roleName (string): Role name to assume
        sessionName (string): Assume role session name

    Returns:
        serviceResource (ServiceResource): botocore service resource
    """
    stsClient = boto3.client('sts')
    try:
        # generate roleArn based using accountId and roleName
        roleArn = f'arn:aws:iam::{accountId}:role/{roleName}'
        role = stsClient.assume_role(RoleArn=roleArn,
                                     RoleSessionName=sessionName)
        accessKey = role['Credentials']['AccessKeyId']
        secretKey = role['Credentials']['SecretAccessKey']
        sessionToken = role['Credentials']['SessionToken']
        serviceResource = boto3.resource(resourceType, region_name=awsRegion,
                                         aws_access_key_id=accessKey,
                                         aws_secret_access_key=secretKey,
                                         aws_session_token=sessionToken)
        return serviceResource
    except Exception as error:
        logger.error('Unexpected Error occured while assuming role for'
                     f'Account: {accountId}, Error: {error}')
        raise error

def notify_email(toEmail, fromEmail, message):
    """
    This function sends Email notification

    Args:
        toEmail (string): Recipient address
        fromEmail (string): Sender address (should be verified in SES)
        message (string): Email Body
    """
    emailRegion = os.environ.get('EmailRegion', 'us-east-1')
    notification = os.environ.get('Notification', 'True')

    try:
        if notification == 'True':
            sesClient = boto3.client('ses', region_name=emailRegion)
            sesClient.send_email(Source=fromEmail,
                                 Destination={'ToAddresses': [toEmail]},
                                 Message={
                                     'Subject':
                                     {'Data': os.environ['Email_Subject']},
                                     'Body': {'Text': {'Data': message}}
                                     }
                                )
            logger.debug(f'Email notification is send to {toEmail}')
            return True
        else:
            logger.info('Email notifications are disabled')
    except Exception as error:
        logger.error('Unexpected error occured while sending Email'
                     f'notifications, Error is {error}')

