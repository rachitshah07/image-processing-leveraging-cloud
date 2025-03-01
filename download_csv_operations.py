from io import BytesIO
import pandas as pd
import traceback
import os
from google.cloud import storage
def upload_csv_to_cloud_storage(csv_data: pd.DataFrame) -> str:
    bucket_name = os.environ.get("GCS_BUCKET_NAME")
    if not bucket_name:
        raise Exception("GCS_BUCKET_NAME environment variable is not set")
    destination_blob_name = "processed_images.csv"
    
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(csv_data, content_type="text/csv")
    url = blob.generate_signed_url(expiration=3600)
    return url
