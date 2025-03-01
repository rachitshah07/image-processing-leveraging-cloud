import requests
from PIL import Image, UnidentifiedImageError
import io
from google.cloud import storage
from google.auth import default
from database.database import get_pending_products, update_product_images, mark_request_completed, get_products
from dotenv import load_dotenv
import os
import urllib.parse
credentials , _ = default()

if os.environ.get("ENV") == "local":
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".env"))
    load_dotenv(BASE_DIR)
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")

try:
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
except Exception as e:
    print(f"Error initializing Google Cloud Storage: {e}")

def generate_output_filename(image_url):
    """Generates a filename by keeping a reference to the input URL."""
    parsed_url = urllib.parse.urlparse(image_url)
    netloc = parsed_url.netloc.replace("www.", "")
    path = parsed_url.path.lstrip("/").replace("/", "_")
    query = parsed_url.query.replace("=", "_").replace("&", "_") 
    filename_parts = [netloc, path, query] if query else [netloc, path]
    filename = "_".join(filter(None, filename_parts))
    
    return f"image_{filename}"

def compress_and_upload(image_url, output_filename):
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status() 
    except requests.RequestException as e:
        print(f"Failed to download image from {image_url}: {e}")
        return None

    try:
        img = Image.open(io.BytesIO(response.content))
        img_io = io.BytesIO()
        img.save(img_io, format="JPEG", quality=50)
        img_io.seek(0)
    except UnidentifiedImageError:
        print(f"Unable to process image from {image_url} (Invalid format)")
        return None
    except Exception as e:
        print(f"Unexpected error processing image from {image_url}: {e}")
        return None

    try:
        if not output_filename.lower().endswith(".jpg"):
                output_filename += ".jpg"
        blob = bucket.blob(output_filename)
        blob.upload_from_file(img_io, content_type="image/jpeg")
        blob.content_type = "image/jpeg" 
        blob.patch()  
        blob.make_public()

        return f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/{output_filename}"
    except Exception as e:
        print(f"Failed to upload image {output_filename} to GCS: {e}")
        return None

def process_product_images(request_id):
    message = "Failure"
    try:
        products = get_pending_products(request_id)
        if not products:
            print(f"No products found for request ID: {request_id}")
            return True,"Success:No products found for request ID. Skipping "
    except Exception as e:
        print(f"Error fetching products for request ID {request_id}: {e}")
        return False,message

    for product in products:
        try:
            input_urls = product.get("input_images", [])
            output_urls = []
            product_id = product["id"]
            for i, url in enumerate(input_urls):
                output_filename =generate_output_filename(url)
                processed_url = compress_and_upload(image_url=url, output_filename=output_filename)
                if processed_url:
                    output_urls.append(processed_url)

            if output_urls:
                update_product_images(product_id=product_id, output_images=output_urls)
            else:
                print(f"No valid images processed for product ID {product['product_name']}")
        except Exception as e:
            print(f"Error processing images for product {product['product_name']}: {e}")
            return False , message

    try:
        mark_request_completed(request_id)
        print(f"Processing completed for request ID: {request_id}")
        return True, "Sucess"
    except Exception as e:
        print(f"Error marking request {request_id} as completed: {e}")
        return False, message
