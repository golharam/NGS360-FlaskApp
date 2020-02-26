browseFiles = function (bucket, prefix) {
    // bucket
    this.bucket = bucket;
    // prefix of directory in bucket
    this.prefix = prefix;
    console.log("Browsing s3://" + bucket + "/" + prefix);
};
