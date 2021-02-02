import boto3


s3 = boto3.client('s3')


def write_to_file(r, output_file):
    """
    This function would write the output to the file.


    Parameters
    ----------
    r: records object
          the select object content which contains the Payload of the fetch.
    output_file: string
          The file name to which the output can be appended.

    """
    with open(output_file, encoding='utf-8', mode='a') as f:
        for event in r['Payload']:
            if 'Records' in event:
                records = event['Records']['Payload'].decode('utf-8')
                if not str(records).encode('utf-8') == "":
                    f.write(records)


def write_to_console(r):
    """
    This function would write the output to the console.


    Parameters
    ----------
    r: records object
          the select object content which contains the Payload of the fetch.

    """
    for event in r['Payload']:
        if 'Records' in event:
            records = event['Records']['Payload'].decode('utf-8')
            print(records.encode('utf-8'))


def perform(bucket, prefix, expression, compression, content_type, content_options, output_file):
    """
    This function performs the actual fetch data operation by performing SQL queries.


    Parameters
    ----------
    bucket: string
          The bucket name
    prefix: string
          The prefix of the file along with filename.
    expression: string
          The expression which is SQL type query.
    compression: string
          The compression of the file - GZIP or so on.
    content_type: string
          The content_type of the file - CSV or items
    content_options: object
          For example - {"FieldDelimiter": delimiter_req, 'AllowQuotedRecordDelimiter': True, 'QuoteCharacter' : ""}
    output_file: string
          The file name to which the output can be appended.


    """
    print("Performing, with: ", bucket, prefix, expression, compression, content_type,
          content_options)

    r = s3.select_object_content(
            Bucket=bucket,
            Key=prefix,
            ExpressionType='SQL',
            Expression=expression,
            InputSerialization={'CompressionType': compression, content_type: content_options},
            OutputSerialization={'CSV': {}},
    )

    if output_file != '':
        write_to_file(r, output_file)
    else:
        write_to_console(r)
