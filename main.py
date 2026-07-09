from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <-- Nueva importación
from app.api import auth, orders, driver
from app.core.database import engine, Base
from app.models import user_db
from app.models.user_db import DBUser
from app.models.order_db import DBOrder 

# Crea las tablas en SQLite
Base.metadata.create_all(bind=engine)

# Inicializa FastAPI
app = FastAPI(title="Rappi Simulator API")

# <-- INICIO DE LA SOLUCIÓN DEL CORS -->
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que el React de tu amigo se conecte
    allow_credentials=True,
    allow_methods=["*"],  # Permite POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)
# <-- FIN DE LA SOLUCIÓN DEL CORS -->

# Incluimos los routers
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(driver.router)
