from sqlalchemy import Column, String, Float
from app.core.database import Base

class DBOrder(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, index=True)
    driver_username = Column(String, nullable=True) # <- NUEVA COLUMNA
    total_price = Column(Float)
    delivery_address = Column(String)
    status = Column(String, default="RECEIVED")