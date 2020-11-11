import time
from datetime import datetime, timedelta

import boto3
import operator
import sys

Region2 = raw_input("Enter the Destination region in which you want to restore db: ") 
instancename = raw_input("Enter the DBInstanceIdentifier: ")
subnetgroupname = raw_input("Enter the Db Subnet group name: ")
dbstoragetype =raw_input("Enter storage type for Db: ")
portnumber = raw_input("Enter the port number: ")
securitygroupid = raw_input("Enter the id of the security group: ")
dbinstanceclass =raw_input("Enter the db instance class: ")


client_Region2 = boto3.client("rds", region_name=Region2)


def execute():
    today = datetime.now().strftime("%d-%m-%Y")

    # Fetching latest snapshot of RDS that is to be restored in DR region
    print("Fetching ARN of latest Snapshot from " + Region2 )
    response = client_Region2.describe_db_snapshots(
        DBInstanceIdentifier=instancename,
        SnapshotType="manual"
    )
    # Sorting the response according to snapshot_creation_time to get the most recent snapshot
    snapshots_list = {}
    for snapshot in response['DBSnapshots']:
        if snapshot['Status'] != 'available':
            continue
        snapshots_list[snapshot['DBSnapshotIdentifier']] = snapshot['SnapshotCreateTime']
    snapshots_list_sorted = sorted(snapshots_list.items(), key=operator.itemgetter(1), reverse=True)
    latest_snapshot_name = snapshots_list_sorted[0][0]
    
    # Fetching the arn of the latest snapshot
    result = client_Region2.describe_db_snapshots(
        DBSnapshotIdentifier=latest_snapshot_name,
        SnapshotType="manual"
    )
    latest_snapshot_arn=result["DBSnapshots"][0]["DBSnapshotArn"]
    print("Latest snapshot name is: ", latest_snapshot_name)
    print("Latest snapshot arn is: ", latest_snapshot_arn)

    # Restoring the RDS from the latest snapshot also, specify KmsKeyId if db snapshot is encrypted
    # You may modify the following values acc. to your snapshot specs
    print("Restoring the RDS from the latest snapshot",latest_snapshot_name)
    restore_response = client_Region2.restore_db_instance_from_db_snapshot(
        DBInstanceIdentifier=instancename,
        DBSnapshotIdentifier=latest_snapshot_name,
        DBInstanceClass=dbinstanceclass,
        Port=portnumber,
        DBSubnetGroupName=subnetgroupname,
        MultiAZ=False,
        PubliclyAccessible=False,
        CopyTagsToSnapshot=True,
        StorageType=dbstoragetype,
        VpcSecurityGroupIds=[
        securitygroupid
        ],
        EnableIAMDatabaseAuthentication=False
    )
    status_response = client_Region2.describe_db_instances(
        DBInstanceIdentifier=instancename
    )
    status = status_response["DBInstances"][0]["DBInstanceStatus"]
    print("The current status of Database instance is now: ",status)
    print("Restoration of RDS is now in progress and database instance will be available in sometime in AWS Console")
    print("Script executed sucsessfully ! ")
        
if __name__ == "__main__":
    execute()

