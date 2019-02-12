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
gets all the instance ID's which has tag AMIBACKUPON=yes and creates AMI one by one in a loop and same AMI will be tagged by fetching tags from instance (which can be achieved using instance describe function), along with this it adds two new tags    


## More
Typing python s3_executor.py --help will give you the options.
