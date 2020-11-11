# Introduction

For a production environment, it is important to take precautions so that you can recover if there’s an unexpected event. While Amazon RDS provides a highly available Multi-AZ configuration, it can’t protect from every possibility, such as a natural disaster, a malicious activity etc. So, its important to design and test a DR plan.
For more info refer,
https://aws.amazon.com/blogs/aws/new-whitepaper-use-aws-for-disaster-recovery/

The scripts present can be used to setup disaster recovery for RDS in AWS. 

## Prerequisites

* Python should be installed in the system (v2.7).
* To perform operations on RDS, if you are using an EC2 machine to host the script make sure the required AWS role is attached to that EC2 or if you are using this script in local then make sure the IAM user has necessary permissions
* Script should be modified by the user and populated with the values according to the user's db instance/cluster specifications.

## How it Works?

It works in two parts i.e. it creates a manual snapshot of the current db present in production(source) region, then copies that snapshot to the DR(destination) region and if the disaster occurs db can be restored from the snapshots present in the DR region. For Db instances, rds_db_instances_backup.py can be used for creating and copying the snapshot and rds_db_instances_restore.py can be used to restore the db in the DR region in the event of disaster, similarly for AWS Aurora cluster rds_aurora_cluster_backup.py and rds_aurora_cluster_restore.py can be used to solve the purpose.
### Note:
You can use cron to schedule the backup script to take snapshots/backup periodically.

## Some of the examples to run the script:

* To create manual snapshot of the db instance and copying it to the DR(destination) region, execute the following command, the command should include 4 parameters in the following order:
1. Source region
2. Destination region
3. Db cluster identifier name
4. KMS key id( only if the db is encrypted, otw this can be commented out)
```python
#in case of Db Instance
python rds_db_instances_backup.py us-east-1 us-west-2 prod-db arn:aws:kms:xxxx:xxxx:key/xxxxxxxxxxx  
```
or
```python
#in case of Db cluster
python rds_aurora_cluster_backup.py us-east-1 us-west-2 prod-db arn:aws:kms:xxxx:xxxx:key/xxxxxxxxxxx 
```

* To restore the Db in the event of disaster in the DR(destination) region, execute the following command, after execution of the command the script prompts the user for various inputs
```python
python rds_db_instances_restore.py #in case of Db instance
```
or
```python
rds_aurora_cluster_restore.py #in case of Db cluster
```

