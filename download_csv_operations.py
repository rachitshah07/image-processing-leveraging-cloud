from datetime import datetime
from io import BytesIO
import pandas as pd
import traceback
import os
import uuid
from google.cloud import storage
def upload_csv_to_cloud_storage(csv_data: str) -> str:
    try:
        bucket_name = os.environ.get("GCS_BUCKET_NAME")
        if not bucket_name:
            raise Exception("GCS_BUCKET_NAME environment variable is not set")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        destination_blob_name = f"processed_images_{timestamp}.csv"

        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(destination_blob_name)
        csv_bytes = csv_data.encode("utf-8")
        blob.upload_from_string(csv_bytes, content_type="text/csv")
        blob.make_public()
        return blob.public_url
    except Exception as e:
        print(f"Error in upload_csv_to_cloud_storage: {e}\n{traceback.format_exc()}")
        raise
