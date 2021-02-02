import operator
from datetime import datetime

import boto3

Region2 = input("Enter the Destination region in which you want to restore db: ")
clustername = input("Enter the DBClusterIdentifier: ")
subnetgroupname = input("Enter the Db Subnet group name: ")
kmskeyid = input("Enter the KMS Key id: ")
dbengine = input("Enter the db engine: ")
portnumber = input("Enter the port number: ")
securitygroupid = input("Enter the id of the security group: ")
clusternameinstance = input("Enter the name for Db instance i.e. DBInstanceIdentifier: ")
dbinstanceclass = input("Enter the db instance class: ")
dbinstanceidentifier = input("Enter the db instance identifier: ")

client_region_2 = boto3.client("rds", region_name=Region2)


def execute():
    today = datetime.now().strftime("%d-%m-%Y")

    # Fetching latest snapshot of RDS that is to be restored in DR region
    print(("Fetching ARN of latest Snapshot from " + Region2))
    response = client_region_2.describe_db_cluster_snapshots(
        DBClusterIdentifier=clustername,
        SnapshotType="manual"
    )
    # Sorting the response according to snapshot_creation_time to get the most recent snapshot
    snapshots_list = {}
    for snapshot in response['DBClusterSnapshots']:
        if snapshot['Status'] != 'available':
            continue
        snapshots_list[snapshot['DBClusterSnapshotIdentifier']] = snapshot['SnapshotCreateTime']
    snapshots_list_sorted = sorted(list(snapshots_list.items()), key=operator.itemgetter(1), reverse=True)
    latest_snapshot_name = snapshots_list_sorted[0][0]

    # Fetching the arn of the latest snapshot
    result = client_region_2.describe_db_cluster_snapshots(
        DBClusterSnapshotIdentifier=latest_snapshot_name,
        SnapshotType="manual"
    )
    latest_snapshot_arn = result["DBClusterSnapshots"][0]["DBClusterSnapshotArn"]
    print(("Latest snapshot name is: " + latest_snapshot_name))
    print(("Latest snapshot arn is: " + latest_snapshot_arn))

    # Restoring the RDS from the latest snapshot also, specify KmsKeyId if db snapshot is encrypted
    # You may modify the following values acc. to your snapshot specs
    print(("Restoring the RDS cluster from the latest snapshot" + latest_snapshot_name))
    restore_response = client_region_2.restore_db_cluster_from_snapshot(
        DBClusterIdentifier=clustername,
        SnapshotIdentifier=latest_snapshot_name,
        Port=portnumber,
        DBSubnetGroupName=subnetgroupname,
        KmsKeyId=kmskeyid,
        Engine=dbengine,
        Tags=[
            {
                'Key': 'Function',
                'Value': 'RDS'
            },
        ],
        VpcSecurityGroupIds=[
            securitygroupid
        ],
        EnableIAMDatabaseAuthentication=False
    )
    status_response = client_region_2.describe_db_clusters(
        DBClusterIdentifier=clustername
    )
    print(status_response)
    status = status_response["DBClusters"][0]["Status"]
    print(("The current status of Cluster: ", status))
    print("Restoration of RDS Cluster is now in progress")

    # You may modify the following values acc. to your instance specs
    print("Now creating the db instance for the cluster")
    instance_response = client_region_2.create_db_instance(
        DBInstanceIdentifier=dbinstanceidentifier,
        DBInstanceClass=dbinstanceclass,
        Engine=dbengine,
        PubliclyAccessible=False,
        DBSubnetGroupName=subnetgroupname,
        DBClusterIdentifier=clustername
    )
    print(instance_response)
    print("Restoration of RDS is now in progress and database instance will be available in sometime in AWS Console")
    print("Script executed successfully ! ")


if __name__ == "__main__":
    execute()
