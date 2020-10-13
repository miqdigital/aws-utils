# Introduction

For a production environment, it is important to take precautions so that you can recover if there’s an unexpected event. While Amazon RDS provides a highly available Multi-AZ configuration, it can’t protect from every possibility, such as a natural disaster, a malicious activity etc. So, its important to design and test a DR plan.
The scripts present can be used to setup disaster recovery for RDS in AWS. 

## Prerequisites

* Python should be installed in the system.
* To perform operations on RDS, if using any EC2 machine to host the script make sure required AWS role is attached to the EC2,or if using in local make sure the IAM user has necassary permissions.
* Script should be modified by the user and populated with the values according to the user's db instance/cluster specifications.

## How it Works?

It works in two parts i.e. it creates a manual snapshot of the current db present in production(source) region, then copies that snapshot to the DR(destination) region and if the disaster occurs db can be restored from the snaphots present in the DR region. For Db instances, rds_db_instances_backup.py can be used for creating and copying the snaphot and rds_db_instances_restore.py can be used to restore the db in the DR region in the event of disater, similarly for AWS Aurora cluster rds_aurora_cluster_backup.py and rds_aurora_cluster_restore.py can be used to solve the purpose.
### Note:
You can use cron to schedule the backup script to take snapnshots/backup periodically.

## Some of the examples to run the script:

* To create manual snaphot of the db instance and copying it to the DR(destination) region, execute the following command(after altering the values according to db's specs in the script)
```python
python rds_db_instances_backup.py.py  #in case of Db instance
```
or
```python
python rds_aurora_cluster_backup.py #in case of Db cluster
```

* To restore the Db in the event of disaster in the DR(destination) region, execute the following command(after altering the values according to db's specs in the script)
```python
python rds_db_instances_restore.py #in case of Db instance
```
or
```python
rds_aurora_cluster_restore.py #in case of Db cluster
```

