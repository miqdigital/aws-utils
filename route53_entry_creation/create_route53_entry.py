import boto3

#To update an existing entry in R53 use 'UPSERT' in 'Action'
Action = raw_input("Enter the Action you want to perform - CREATE/DELETE/UPSERT: ") 
Name = raw_input("Enter the full URL here with domain name:")
Value = raw_input("Mention IP or DNS name here: ")
Type = raw_input("Enter the type of record you want to create in R53- CNAME/A:")
HostedZoneId = raw_input("Enter the id of hosted zone in which entry need to be updated: ")	

client = boto3.client('route53')


def execute():
    response = client.change_resource_record_sets(
    ChangeBatch={
        'Changes': [
            {
                'Action':Action,
                'ResourceRecordSet': {
                    'Name':Name,
                    'ResourceRecords': [
                        {
                            'Value':Value,
                        },
                    ],
                    'TTL': 300,
                    'Type':Type,
                },
            },
        ],
    },
    HostedZoneId= HostedZoneId,
    )
    print(response)
    print("The R53 entry has been updated")

if __name__ == "__main__":
    execute()
