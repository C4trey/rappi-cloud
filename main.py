from fastapi import FastAPI
from app.api import auth, orders, driver
from app.core.database import engine, Base
from app.models import user_db
from app.models.user_db import DBUser
from app.models.order_db import DBOrder 

# Crea las tablas en SQLite
Base.metadata.create_all(bind=engine)

# Inicializa FastAPI
app = FastAPI(title="Rappi Simulator API")

# Incluimos los routers
app.include_router(auth.router)
app.include_router(orders.router)
app.include_router(driver.router)