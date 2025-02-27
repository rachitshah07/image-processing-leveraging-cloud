from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database.config import Base, engine

class ProcessingRequest(Base):
    __tablename__ = "processing_requests"

    id = Column(String, primary_key=True)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=datetime.utcnow)

    products = relationship("Product", back_populates="request")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String, ForeignKey("processing_requests.id"), nullable=False)
    product_name = Column(String, nullable=False)
    input_images = Column(JSON, nullable=False)
    output_images = Column(JSON, nullable=True)
    status = Column(String, default="PENDING")

    request = relationship("ProcessingRequest", back_populates="products")

Base.metadata.create_all(engine)
print("Tables created successfully (if not already present).")