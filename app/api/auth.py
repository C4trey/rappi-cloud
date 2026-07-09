from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db, engine, Base
from app.services.auth_service import authenticate_user
from app.models.user_db import DBUser
from app.models.user import Token # Tu modelo Pydantic
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm # Agregamos OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.security import create_access_token, get_password_hash, SECRET_KEY, ALGORITHM

Base.metadata.create_all(bind=engine)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# Esta es la función que te faltaba
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Intentamos descifrar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    # Buscamos al usuario en la base de datos SQLite
    user = db.query(DBUser).filter(DBUser.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/api/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db) # Inyectamos la BD
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}



# Aquí agregamos el registro real
from pydantic import BaseModel
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "customer"

@router.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Verificamos si el username ya existe
    db_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
        
    # 2. Verificamos si el email ya está registrado
    db_email = db.query(DBUser).filter(DBUser.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Este correo ya está en uso")
    
    # 3. Validamos el rol
    if user.role not in ["customer", "driver"]:
        raise HTTPException(status_code=400, detail="Rol inválido. Debe ser 'customer' o 'driver'")
    
    # 4. Creamos el usuario incluyendo el email
    hashed_pwd = get_password_hash(user.password)
    new_user = DBUser(
        username=user.username, 
        email=user.email, 
        hashed_password=hashed_pwd, 
        role=user.role
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    if user.role == "driver":
        return {"message": f"Repartidor {user.username} registrado exitosamente"}
    
    return {"message": f"Usuario {user.username} registrado exitosamente"}



@router.post("/api/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: DBUser = Depends(get_current_user)):
    """
    Endpoint para cerrar sesión. 
    Como usamos JWT (Stateless), el servidor no destruye el token.
    La responsabilidad de eliminarlo recae en el cliente (Frontend/Postman).
    """
    return {
        "message": f"Logout exitoso para el usuario {current_user.username}.",
        "instruction": "Por favor, elimina el token guardado en tu aplicación cliente."
    }