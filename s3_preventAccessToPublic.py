#!/usr/bin/env python
"""
s3_preventAccessToPublic.py lambda module for preventing public access to S3 Buckets and Objects

Description:
Sample event is on this module directory(event.json). This module is designed to handle the following events:
-CreateBucket

"""
import os
import botocore
from utils.common import get_config, notify_email, get_aws_resource
from utils.logger import LoggerUtils as logger

# global variables
s3Bucket = os.environ['CONF_S3BUCKET']
s3Key = os.environ['CONF_DenyPolicy']
defaultDenyPolicy = get_config(s3Bucket, s3Key)
bucketList = get_config(s3Bucket, {subscriberAccountId}.json)
toEmail = os.environ['ToEmail']
fromEmail = os.environ['FromEmail']
roleName = os.environ['ROLE_NAME']
notification = True if os.environ['Notifications'] == 'True' else False

logger.setLevel()

def existing_bucket(bucketName, s3, subscriberAccountId, awsRegion):
    """ This function parses the bucketpolicy on an existing bucket and also identifies exceptional buckets """
    try:
        exceptionalBucket = bucketList['publiclyAccessibleBuckets']
        if bucketName in exceptionalBucket:
            logger.debug(f'Found the bucket: {bucketName} in {awsRegion} in the exceptions bucket list')
    except Exception as e:
        logger.error(f'Got error: {e} while fetching exceptional bucket')
        raise e

def replace_resource_arn_with_bucketName(bucketName, defaultDenyPolicy):
    """ This function fetches the deny policy from the CONF_S3BUCKET, and replaces the resource arn in the statements with the bucketName """
    try:
        for resource in defaultDenyPolicy['statement']['resource']:
            if resource in ['arn:aws:s3:::examplebucket/*', 'arn:aws:s3:::examplebucket']:
                replacingWithBucketName = resource.replace("examplebucket", bucketName)
                logger.info(f'Replacing examplebucket in the defaultDenyPolicy with {bucketName}')
                newBucketDenyPolicy = defaultDenyPolicy.write(replacingWithBucketName)
    except Exception as e:
        logger.debug(f'Got error: {e} while replacing the resource ARN with bucket name')


def apply_policy_to_new_bucket(bucketName, s3, newBucketDenyPolicy, subscriberAccountId, awsRegion):
    """ This function enforces bucket policy on the new bucket """
    try:
        s3.put_bucket_policy(Bucket=bucketName, Policy=newBucketDenyPolicy)
        message = 'Applied preventPublicAccessPolicy to the bucket: {bucketName} in the {subscriberAccountId} account in the {awsRegion} region'
        logger.debug(f'Bucket policy applied successfully and send an email notification')
        notify_email(toEmail, fromEmail, message)
    except Exception as e:
        message = f'Got error: {e} while applying the bucket policy to the bucket: {bucketName} in the {subscriberAccountId} account in the {awsRegion} region'
        logger.error(message)
        notify_email(toEmail, fromEmail, message)
        logger.debug(f'Notifying the recepient of the error')
        raise e

def lambda_handler(event, context):
    """ This is the main lambda function """
    subscriberAccountId = event['account']
    logger.debug(f'Found the subscriber account: {subscriberAccountId}')
    awsRegion = event['detail']['awsRegion']
    logger.debug(f'Found the aaccount: {awsRegion}')
    sessionName = context.function_name
    logger.debug(f'Found the session: {sessionName}')
    eventName = event['detail']['eventName']
    logger.debug(f'Found the event {eventName}')
    bucketName = event['detail']['requestParameters']['bucketName']
    logger.debug(f'Found the bucket: {bucketName}')

    s3 = get_aws_client('s3', subscriberAccountId, awsRegion, roleName, sessionName)

    if eventName == 'createBucket':
        logger.info(f'Executing the Lambda function as the event is {eventName}')
        replace_resource_arn_with_bucketName(bucketName, defaultDenyPolicy)
        apply_policy_to_new_bucket(bucketName, s3, newBucketDenyPolicy, subscriberAccountId, awsRegion)

    elif eventName in ['PutBucketPolicy', 'DeleteBucketPolicy']:
        logger.info(f'Executing the Lambda function as the event is {eventName}')
        existing_bucket(bucketName, s3, subscriberAccountId, awsRegion)
