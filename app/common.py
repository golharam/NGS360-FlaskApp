def access(bucket, key):
    '''
    This function mimick os.access to check for a file
    key is full s3 path to file eg s3://mybucket/myfile.txt
    '''
    try:
        paginator = boto3.clients['s3'].get_paginator('list_objects')
        iterator = paginator.paginate(Bucket=bucket,
                                    Prefix=key, Delimiter='/')
        for responseData in iterator:
            #common_prefixes = responseData.get('CommonPrefixes', [])
            contents = responseData.get('Contents', [])
            #if not contents: # and not common_prefixes:
                #self._empty_result = True
            #    return
            #for common_prefix in common_prefixes:
                # is Dir, should never occur
            for content in contents:
                return key == content['Key']
    except botocore.exceptions.ClientError:
        pass
    return False

def find_bucket_key(s3path):
    """
    This is a helper function that given an s3 path such that the path is of
    the form: bucket/key
    It will return the bucket and the key represented by the s3 path, eg
    if s3path == s3://bmsrd-ngs-data/P-234
    """
    if s3path.startswith('s3://'):
        s3path = s3path[5:]
    s3components = s3path.split('/')
    bucket = s3components[0]
    s3key = ""
    if len(s3components) > 1:
        s3key = '/'.join(s3components[1:])
    return bucket, s3key

