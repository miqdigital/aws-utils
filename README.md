# Introduction

This repository provides utilities which are used at MiQ.
MiQ has been using AWS tech stack as it's the backbone and has been using many utilities to help scale their product.


# Available Tools

## S3 Select Executor

This utility provides a set of python scripts to effectively run S3 Select commands on the AWS S3 files. 
Used for validation and ad hoc filtering. [Documentation](s3_select_executor/README.md)

## AMI Backup

This function is for creating AMI as a backup for required instance and delete older AMI's based on the retention period we provide. Every AMI and EBS Snapshots created will inherit all tags from instance

---

# Contribution
We are happy to accept the changes that you think can help the utilities grow.

Here are some things to note:

* Raise a ticket for any requirement
* Discuss the implementation requirement or bug fix with the team members
* Fork the repository and solve the issue in one single commit
* Raise a PR regarding the same issue and attach the required documentation or provide a more detailed overview of the changes
