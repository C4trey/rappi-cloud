from app.api import auth
from app.core.database import engine, Base
# Importamos los modelos para que SQLAlchemy sepa qué tablas crear
from app.models import user_db
from fastapi import FastAPI, Depends
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Rappi Simulator API")

# Incluimos el router de autenticación
app.include_router(auth.router)

# Importamos la dependencia que verifica el token
from app.api.auth import get_current_user
from app.models.user import User

# Ejemplo de ruta protegida (requiere token JWT)
@app.post("/api/orders", status_code=201)
async def create_order(current_user: User = Depends(get_current_user)):
    return {
        "message": "Pedido creado", 
        "user": current_user.username,
        "note": "Aquí irá la lógica para disparar el evento a AWS"
    }