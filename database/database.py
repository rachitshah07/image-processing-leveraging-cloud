import traceback
from typing import List
from database.models import ProcessingRequest, Product
from database.config import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_request(request_id):
    try:
        db = SessionLocal()
        new_request = ProcessingRequest(id=request_id, status="PENDING")
        db.add(new_request)
        db.commit()
        db.close()
    except Exception as e:
        print(f"Error saving request {request_id} in DB: {traceback.format_exc()}")
        

def save_product(request_id, product_name, input_images):
    try:
        db = SessionLocal()
        new_product = Product(
            request_id=request_id,
            product_name=product_name,
            input_images=input_images,
            status="PENDING"
        )
        db.add(new_product)
        db.commit()
        db.close()

    except Exception as e:
        print(f"Error saving CSV Data for {request_id} and product name {product_name} in DB: {traceback.format_exc()}")

def get_request_status(request_id):
    try:

        db = SessionLocal()
        request = db.query(ProcessingRequest).filter(ProcessingRequest.id == request_id).first()
        db.close()
    except Exception as e:
        print(f"Error getting request status for {request_id} from DB: {traceback.format_exc()}")
        return None
    return request.status if request else None

def get_products(request_id)->List[Product]:
    try: 
        db = SessionLocal()
        products = db.query(Product).filter(Product.request_id == request_id).all()
        db.close()
    except Exception as e:
        print(f"Error getting products for {request_id} from DB: {traceback.format_exc()}")
        return None
    return products

def get_pending_products(request_id)->List[Product]:
    try: 
        db = SessionLocal()

        products = db.query(Product).filter(
            Product.request_id == request_id,
            Product.status == "PENDING"
        ).all()
        db.close()
    except Exception as e:
        print(f"Error getting products for {request_id} from DB: {traceback.format_exc()}")
        return []
    return products


def update_product_images(product_id, output_images):
    try:
        db = SessionLocal()
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            product.output_images = output_images
            product.status = "COMPLETED"
            db.commit()
        db.close()
    except Exception as e:
        print(f"Error updating OUTPUT URLS and STATUS for {product_id} in DB: {traceback.format_exc(e)}")
        

def mark_request_completed(request_id):
    try:
        db = SessionLocal()
        request = db.query(ProcessingRequest).filter(ProcessingRequest.id == request_id).first()
        if request:
            request.status = "COMPLETED"
            db.commit()
        db.close()
    except Exception as e:
        print(f"Error marking STATUS for {request_id} in DB: {traceback.format_exc(e)}")
       

def get_completed_request_products() -> List[Product]:
    db = SessionLocal()
    try:
        products: List[Product] = db.query(Product).filter(Product.status == "COMPLETED").all()
        return products
    except Exception as e:
        print(f"Error fetching CSV for COMPLETED Processes from DB: {traceback.format_exc()}")
        return [] 
    finally:
        db.close()