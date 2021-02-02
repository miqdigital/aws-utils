# Introduction

We realized that using S3 select we can run a lot of validations and also run ad-hoc filtering on the data available in S3.

The major use case which got resolved from this script is data validation and thus has helped us do this in a cost-effective manner.



# Requirements to run this script

* Install Python >=v3
* Install Pip3 module
* Install AWS CLI on Windows (https://docs.aws.amazon.com/cli/latest/userguide/awscli-install-windows.html) / Ubuntu users would do using pip install awscli --upgrade
* Install Boto using: pip3 install boto3
* Run the following to configure aws: aws configure



# Execution

Once the pre-requisites are installed, then starts the execution.


## Here are the different examples to run the file:

* Select all rows from a path where column _88 is VIEW_DETECTED and get [1st column, 2nd column, 20th coulmn] from the schema, as well save it to a file 'feed.csv", then we would run it using the following – query: "select _1, _2, _20 from s3object s where _88 = 'VIEW_DETECTED' "

```python
python3 s3_executor.py -b "bucket-name" -p "path/to/files/" -d TAB -s "select _1, _2, _20  from s3object s where _88 = 'VIEW_DETECTED' " -o feed.csv
```


* Select all rows by applying the filter on Http Referral URL, where if we want to select the 2nd column and 3rd column with http_referral (5th column) has value with like '%it.eurosport.com%' -- query: "select _2, _3 from s3object s where _5 like '%it.eurosport.com%' "

```python
python3 s3_executor.py -b "bucket-name" -p "path/to/files/" -d TAB -s "select _2, _3 from s3object s where _5 like '%it.eurosport.com%' " -o feed_for_eurosport.csv
```


## More
Typing ```python3 s3_executor.py --help``` will give you the options.

