import os
import uuid
import requests
from fastapi import APIRouter, Depends, status, BackgroundTasks, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.models.order import OrderCreate
from app.models.order_db import DBOrder
from app.api.auth import get_current_user
from app.models.user_db import DBUser
from app.core.database import get_db

router = APIRouter()

# --- MODELOS ---
class StatusUpdate(BaseModel):
    tenant_id: str
    order_id: str
    status: str
    step: str
    worker_id: str | None = None
    timestamp: str

# --- TAREAS EN SEGUNDO PLANO ---
def send_order_to_aws(order_data: dict):
    aws_url = os.getenv("AWS_API_GATEWAY_URL", "URL_PENDIENTE")
    secret = os.getenv("RAPPI_SHARED_SECRET", "un-secreto-largo")
    headers = {"X-Rappi-Secret": secret}
    
    if aws_url == "URL_PENDIENTE":
        print(f"[SIMULACIÓN] Pedido listo para enviar. Falta URL de AWS.")
        return

    try:
        # Apuntamos al endpoint específico para crear órdenes de Rappi
        response = requests.post(f"{aws_url}/integrations/rappi/orders", json=order_data, headers=headers)
        response.raise_for_status()
        print(f"[ÉXITO] Pedido enviado a AWS: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Falló al enviar a AWS: {e}")

def send_receipt_confirmation_to_aws(order_id: str):
    aws_url = os.getenv("AWS_API_GATEWAY_URL", "URL_PENDIENTE")
    secret = os.getenv("RAPPI_SHARED_SECRET", "un-secreto-largo")
    headers = {"X-Rappi-Secret": secret}
    
    if aws_url != "URL_PENDIENTE":
        try:
            response = requests.post(f"{aws_url}/integrations/rappi/orders/{order_id}/receive", json={}, headers=headers)
            response.raise_for_status()
            print(f"[ÉXITO] Recepción confirmada en AWS para la orden {order_id}")
        except Exception as e:
            print(f"[ERROR] Falló al confirmar recepción en AWS: {e}")

# --- 1. ENDPOINT: CLIENTE CREA PEDIDO ---
@router.post("/api/orders", status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    order_id = str(uuid.uuid4())
    
    new_order = DBOrder(
        id=order_id,
        username=current_user.username,
        total_price=order.total_price,
        delivery_address=order.delivery_address,
        status="RECEIVED"
    )
    db.add(new_order)
    db.commit()

    order_payload = {
    "tenant_id": "madamtusan", # Dato quemado obligatorio según el README
    "customer_id": current_user.username, # Traducimos el nombre de usuario
    "items": [item.dict() for item in order.items] # Pasamos la lista de productos
}

# Enviamos ese paquete (payload) hacia el API Gateway de tus compañeros
    background_tasks.add_task(send_order_to_aws, order_payload)
    return {"message": "Pedido registrado", "order_id": order_id}

# --- 2. ENDPOINT: WEBHOOK DE AWS ---
# Exigimos el header x_rappi_secret para autorizar la petición
@router.post("/api/estado", status_code=status.HTTP_200_OK)
async def update_order_status_from_aws(
    update: StatusUpdate, 
    x_rappi_secret: str = Header(...), 
    db: Session = Depends(get_db)
):
    # Validamos que el secreto coincida
    if x_rappi_secret != os.getenv("RAPPI_SHARED_SECRET"):
        raise HTTPException(status_code=401, detail="Secreto inválido")

    db_order = db.query(DBOrder).filter(DBOrder.id == update.order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado en Rappi")
    
    db_order.status = update.status
    db.commit()
    
    return {"message": "Estado actualizado exitosamente"}

# --- 3. ENDPOINT: CLIENTE CONFIRMA RECEPCIÓN ---
@router.post("/api/orders/{order_id}/confirm")
async def confirm_receipt(
    order_id: str, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    db_order = db.query(DBOrder).filter(DBOrder.id == order_id, DBOrder.username == current_user.username).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    db_order.status = "COMPLETED"
    db.commit()
    
    background_tasks.add_task(send_receipt_confirmation_to_aws, order_id)
    return {"message": "Has confirmado la recepción de tu pedido."}

# --- 4. ENDPOINT: CONSULTAR ESTADO ---
@router.get("/api/orders/{order_id}")
async def get_order_status(order_id: str, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    db_order = db.query(DBOrder).filter(DBOrder.id == order_id, DBOrder.username == current_user.username).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    return {"order_id": db_order.id, "total": db_order.total_price, "status": db_order.status}