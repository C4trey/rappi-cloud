from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.models.order_db import DBOrder
from app.api.auth import get_current_user
from app.models.user_db import DBUser
from app.core.database import get_db

router = APIRouter()

# 1. Repartidor ve los pedidos que ya fueron empacados por Madam Tusan
@router.get("/api/driver/orders")
async def get_available_orders(db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    if current_user.role != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acceso denegado. Esta sección es exclusiva para repartidores."
        )
    # Buscamos pedidos que AWS haya marcado como empacados y que no tengan repartidor
    available_orders = db.query(DBOrder).filter(
        DBOrder.status == "PACK_COMPLETED", 
        DBOrder.driver_username == None
    ).all()
    
    return available_orders

# 2. Repartidor acepta llevar un pedido
@router.post("/api/driver/orders/{order_id}/accept")
async def accept_order(order_id: str, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    if current_user.role != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acceso denegado. Esta sección es exclusiva para repartidores."
        )
    
    db_order = db.query(DBOrder).filter(DBOrder.id == order_id).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if db_order.driver_username:
        raise HTTPException(status_code=400, detail="Este pedido ya tiene un repartidor asignado")
        
    db_order.driver_username = current_user.username
    db_order.status = "ON_THE_WAY" # El repartidor va en camino
    db.commit()
    
    return {"message": f"Has aceptado el pedido {order_id}. ¡Ve a entregarlo!"}

# 3. Repartidor marca el pedido como entregado en la puerta del cliente
@router.post("/api/driver/orders/{order_id}/delivered")
async def order_delivered(order_id: str, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    if current_user.role != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acceso denegado. Esta sección es exclusiva para repartidores."
        )
    db_order = db.query(DBOrder).filter(
        DBOrder.id == order_id, 
        DBOrder.driver_username == current_user.username
    ).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado o no te pertenece")
        
    db_order.status = "WAITING_RECEIVE" # Esto habilita al cliente para confirmar en su app
    db.commit()
    
    return {"message": "Has entregado el pedido. Esperando confirmación del cliente."}