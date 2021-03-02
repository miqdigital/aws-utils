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

* Select a column from JSON Document example:
```python
python3 s3_executor.py -b "bucket-name" -p "path/to/files/" -c JSON -s "SELECT * FROM s3object[*].employee_names s" -comp None -d None
```
The above query tries to get the key from top level object which has a key as "employee_names"


## More
Typing ```python3 s3_executor.py --help``` will give you the options:

```sh
usage: s3_executor.py [-h] -b --bucket -p --prefix -comp --compression [-c --ctype] [-d --delimiter] -s --sql [-o --outputfile] [-exc --exclude] [-e --throwerror]

Provide S3 details: example python s3_executor.py -b "bucket-name" -p "path/to/file/mysample-file.tsv.gz" -d TAB -s "select * from s3object s where _88 != 'VIEW_DETECTED' limit 10"

optional arguments:
  -h, --help           show this help message and exit
  -b --bucket          Provide the bucket name, for example: bucket-name
  -p --prefix          Provide the prefix - till the folder, for example: path/to/file/mysample-file.tsv.gz
  -comp --compression  Is the compression available - GZIP/None/BZIP2
  -c --ctype           Content Type of the file - CSV/JSON/Parquet
  -d --delimiter       Provide the Delimiter - COMMA/TAB
  -s --sql             Provide the SQL to be executed, for example: select _1, _2, _20 from s3object s where _88 != 'VIEW_DETECTED' limit 10
  -o --outputfile      Provide the filename to dump the records fetched
  -exc --exclude       Provide the file regex to exclude
  -e --throwerror      Boolean value true/false - which determines whether to throw error while processing
```

