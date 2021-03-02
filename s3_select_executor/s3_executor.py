#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

import boto3

from select_runner import *

def fetch_objects(bucket, prefix, throwerror, **kwargs):
    """
    This solution was available via: https://alexwlchan.net/2018/01/listing-s3-keys-redux/
    This function is the crucial function, which loops through all the available files in a folder and fetches the key of that object.


    Parameters
    ----------
    bucket: string
            takes the bucket name
    prefix: string
            takes the prefix - either till the folder or till the entire file name.
    throwerror: boolean
            this boolean value depicts whether to throw exception in case there
            is any missing data (useful for validation)
    kwargs: dict
            this has the kwargs which can more optional parameters
    Returns
    -------
    list
        Generates a list of keys which are found inside the prefix
    """
    print('Fetching s3 files from bucket ' + bucket + ' and prefix ' + prefix)

    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}
    exclude = kwargs.get('exclude', None)

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.

    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    while True:
        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)
        try:
            contents = resp['Contents']
        except KeyError:
            if throwerror == 'true':
                raise Exception('Could not find data for prefix: ' + prefix)
            return

        for obj in contents:
            key = obj['Key']

            if key.startswith(prefix) and (not exclude or key.find(exclude) == -1):
                yield key

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break


def fetch_args():
    """
       Is an arguments parser which showcases all possible arguments this python function takes in.
    """
    parser = \
        argparse.ArgumentParser(description='''Provide S3 details: example python s3_executor.py  -b "bucket-name" -p "path/to/file/mysample-file.tsv.gz" -d TAB -s "select * from s3object s where _88 != 'VIEW_DETECTED' limit 10" ''')
    parser.add_argument('-b', metavar='--bucket', required=True,
                        help='''Provide the bucket name, for example:  bucket-name ''')
    parser.add_argument('-p', metavar='--prefix', required=True,
                        help='''Provide the prefix - till the folder, for example: path/to/file/mysample-file.tsv.gz''')
    parser.add_argument('-comp', metavar='--compression', required=True, help='''Is the compression
            available - GZIP/None/BZIP2''', default="GZIP")
    parser.add_argument('-c', metavar='--ctype', help='Content Type of the file - CSV/JSON/Parquet',
            default='CSV')
    parser.add_argument('-d', metavar='--delimiter', help='Provide the Delimiter - COMMA/TAB', default='COMMA')
    parser.add_argument('-s', metavar='--sql',  required=True, help='''Provide the SQL to be executed, for example:
            select _1, _2, _20 from s3object s where _88 != 'VIEW_DETECTED' limit 10''', default='')
    parser.add_argument('-o', metavar='--outputfile', help='Provide the filename to dump the records fetched', default='')
    parser.add_argument('-exc', metavar='--exclude', help='Provide the file regex to exclude', default=None)
    parser.add_argument('-e', metavar='--throwerror', help='Boolean value true/false - which determines whether to throw error while processing', default='false')

    return parser


def get_compression(comp):
    """
    Get's the value the compression, in case there is no compression provided then it would be empty string.
    """
    value = ""
    if comp:
        value = comp

    return value

def get_content_type(content_type):
    """
    Get's the content_type for respective option.
    In case it's a TSV or CSV the return value is always csv
    """
    value = "CSV"
    if content_type == "Parquet":
        value = content_type
    elif content_type == "JSON":
        value = content_type

    return value

def get_delimiter(delimiter):
    """
    Get's the delimiter, in case nothing is given, then it would None
    """
    value = None
    if delimiter == "COMMA":
        value = ","
    elif delimiter == "TAB":
        value = "\t"

    return value

def get_output_content(content_type):
    """
    Get the outcontent type based on the expected content
    """
    value = 'CSV'
    if content_type == 'JSON':
        value = 'JSON'

    return value

def get_content_options(kwargs):
    """
    Get's the content options for given data.
    For Parquet this is not needed.
    """
    content_options = {}

    if kwargs['content_type'] != 'Parquet' and kwargs['content_type'] != 'JSON':
        content_options = {'AllowQuotedRecordDelimiter': True, 'QuoteCharacter' : ""}
        if delimiter:
            content_options['FieldDelimiter'] = kwargs['delimiter']
    if kwargs['content_type'] == 'JSON':
        content_options = {'Type': "DOCUMENT"}
        if delimiter:
            content_options['FieldDelimiter'] = kwargs['delimiter']

    return content_options


if __name__ == '__main__':
    parser = fetch_args()
    args = parser.parse_args()

    sql = args.s
    bucket = args.b
    prefix = args.p
    throwerror = args.e
    exclude = args.exc

    if bucket is None or prefix is None or sql is None:
        print('Please use: python s3_executor.py --help and pass valid arguments')
        exit(1)

    object_items = fetch_objects(bucket, prefix, throwerror, exclude=exclude)

    comp = get_compression(args.comp)
    content_type = get_content_type(args.c)
    delimiter = get_delimiter(args.d)
    output_file = args.o
    content_options = get_content_options({ 'content_type': content_type, 'delimiter': delimiter })
    output_content = get_output_content(content_type)

    for item in object_items:
        perform(bucket, item, sql, comp, content_type, content_options, output_file, output_content)


