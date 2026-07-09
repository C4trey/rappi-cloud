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
    aws_url = os.getenv("AWS_API_GATEWAY_URL", "")
    secret = os.getenv("RAPPI_SHARED_SECRET", "un-secreto-largo")
    headers = {"X-Rappi-Secret": secret}
    try:
        response = requests.post(f"{aws_url}/integrations/rappi/orders", json=order_data, headers=headers)
        response.raise_for_status()
        print(f"[ÉXITO] Pedido enviado a AWS: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Falló al enviar a AWS: {e}")


# --- RUTAS ---
@router.post("/api/orders", status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate, 
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    # 1. Empaquetamos los datos para AWS
    order_payload = {
        "tenant_id": "madamtusan",
        "customer_id": current_user.username,
        "items": [item.dict() for item in order.items]
    }
    
    # 2. Enviamos el pedido a AWS y ESPERAMOS su respuesta
    aws_url = os.getenv("AWS_API_GATEWAY_URL", "")
    secret = os.getenv("RAPPI_SHARED_SECRET", "un-secreto-largo")
    headers = {"X-Rappi-Secret": secret}
    
    try:
        response = requests.post(f"{aws_url}/integrations/rappi/orders", json=order_payload, headers=headers)
        response.raise_for_status()
        
        # 3. ¡Capturamos el ID oficial de AWS!
        aws_data = response.json()
        aws_order_id = aws_data["order_id"]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando con AWS: {e}")

    # 4. Guardamos en nuestra BD local usando el ID maestro de AWS
    new_order = DBOrder(
        id=aws_order_id,
        username=current_user.username,
        total_price=order.total_price,
        delivery_address=order.delivery_address,
        status="RECEIVED"
    )
    db.add(new_order)
    db.commit()

    print(f"\n[ÉXITO] Pedido sincronizado. ID Maestro: {aws_order_id}\n")
    return {"message": "Pedido registrado", "order_id": aws_order_id}

@router.post("/api/estado", status_code=status.HTTP_200_OK)
async def update_order_status_from_aws(
    update: StatusUpdate, 
    x_rappi_secret: str = Header(None), 
    db: Session = Depends(get_db)
):
    # Validamos que el secreto coincida
    if x_rappi_secret != os.getenv("RAPPI_SHARED_SECRET", "un-secreto-largo"):
        raise HTTPException(status_code=401, detail="Secreto inválido")

    db_order = db.query(DBOrder).filter(DBOrder.id == update.order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado en Rappi")
    
    db_order.status = update.status
    db.commit()
    
    # Imprimimos en verde en la consola para saber que funcionó
    print(f"\n✅ [AWS NOTIFICA] El pedido {update.order_id} cambió a estado: {update.status}\n")
    return {"message": "Estado actualizado exitosamente"}

@router.post("/api/orders/{order_id}/confirm")
async def confirm_receipt(
    order_id: str, 
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    # 1. Buscamos el pedido
    db_order = db.query(DBOrder).filter(DBOrder.id == order_id, DBOrder.username == current_user.username).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    # 2. Intentamos sincronizar con AWS PRIMERO
    aws_url = os.getenv("AWS_API_GATEWAY_URL", "")
    secret = os.getenv("RAPPI_SHARED_SECRET", "un-secreto-largo")
    headers = {"X-Rappi-Secret": secret}
    
    try:
        response = requests.post(f"{aws_url}/integrations/rappi/orders/{order_id}/receive", json={}, headers=headers)
        response.raise_for_status() # Lanza error si AWS no responde 200 OK
    except Exception as e:
        # Extraemos el mensaje de error exacto que AWS nos mandó
        error_msg = response.json().get("message", str(e)) if 'response' in locals() and response else str(e)
        raise HTTPException(status_code=400, detail=f"AWS rechazó la confirmación: {error_msg}")

    # 3. Solo si AWS aceptó, actualizamos nuestra BD local
    db_order.status = "COMPLETED"
    db.commit()
    
    return {"message": "Has confirmado la recepción."}

@router.get("/api/orders/{order_id}")
async def get_order_status(order_id: str, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    db_order = db.query(DBOrder).filter(DBOrder.id == order_id, DBOrder.username == current_user.username).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
    return {"order_id": db_order.id, "total": db_order.total_price, "status": db_order.status}