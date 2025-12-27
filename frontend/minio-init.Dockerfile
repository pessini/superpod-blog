FROM minio/mc:latest

ENTRYPOINT [ "sh", "-c", "\
  sleep 5 && \
  /usr/bin/mc alias set myminio \"$MINIO_ENDPOINT\" \"$MINIO_ROOT_USER\" \"$MINIO_ROOT_PASSWORD\" && \
  /usr/bin/mc mb --region=\"$MINIO_REGION\" myminio/\"$MINIO_BUCKETS\" || true \
"]