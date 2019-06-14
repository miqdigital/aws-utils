# Introduction

This function is for creating AMI as a backup for all required instances based on the tags and delete older AMI's and this can be used for Lambda as well with bit modification.

## Prerequisites

* Python library Pytz
* Python library Requests
* Lambda Role which you use requires EC2-Read access, AMI Full access and Resource Tagging access in case if you want to configure through Lambda
* All the instances which needs AMI backup has to be tagged and that tag will be used by Lambda function to identify those instances(here we are using tag Key:AMIBACKUPON, Value:yes)


## How it Works?

### ami_backup

This will delete AMI's older than number days you provide as input and creates the new AMI for an instance and same AMI will be tagged by fetching all tags from instance and tags the AMI, two extra tags DELETEON=yes and Snapshottag=yes will be added inorder to identify AMI's while tagging snapshots and deleting older AMI's.

Tag DELETEON=yes is used to identify the AMI's which are supposed to be deleted after given number of days.
Tag Snapshottag=yes is used to identify the AMI's of which Snapshots needs to be tagged.

Once the snapshots are tagged the tag Snapshottag=yes will be deleted from AMI.

## Exception handler:

* Script uses slack notification as exception handler which can also be replaced by SNS topic or email notification as per your convenience and this is optional parameter, if you provide slack parameter as "true" will post exceptions to slack else prints the same to stdout.


## Some of the examples to run the script

* To create AMI's for the instances having tag Key:AMIBACKUPON Value:yes in us-east-1 region and to delete AMI's/Snapshots created through this script, also which are older than 10 days and to post exception in slack

```python
 python ami_backup.py -r us-east-1 -d 10 -s true -c "#ami_bkp_lambda" -w "https://hooks.slack.com/*********/*****"
``` 
Please see the link for more information on how to generate webhook url for slack https://api.slack.com/incoming-webhooks

* To create AMI's for the instances having tag Key:AMIBACKUPON Value:yes in us-west-2 region and to delete AMI's/Snapshots created through this script, also which are older than 5 days and not to post slack message.

```python
 python ami_backup.py -r us-west-2 -d 5 
``` 
* Typing ```python ami_backup.py -h will give you the options```

### Modification For Lambda
Code changes are required for this script to make it comaptible with Lambda.

* Block that needs to be replaced, from line 226 to 257

```python
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
 ```
 
 * Replace above lines in the script with following two lines.
 
 ```python
 
 # To post message to slack
 
 def lambda_handler(event, context):
    amibkp('us-east-1', 10, true, '#channel_name', 'https://hook.slack.com/********/') # replace parameters according to your need
    
 # If you don't use slack   
 
 def lambda_handler(event, context):
    amibkp('us-east-1', 10, false, 'null', 'null')
    
```

Function uses two libraries(Pytz, Requests) other than AWS SDK provided, so for lambda we need to create deployment package along with the code and upload it to Lambda function. Please go through the official AWS [Documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) to know more about how to create deployment package.

## NOTE 
* We are using CloudWatch Event Rules to schedule the run of Lambda Function, two function blocks are used as most of the times we ran into exception "errorType": "UnboundLocalError","errorMessage": "local variable 'snapshotid' referenced before assignment" as assignment of Snapshot ID took some time for some of the AMI's.

