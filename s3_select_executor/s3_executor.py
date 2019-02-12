#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

import boto3

from select_runner import *

def fetch_objects(bucket, prefix, throwerror):
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
    Returns
    -------
    list
        Generates a list of keys which are found inside the prefix
    """
    print 'Fetching s3 files from bucket ' + bucket + ' and prefix ' + prefix

    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}

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
            if key.startswith(prefix):
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
    parser.add_argument('-b', metavar='--bucket',
                        help='''Provide the bucket name, for example:  bucket-name ''')
    parser.add_argument('-p', metavar='--prefix',
                        help='''Provide the prefix - till the folder, for example: path/to/file/mysample-file.tsv.gz''')
    parser.add_argument('-comp', metavar='--compression',
                        help='''Is the compression available-true/false ''', default=True)
    parser.add_argument('-c', metavar='--ctype',
                        help='Content Type of the file - CSV/JSON',
                        default='CSV')
    parser.add_argument('-d', metavar='--delimiter',
                        help='Provide the Delimiter - COMMA/TAB',
                        default='COMMA')
    parser.add_argument('-s', metavar='--sql',
                        help='''Provide the SQL to be executed, for example:
                              select _1, _2, _20 from s3object s where _88 != 'VIEW_DETECTED' limit 10''', default='')
    parser.add_argument('-o', metavar='--outputfile',
                        help='Provide the filename to dump the records fetched', default='')
    parser.add_argument('-e', metavar='--throwerror',
                        help='Boolean value true/false - which determines whether to throw error while processing', default='false')

    return parser


if __name__ == '__main__':
    parser = fetch_args()

    args = parser.parse_args()
    sql = args.s
    bucket = args.b
    comp = ('GZIP' if args.comp else '')
    content_type = args.c
    delimiter = args.d
    output_file = args.o
    prefix = args.p
    delimiter_req = (',' if delimiter == 'COMMA' else '\t')
    throwerror = args.e

    if bucket is None or prefix is None or sql is None:
        print 'Please use: python s3_executor.py --help and pass valid arguments'
        exit(1)

    object_items = fetch_objects(bucket, prefix, throwerror)
    for item in object_items:
        perform(
                bucket,
                item,
                sql,
                comp,
                content_type,
                {'FieldDelimiter': delimiter_req, 'AllowQuotedRecordDelimiter': True, 'QuoteCharacter': ''},
                output_file)

