from sqlalchemy.orm import Session
from . import models
from typing import Dict, Any, List
import json

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, email: str, password: str, authorized_ugs: List[str]):
    hashed_password = models.User.get_password_hash(password)
    db_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        authorized_ugs=authorized_ugs
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def save_levantamento_data(db: Session, ug: str, data_type: str, content: Dict[str, Any], user_id: int):
    db_data = models.LevantamentoData(
        ug=ug,
        data_type=data_type,
        content=content,
        user_id=user_id
    )
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def get_levantamento_data(db: Session, ug: str, data_type: str):
    return db.query(models.LevantamentoData).filter(
        models.LevantamentoData.ug == ug,
        models.LevantamentoData.data_type == data_type
    ).first()