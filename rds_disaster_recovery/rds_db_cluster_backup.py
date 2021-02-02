import operator
import sys
import time
from datetime import datetime

import boto3

# Here source region(for prod) is Region1 and the destination region(for DR) is Region2
client_Region1 = boto3.client("rds", region_name=sys.argv[1])
client_Region2 = boto3.client("rds", region_name=sys.argv[2])


def execute():
    today = datetime.now().strftime("%d-%m-%Y")

    # Fetching latest Snapshot of RDS that is to be restored in region 2 i.e. DR region
    print("Fetching the ARN of latest Snapshot from region1")
    response = client_Region1.describe_db_cluster_snapshots(
        DBClusterIdentifier=sys.argv[3],
        SnapshotType="automated"
    )
    # Sorting the response according to snapshot_creation_time to get the most recent Snapshot
    snapshots_list = {}
    for snapshot in response['DBClusterSnapshots']:
        if snapshot['Status'] != 'available':
            continue
        snapshots_list[snapshot['DBClusterSnapshotIdentifier']] = snapshot['SnapshotCreateTime']
    snapshots_list_sorted = sorted(list(snapshots_list.items()), key=operator.itemgetter(1), reverse=True)
    latest_snapshot_name = snapshots_list_sorted[0][0]

    # Fetching the ARN of the latest Snapshot to be copied
    result = client_Region1.describe_db_cluster_snapshots(
        DBClusterSnapshotIdentifier=latest_snapshot_name,
        SnapshotType="automated"
    )
    latest_snapshot_arn = result["DBClusterSnapshots"][0]["DBClusterSnapshotArn"]
    print(("Latest Snapshot's name : " + latest_snapshot_name))
    print(("Latest Snapshot's ARN : " + latest_snapshot_arn))

    # Copy snapshot to region 2 i.e. DR region
    # Specify KmsKeyId if db snapshot is encrypted
    print("Started Copying of RDS Snapshot from Region1 to Region2")
    client_Region2.copy_db_cluster_snapshot(
        SourceDBClusterSnapshotIdentifier=latest_snapshot_arn,
        TargetDBClusterSnapshotIdentifier=sys.argv[3] + "-dr-" + today,
        CopyTags=True,
        KmsKeyId=sys.argv[4],
        SourceRegion=sys.argv[1],
    )

    # Check if snapshot successfully copied
    response = client_Region2.describe_db_cluster_snapshots(
        SnapshotType="manual", DBClusterSnapshotIdentifier=sys.argv[3] + "-dr-" + today,
    )
    status = response["DBClusterSnapshots"][0]["Status"]
    print(('DEBUG: status of copying: ', status))

    while status == "copying":
        print("Still copying Snapshot")
        time.sleep(120)

        response = client_Region2.describe_db_cluster_snapshots(
            SnapshotType="manual",
            DBClusterSnapshotIdentifier=sys.argv[3] + "-dr-" + today,
        )
        status = response["DBClusterSnapshots"][0]["Status"]
        print(("DEBUG: Status of copying: ", status))
        if status == "available":
            print("Snapshot is now in available state")
            break

    print("Copying is completed")

    # Sorting the Snapshots in region 2 to fetch and delete older Snapshots
    print("Fetching Snapshots from Region 2 in a sorted manner in order to delete the older snapshots")
    response = client_Region2.describe_db_cluster_snapshots(
        DBClusterIdentifier=sys.argv[3],
        SnapshotType="manual"
    )
    # Sorting the response
    snapshots_list = {}
    for snapshot in response['DBClusterSnapshots']:
        if snapshot['Status'] != 'available':
            continue
        snapshots_list[snapshot['DBClusterSnapshotArn']] = snapshot['SnapshotCreateTime']
    snapshots_list_sorted = sorted(list(snapshots_list.items()), key=operator.itemgetter(1), reverse=True)
    print("The sorted list of available Snapshots in region2 is:")
    for p in snapshots_list_sorted:
        print(p[0])

    # Storing the Snapshots to be deleted in Result list(In this case we are retaining only latest 3 Snapshots,
    # rest all are to be deleted)
    result = snapshots_list_sorted[3:]
    print("Now Deleting the Snapshots")
    if len(result) == 0:
        print("There exists no Snapshots that needs to be deleted !")
    for doc in result:
        arn_to_delete = doc[0]
        print(("Snapshot ARN to be deleted : " + arn_to_delete))
        response = client_Region2.delete_db_cluster_snapshot(
            DBClusterSnapshotIdentifier=arn_to_delete
        )
        print(("Snapshot ARN deleted : " + arn_to_delete))

    print("Script executed successfully")


if __name__ == "__main__":
    execute()
