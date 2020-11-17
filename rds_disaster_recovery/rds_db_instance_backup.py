import time
from datetime import datetime, timedelta

import boto3
import operator
import sys

# Here source region(for prod) is Region1 and the destination region(for DR) is Region2
client_Region1 = boto3.client("rds", region_name=sys.argv[1])
client_Region2 = boto3.client("rds", region_name=sys.argv[2])


def execute():
    today = datetime.now().strftime("%d-%m-%Y")

    # Fetching latest Snapshot of RDS that is to be copied in Region2(DR region) from Region1(Prod region)
    print("Fetching ARN of latest Snapshot from Region1")
    response = client_Region1.describe_db_snapshots(
        DBInstanceIdentifier=sys.argv[3],
        SnapshotType="automated"
    )
    # Sorting the response according to snapshot_creation_time to get the most recent Snapshot
    snapshots_list = {}
    for snapshot in response['DBSnapshots']:
        if snapshot['Status'] != 'available':
            continue
        snapshots_list[snapshot['DBSnapshotIdentifier']] = snapshot['SnapshotCreateTime']
    snapshots_list_sorted = sorted(snapshots_list.items(), key=operator.itemgetter(1), reverse=True)
    latest_snapshot_name = snapshots_list_sorted[0][0]
    
    #Fetching the ARN of the latest Snapshot
    result = client_Region1.describe_db_snapshots(
        DBSnapshotIdentifier=latest_snapshot_name,
        SnapshotType="automated"
    )
    latest_snapshot_arn=result["DBSnapshots"][0]["DBSnapshotArn"]
    print("Latest Snapshot's name : "  + latest_snapshot_name)
    print("Latest Snapshot's ARN : " + latest_snapshot_arn)

    # Copy Snapshot to region 2 i.e. us-west-2 (DR region)
    # Specify KmsKeyId only if db snapshot is encrypted
    print("Started Copying of RDS Snapshot from region Region1 to Region2")
    client_Region2.copy_db_snapshot(
        SourceDBSnapshotIdentifier=latest_snapshot_arn,
        TargetDBSnapshotIdentifier=sys.argv[3]+ "-dr-" +today,
        CopyTags=True,
        KmsKeyId=sys.argv[4],
        SourceRegion=sys.argv[1],
    )

    # Check if Snapshot is successfully copied
    response = client_Region2.describe_db_snapshots(
        SnapshotType="manual", DBSnapshotIdentifier=sys.argv[3]+"-dr-" + today,
    )
    status = response["DBSnapshots"][0]["Status"]
    print('DEBUG: status of copying: ', status)
    
    while (status == "creating" or status == "pending"):
        print("Still copying snapshot.")
        time.sleep(60)

        response = client_Region2.describe_db_snapshots(
            SnapshotType="manual",
            DBSnapshotIdentifier=sys.argv[3]+"-dr-" + today,
        )
        arn_of_snapshot = response["DBSnapshots"][0]["DBSnapshotArn"]
        status = response["DBSnapshots"][0]["Status"]
        print("ARN of the snapshot copying in destination region: ", arn_of_snapshot)
        print("DEBUG: Status of copying: ", status)
        if(status == "available"):
            print("Snaphot is now in available state")
            break
    
    print("Copying completed.")
    
    # Sorting the Snapshots in us-west-2 region to fetch and delete older Snapshots
    print("Fetching ARNs of Snapshots from us-west-2 in a sorted manner")
    response = client_Region2.describe_db_snapshots(
        DBInstanceIdentifier=sys.argv[3],
        SnapshotType="manual"
    )
    # Sorting the response
    snapshots_list = {}
    for snapshot in response['DBSnapshots']:
        if snapshot['Status'] != 'available':
            continue
        snapshots_list[snapshot['DBSnapshotIdentifier']] = snapshot['SnapshotCreateTime']
    snapshots_list_sorted = sorted(snapshots_list.items(), key=operator.itemgetter(1), reverse=True)
    print("The sorted list of available Snapshots is:")
    for p in snapshots_list_sorted: print p[0]
    

    #Storing the Snapshots to be deleted in Result list(In this case we are retaining only latest 3 Snapshots, rest all are to be deleted)
    result = snapshots_list_sorted[3:]
    print("Now Deleting the Snapshots")

    if len(result)==0:
        print("There exists no Snapshots that needs to be deleted !")
    
    for doc in result:
        identifier_to_delete=doc[0]
        print("Snapshot identifier to be deleted : "+ identifier_to_delete)
        response = client_Region2.delete_db_snapshot(
            DBSnapshotIdentifier = identifier_to_delete
        )
        print("Snapshot identifier deleted : "+ identifier_to_delete)
    
    print("Script executed successfully")


if __name__ == "__main__":
    execute()
