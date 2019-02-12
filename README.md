# MiQ's aws-utils

This repository provides utilities which are used at MiQ.
MiQ has been using AWS tech stack as it's backbone and has been using many utilities to help scale their product.


## S3 Select Executor

This utility provides a set of python scripts to effectively run S3 Select commands on the AWS S3 files. 
Used for validation and ad hoc filtering. [Documentation](s3_select_executor/README.md)

## Lambda Function for AMI Backup with Retention Period

This function is for creating AMI as a backup for required instance and delete older AMI's based on the retention period we provide. Every AMI created will inherit selected tags from instance based on requirment.
