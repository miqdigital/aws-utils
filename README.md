# Introduction

This repository provides utilities which are used at MiQ.
MiQ has been using AWS tech stack as it's the backbone and has been using many utilities to help scale their product.

---
 Available Executors
---

# S3 Select Executor

This utility provides a set of python scripts to effectively run S3 Select commands on the AWS S3 files. 
Used for validation and ad hoc filtering. [Documentation](s3_select_executor/README.md)


# AMI Backup Executor

This function is for creating AMI as a backup for required instance and delete older AMI's based on the retention period we provide. Every AMI and EBS Snapshots created will inherit all tags from instance


# RDS Disaster Recovery
The scripts present can be used to setup disaster recovery for RDS in AWS. It creates a manual snapshot of the current db present in production(source) region, then copies that snapshot to the DR(destination) region and if the disaster occurs db can be restored from the snapshots present in the DR region.


---

# Contribution
We are happy to accept the changes that you think can help the utilities grow.

Here are some things to note:

* Raise a ticket for any requirement
* Discuss the implementation requirement or bug fix with the team members
* Fork the repository and solve the issue in one single commit
* Raise a PR regarding the same issue and attach the required documentation or provide a more detailed overview of the changes
 
