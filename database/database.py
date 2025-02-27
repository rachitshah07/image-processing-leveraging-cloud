from sqlalchemy.orm import Session
from database.models import ProcessingRequest, Product
from database.config import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def save_request(request_id):
    db = SessionLocal()
    new_request = ProcessingRequest(id=request_id, status="PENDING")
    db.add(new_request)
    db.commit()
    db.close()

def save_product(request_id, product_name, input_images):
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

def get_request_status(request_id):
    db = SessionLocal()
    request = db.query(ProcessingRequest).filter(ProcessingRequest.id == request_id).first()
    db.close()
    return request.status if request else None

def get_products(request_id):
    db = SessionLocal()
    products = db.query(Product).filter(Product.request_id == request_id).all()
    db.close()
    return [
        {"id":p.id,"product_name": p.product_name, "input_images": p.input_images, "output_images": p.output_images}
        for p in products
    ]


def update_product_images(product_id, output_images):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if product:
        product.output_images = output_images
        product.status = "COMPLETED"
        db.commit()
    db.close()

def mark_request_completed(request_id):
    db = SessionLocal()
    request = db.query(ProcessingRequest).filter(ProcessingRequest.id == request_id).first()
    if request:
        request.status = "COMPLETED"
        db.commit()
    db.close()