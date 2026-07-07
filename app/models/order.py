from pydantic import BaseModel
from typing import List

# Representa un producto individual en la canasta
class OrderItem(BaseModel):
    product_id: str
    name: str
    quantity: int
    price: float

# Representa el pedido completo que envía el usuario
class OrderCreate(BaseModel):
    items: List[OrderItem]
    total_price: float
    delivery_address: str
