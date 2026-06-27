from sqlalchemy.orm import Session
from app.models.user_db import DBUser
from app.core.security import verify_password

def get_user(db: Session, username: str):
    # Consulta real a la base de datos
    return db.query(DBUser).filter(DBUser.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user