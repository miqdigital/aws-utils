#! /usr/bin/python

import boto3
import datetime
import json
import requests


slack_webhook_url = 'https://hooks.slack.com/********###########***********######****'
slack_channel = '#channel name'
slack_username = 'AWS Lambda'


def slack(event):
    message = 'AMI_BKP_ALERT'
    payload = { 'channel': slack_channel,
                'username': slack_username,
                'text': message,
                'icon_emoji': ':aws_lambda:',
                'attachments': [ {
                  'color': 'danger',
                  'fields': [{'value': event}]
                } ]
            }
    r = requests.post(slack_webhook_url, data=json.dumps(payload))



def snaptag(region):    

    client = boto3.client('ec2', region_name=region)
    ec2 = boto3.resource('ec2', region_name=region)
    
    response2 = client.describe_images(

            Filters=[
               {
                 'Name': 'tag:Snapshottag',
                 'Values': [
                     'yes',
                 ]
               },
            ]
    )

    for i in response2['Images']:
          image_id = i['ImageId']
          print image_id
          descrip = i['Name']
          for k in i['Tags']:
                if k['Key'] == 'TEAM':
                   Teamtag = k['Value']
                if k['Key'] == 'OWNER':
                   Ownertag = k['Value']
                if k['Key'] == 'PRODUCT':
                   Producttag = k['Value']
              
          for j in i['BlockDeviceMappings']:  
            if 'Ebs'in j:  
              snapid =  j["Ebs"]["SnapshotId"]
              print snapid
              
              try:
                  
                  responsetag = client.create_tags(
                                Resources=[
                                        snapid,
                                ],
                                Tags=[
                                  {
                                    'Key': 'TEAM',
                                    'Value': Teamtag,
                                  },
                                  {
                                    'Key': 'OWNER',
                                    'Value': Ownertag
                                  },
                                  {
                                    'Key': 'PRODUCT',
                                    'Value': Producttag,
    
                                  },
                                  {
    
                                      'Key': 'Name',
                                      'Value': descrip,
    
                                  }    
                                ],
                )
    
              except Exception as e:

                    print(e)

                    message = 'Error while creating tags on one or more snapshots of AMI \n\n AMIId: '+ image_id  + '\n\n Region: '+ region + '\n\n Exception: '+ str(e)

                    slack(message)        

          responsedel = client.delete_tags(
                Resources=[
                   image_id,
                ],
                Tags=[
                       {
                         'Key': 'Snapshottag',
                         'Value': 'yes'
                       },
                ]            
          
          )                      


def lambda_handler(event, context):
    snaptag('us-east-1')
    snaptag('eu-west-2')
    snaptag('ap-southeast-1')
    snaptag('eu-central-1')
