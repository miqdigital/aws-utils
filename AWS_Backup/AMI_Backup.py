
#! /usr/bin/python

import argparse
import datetime
import json
import pytz
import requests
import boto3

Utc = pytz.UTC

def slack(event, channel, webhookurl):
    #This function is used to post message to slack
    message = 'AMI_BKP_ALERT'
    payload = {'channel': channel,
               'username': "AMI_BKP_SCRIPT",
               'text': message,
               'attachments': [{
                   'color': 'danger',
                   'fields': [{'value': event}]
                   }]
              }
    req = requests.post(webhookurl, data=json.dumps(payload))

def amibkp(region, days_del, slack_req, slack_channel, slack_webhook):
    """
    This function is the crucial function,
    fetches all the instances which has tag Key:AMIBACKUPON, Value:yes and creates AMI in a loop,
    along with propogating all the tags from instance to AMI to EBS Snapshots.
    Also, it deletes all the AMI's which was created through this script
    and older than number of days you provide as an argument.
    Parameters
    ----------
    region: string
          AWS region code.
    days: integer
          Number of days to keep AMI's before deleting.
    slack: string
          Optional argument.
          Passing this parameter as "true" will post the execption to slack if any.
    slack_channel: String
          Slack channel to where exceptions has to be posted
          Depends on the previous parameter "slack", this is required if slack is true.
    webhookurl: string
          Slack webhookurl to identify to which slack team exeception has to be posted?
          Depends on the previous parameter "slack", this is required if slack is true.
    Returns
    -------
    list
        Returns list of AMI's/Snapshots deleted and newly created AMI's/Snapshots.
    """
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
    old_date = right_now_days_ago.replace(tzinfo=Utc)

    for i in response2['Images']:
        if i['CreationDate'] < str(old_date):
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
                print e
                message = 'Error while deleting image\nImageId:'+image_id+' \
                                  \nRegion:'+region+'\nException:'+str(e)
                if slack_req == 'true':
                    slack(message, slack_channel, slack_webhook)
                else:
                    print message

    response = client.describe_instances(
        Filters=[
            {
                'Name': 'tag:AMIBACKUPON', #Tag used to identify list of Instances to be backed up.
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
            tag_key_list = []
            tag_value_list = []
            instance = ec2.Instance(iid)
            for k in instance.tags:
                tag_key_list.append(k['Key'])
                tag_value_list.append(k['Value'])
                if k['Key'] == 'Name':
                    dscrip = k['Value']
            try:
                image = instance.create_image(
                    Name=dscrip+ "-" +str(datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S.%f')),
                    NoReboot=True
                    )
                for l in range(len(tag_key_list)):
                    tag = image.create_tags(
                        Tags=[
                            {
                                'Key': tag_key_list[l],
                                'Value': tag_value_list[l]
                            }
                        ]
                    )

                tag = image.create_tags(
                    Tags=[
                        {
                            'Key': 'DELETEON', #Tag required to fetch all the AMI's to delete.
                            'Value': 'yes'
                        },
                        {
                            'Key': 'Snapshottag', #Tag required to fetch all the snapshots associated to AMI in order to tag those snapshots.
                            'Value': 'yes'
                        }
                    ]
                )
            except Exception as e:
                print e
                message = 'Error while creating image of instance\n\nInstanceId:'+ iid +' \
                            \n\n Region:'+ region +'\n\n Exception:'+ str(e)
                if slack_req == 'true':
                    slack(message, slack_channel, slack_webhook)
                else:
                    print message
    response3 = client.describe_images(
        Filters=[
            {
                'Name': 'tag:Snapshottag',
                'Values': [
                    'yes',
                    ]
            },
        ]
    )

    for i in response3['Images']:
        image_id = i['ImageId']
        print image_id
        descrip = i['Name']
        snap_tag_key_list = []
        snap_tag_value_list = []
        for k in i['Tags']:
            snap_tag_key_list.append(k['Key'])
            snap_tag_value_list.append(k['Value'])
        for j in i['BlockDeviceMappings']:
            if 'Ebs'in j:
                snapid = j["Ebs"]["SnapshotId"]
                print snapid
            try:
                for l in range(len(snap_tag_key_list)):
                    responsetag = client.create_tags(
                        Resources=[
                            snapid,
                        ],
                        Tags=[
                            {
                                'Key': snap_tag_key_list[l],
                                'Value': snap_tag_value_list[l],
                            }
                        ],
                    )
            except Exception as e:

                print e

                message = 'Error while creating tags on snapshots of AMI\nAMIId:'+image_id+' \
                            \nRegion:'+region+'\nException:'+ str(e)
                if slack_req == 'true':
                    slack(message, slack_channel, slack_webhook)
                else:
                    print message

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


def fetch_args():
    """
       Is an arguments parser which showcases all possible arguments this python function takes in.
    """
    parser = \
        argparse.ArgumentParser(description=''' Provide AWS region and number of days
                                to keep AMI and optional slack details:example
                                python AMI_Backup.py -r "us-east-1" -d 10 -s true -c "#AWS_BKP",
                                -w "https://hooks.slack.com/************" ''')
    parser.add_argument('-r', metavar='--region', required=True,
                        help='''Provide the AWS region code, for example:  us-east-1 ''')
    parser.add_argument('-d', metavar='--days', type=int, required=True,
                        help='''Number of days you want to keep AMI, for example: 10 ''')
    parser.add_argument('-s', metavar='--slack',
                        help='''Please provide true if you want to send exception to slack ''')
    parser.add_argument('-c', metavar='--slack_channel',
                        help='''Slack channel, for example: "#channel_name" ''')
    parser.add_argument('-w', metavar='--webhookurl',
                        help='''Slack webhook URL,
                        for example: "https://hooks.slack.com/************#########**********####",
                        see the link for information: https://api.slack.com/incoming-webhooks ''')

    return parser


if __name__ == '__main__':
    PARSER = fetch_args()
    ARGS = PARSER.parse_args()
    if ARGS.s == 'true' and not (ARGS.c and  ARGS.w):
        PARSER.error('If slack argument is true, it requires slack_channel and webhookurl')

    amibkp(ARGS.r, ARGS.d, ARGS.s, ARGS.c, ARGS.w)


