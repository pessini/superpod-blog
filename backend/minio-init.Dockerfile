FROM minio/mc:latest

# The mc mb (make bucket) command creates the bucket only if it does not exist. 
# If the bucket already exists, it will return an error, 
#   but the || true part ensures the script continues without failing.
ENTRYPOINT [ "sh", "-c", "\
  sleep 5 && \
  /usr/bin/mc alias set myminio \"$MINIO_ENDPOINT\" \"$MINIO_ROOT_USER\" \"$MINIO_ROOT_PASSWORD\" && \
  /usr/bin/mc mb --region=\"$MINIO_REGION\" myminio/\"$MINIO_BUCKETS\" || true \
"]