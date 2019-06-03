# Introduction

This Lambda function is for creating AMI as a backup for all required instances based on the tags and delete older AMI's. We are using two functions which runs everyday once as per the schedule

## Prerequisites

* Python library Pytz
* Python library Requests
* Lambda Role which you use requires EC2-Read access, AMI Full access and Resource Tagging access
* All the instances which needs AMI backup has to be tagged and that tag will be used by Lambda function to identify those instances(here we are using tag Key:AMIBACKUPON, Value:yes)

Function uses two libraries(Pytz, Requests) other than AWS SDK provided, so we need to create deployment package along with the code and upload it to Lambda function. Please go through the official AWS [Documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) to know more about how to create deployment package.


## How it Works?

### AMI-Backup.py 

This will delete AMI's older than 10 days and creates the new AMI for an instance and same AMI will be tagged by fetching tags from instance, please refer script block from line 94 to 101 where it fetches TEAM/OWNER/PRODUCT/NAME Tag from instance and tags the AMI, you can replace/add the "Key" items in "if loop" to have your own list of tags and replace/add same set of tags/variables from line 112 to 131 and you can see two other tags DELETEON=yes and Snapshottag=yes which is required by function to identify AMI's while tagging snapshots and deleting older AMI's.

Tag DELETEON=yes is used to identify the AMI's which are supposed to be deleted after 10 days.
Tag Snapshottag=yes is used by Snapshot-tag.py to identify the AMI's of which Snapshots needs to be tagged.

Number of days to keep the AMI is an argument along with the region, modify those two arguments as per your requirement, please refer lambda handler block(line 145).

### Snapshot-tag.py

Snapshot-tag.py tags the Snapshots of AMI which was created by AMI-Backup.py function, this will get all the AMI's having Snapshottag=yes has a tag and fetches the Snapshot ID's associated and tags by fetching required tags from AMI.

As I mentioned above you can replace/add the "Key" items in script block from line 51 to 56 and replace/add same set of tags/variables from line 69 to 87, once the snapshots are tagged the tag Snapshottag=yes will be deleted from AMI.

## NOTE
* We are using CloudWatch Event Rules to schedule the run of Lambda Function, Snapshot-tag.py is scheduled to run after AMI-Backup.py function completion, two functions are used as most of the times we ran into exception "errorType": "UnboundLocalError","errorMessage": "local variable 'snapshotid' referenced before assignment" as assignment of Snapshot ID took some time for some of the AMI's.

* Both the function uses slack notification as exception handler which can also be replaced by SNS topic or email notification as per convenience.
