from flask import Flask, request, jsonify
import uuid
from database.database import save_product , save_request ,get_products,get_request_status
from cloud_tasks import create_cloud_task
import pandas as pd
app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload_csv():
    print(request.files)
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
    create_cloud_task(request_id)
    return jsonify({"request_id": request_id, "status": "PENDING"}), 202


@app.route("/status/<request_id>", methods=["GET"])
def check_status(request_id):
    status = get_request_status(request_id)
    products = get_products(request_id)
    
    return jsonify({"request_id": request_id, "status": status, "products": products})


@app.route("/process", methods=["POST"])
def process_images():
    if request.content_type != "application/json":
        return jsonify({"error": "Invalid Content-Type. Expected application/json"}), 400

    from image_processor import process_product_images
    data = request.get_json()
    request_id = data.get("request_id")

    if not request_id:
        return jsonify({"error": "Missing request_id"}), 400

    process_product_images(request_id)

    return jsonify({"request_id": request_id, "status": "COMPLETED"}), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8080)


 
