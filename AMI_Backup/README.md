# Introduction

This function is for creating AMI as a backup for all required instances based on the tags and delete older AMI's and this can be used for Lambda as well with bit modification.

## Prerequisites

* Python library Pytz
* Python library Requests
* Lambda Role which you use requires EC2-Read access, AMI Full access and Resource Tagging access in case if you want to configure through Lambda
* All the instances which needs AMI backup has to be tagged and that tag will be used by Lambda function to identify those instances(here we are using tag Key:AMIBACKUPON, Value:yes)

Function uses two libraries(Pytz, Requests) other than AWS SDK provided, so for lambda we need to create deployment package along with the code and upload it to Lambda function. Please go through the official AWS [Documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) to know more about how to create deployment package.


## How it Works?

### AMI-Backup.py 

This will delete AMI's older than number days you provide as input and creates the new AMI for an instance and same AMI will be tagged by fetching all tags from instance and tags the AMI, two extra tags DELETEON=yes and Snapshottag=yes will be added inorder to identify AMI's while tagging snapshots and deleting older AMI's.

Tag DELETEON=yes is used to identify the AMI's which are supposed to be deleted after given number of days.
Tag Snapshottag=yes is used to identify the AMI's of which Snapshots needs to be tagged.

Once the snapshots are tagged the tag Snapshottag=yes will be deleted from AMI

Number of days to keep the AMI is an argument along with the region, modify those two arguments as per your requirement, please refer lambda handler block(line 145).

## Exception handler:

* Both the function uses slack notification as exception handler which can also be replaced by SNS topic or email notification as per convenience and this optional parameter, if you provide -s true, this will post exception details to slack else prints the same to stdout.

## NOTE 
* We are using CloudWatch Event Rules to schedule the run of Lambda Function, two function blocks are used as most of the times we ran into exception "errorType": "UnboundLocalError","errorMessage": "local variable 'snapshotid' referenced before assignment" as assignment of Snapshot ID took some time for some of the AMI's.

## Some of the examples to run the script

* To create AMI's for the instances having tag Key:AMIBACKUPON Value:yes in us-east-1 region and to delete AMI's/Snapshots created through this script, also which are older than 10 days and to post exception in slack

```python
 python checsyntax.py -r us-east-1 -d 10 -s true -c "#ami_bkp_lambda" -w "https://hooks.slack.com/*********/*****"
``` 
Please the link for more information on how to generate webhook url for slack https://api.slack.com/incoming-webhooks

* To create AMI's for the instances having tag Key:AMIBACKUPON Value:yes in us-west-2 region and to delete AMI's/Snapshots created through this script, also which are older than 5 days and not to post slack message.

```python
 python checsyntax.py -r us-west-2 -d 5 
``` 



