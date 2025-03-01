import traceback
from flask import Flask, request, jsonify
import uuid
from database.database import save_product , save_request ,get_products,get_request_status,get_completed_request_products
from cloud_tasks import create_cloud_task
from download_csv_operations import upload_csv_to_cloud_storage
import pandas as pd
import os
app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    request_id = str(uuid.uuid4())
    df = pd.read_csv(file)
    if not {'Serial Number', 'Product Name', 'Input Image Urls'}.issubset(df.columns):
        return jsonify({"error": "Invalid CSV format"}), 400
    
    save_request(request_id)
    
    for _, row in df.iterrows():
        product_name = row["Product Name"]
        input_images = row["Input Image Urls"].split(",")
        save_product(request_id=request_id, product_name=product_name, input_images=input_images)
    task_response = create_cloud_task(request_id)
    if task_response is None:
        print("[ERROR] Cloud Task creation failed.")
    else:
        print(f"[DEBUG] Cloud Task created successfully with name: {task_response}")
    return jsonify({"request_id": request_id, "status": "PENDING"}), 202


@app.route("/status/<request_id>", methods=["GET"])
def check_status(request_id):
    status = get_request_status(request_id)
    products = get_products(request_id)
    products_serialized = [product.to_dict() for product in products] if products else []
    
    return jsonify({
        "request_id": request_id,
        "status": status,
        "products": products_serialized
    }), 200

@app.route("/process", methods=["POST"])
def process_images():
    if request.content_type != "application/json":
        return jsonify({"error": "Invalid Content-Type. Expected application/json"}), 400

    from image_processor import process_product_images
    data = request.get_json()
    request_id = data.get("request_id")

    if not request_id:
        return jsonify({"error": "Missing request_id"}), 400

    status,message = process_product_images(request_id)

    return jsonify(
    {
        "request_id": request_id,
        "status": "COMPLETED" if status else "PENDING",
        "message":message
    }
), 200


@app.route("/download_csv", methods=["GET"])
def download_csv():
    try:
        products = get_completed_request_products()
        if not products:
            return jsonify({"error": "No processed images available"}), 404

        # Convert product objects to serializable dictionaries and create a DataFrame
        try:
            data = [product.to_dict() for product in products]
            df = pd.DataFrame(data)
        except Exception as e:
            print(f"Error converting products to DataFrame: {e}\n{traceback.format_exc()}")
            raise

        env = os.environ.get("ENV", "deployment").lower()
        csv_path = "processed_images.csv"  
        if env == "local":
            try:
                df.to_csv(csv_path, index=False)
            except Exception as e:
                print(f"Error saving CSV locally: {e}\n{traceback.format_exc()}")
                raise
        else:
            try:
                csv_data = df.to_csv(index=False)
                csv_path = upload_csv_to_cloud_storage(csv_data=csv_data)
            except Exception as e:
                print(f"Error uploading CSV to cloud storage: {e}\n{traceback.format_exc()}")
                raise

        return jsonify({"download_url": csv_path}), 200

    except Exception as e:
        print(f"Error generating CSV: {e}\n{traceback.format_exc()}")
        return jsonify({"error": "Failed to generate CSV"}), 500
    

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)


 
