# Introduction
  
 This Lambda function is for creating AMI as a backup for all required instances based on the tags. We are using two functions which runs everyday once as per the schedule

## Prerequisites

* Python library Pytz
* Python library Requests
* Lambda Role which you use requires EC2-Read access, AMI Full access and Resource Tagging access
* All the instances which needs AMI to be created has to be tagged and that tag will be used by Lambda function to identify the instances(We are using tag Key:AMIBACKUPON, Value:yes) 

Function uses two libraries other than AWS SDK provided(Pytz, Requests), so we need to create deployment package along with the code and upload it to Lambda function. Please go through the official AWS [Documentation](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) to know more about how to create deployment package.



## Here are the different examples to run the file:

* Select all rows from a path where column _88 is VIEW_DETECTED and get [1st column, 2nd column, 20th coulmn] from the schema, as well save it to a file 'feed.csv", then we would run it using the following – query: "select _1, _2, _20 from s3object s where _88 = 'VIEW_DETECTED' "

```python
python s3_executor.py -b "bucket-name" -p "path/to/files/" -d TAB -s "select _1, _2, _20  from s3object s where _88 = 'VIEW_DETECTED' " -o feed.csv
```


* Select all rows by applying filter on Http Referral URL, where if we want to select the 2nd column and 3rd column with http_referral (5th column) has value with like '%it.eurosport.com%' -- query: "select _2, _3 from s3object s where _5 like '%it.eurosport.com%' "

```python
python s3_executor.py -b "bucket-name" -p "path/to/files/" -d TAB -s "select _2, _3 from s3object s where _5 like '%it.eurosport.com%' " -o feed_for_eurosport.csv
```


## More
Typing python s3_executor.py --help will give you the options.
