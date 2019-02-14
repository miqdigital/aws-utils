#! /usr/bin/python

import boto3
import datetime
import pytz
import json
import requests

utc=pytz.UTC

slack_webhook_url = 'https://hooks.slack.com/************#########**********####'
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

        

def amibkp(region, days_del):

    client = boto3.client('ec2', region_name=region)
    ec2 = boto3.resource('ec2', region_name=region)
    
    response2 = client.describe_images(

            Filters=[
               {
                 'Name': 'tag:DELETEON',
                 'Values': [
                     'yes',
                 ]
               },
            ]
    )
    
    right_now_days_ago = datetime.datetime.today() - datetime.timedelta(days=days_del)
    old_date = right_now_days_ago.replace(tzinfo=utc)
    
    for i in response2['Images']:
      if (i['CreationDate'] < str(old_date)):
          image_id = i['ImageId']
          print image_id
          delimage = ec2.Image(image_id)
          snap_list = []
          for j in i['BlockDeviceMappings']:
              if 'Ebs'in j:
                 snap_list.append(j['Ebs']['SnapshotId'])
                 
          
          try:

            response = delimage.deregister()
            for k in range(len(snap_list)):
                snapshot = ec2.Snapshot(snap_list[k])
                reponse = snapshot.delete()  
                print "AMI snapshot ID deleted " + snap_list[k]
                

          except Exception as e:

            print(e)
            
            message = 'Error while deleting image \n\n ImageId: '+ image_id + '\n\n Region: '+ region + '\n\n Exception: '+  str(e)

            slack(message)


    response = client.describe_instances(
        Filters=[
            {
                'Name': 'tag:AMIBACKUPON',
                'Values': [
                    'yes',
                ]
            }
        ]
    )

    for i in response['Reservations']:
        for j in i['Instances']:
            print j['InstanceId']
            iid = j['InstanceId']
            instance = ec2.Instance(iid)
            for k in instance.tags:
                if k['Key'] == 'TEAM':
                   Teamtag = k['Value']
                if k['Key'] == 'OWNER':
                   Ownertag = k['Value']
                if k['Key'] == 'PRODUCT':
                   Producttag = k['Value']        
                if k['Key'] == 'Name':
                   Dscrip = k['Value']
                   
            try:
                       
                        image = instance.create_image(
                             Name=Dscrip + "-" + str(datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S.%f')),
                             NoReboot=True
                        )
                        tag = image.create_tags(
                              Tags=[
                                     {
                                      'Key': 'DELETEON',
                                      'Value': 'yes'
                                     },
                                     {
                                         'Key': 'TEAM',
                                         'Value': Teamtag
                                     },
                                     {
                                         'Key': 'PRODUCT',
                                         'Value': Producttag
                                     },
                                     {
                                         
                                         'Key': 'OWNER',
                                         'Value': Ownertag
                                     },
                                     {
                                         'Key': 'Snapshottag',
                                         'Value': 'yes'
                                     }
                              ]
                        )
                        
            except Exception as e:
                       
                       print(e)
                       
                       message = 'Error while creating image of instance\n\n InstanceId: '+ iid + '\n\n Region: '+ region + '\n\n Exception: '+ str(e)
                       
                       slack(message)       
                   


def lambda_handler(event, context):
    amibkp('us-east-1', 10)
    amibkp('eu-west-2', 10)
    amibkp('ap-southeast-1', 10)
    amibkp('eu-central-1', 10)
