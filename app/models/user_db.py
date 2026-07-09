from sqlalchemy import Column, Integer, String
from app.core.database import Base

class DBUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True) # <-- NUEVA COLUMNA
    hashed_password = Column(String)
    role = Column(String, default="customer")