from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session
from src.database import crud, models
from src.database.deps import get_db
from src.auth.auth_utils import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI(
    title="Levantamento Patrimonial API",
    description="API para gerenciamento de credenciamento, status de levantamento e inventário.",
    version="1.0.0"
)

# Exemplo de dados: mapeamento de usuários para UGs
USER_UGS = {
    "miguel.mpf": ["SRPB", "SRPE"],
    "pericles.pd": ["SRPB", "SRAC"],
    "getulio.gbs": ["SRPR", "SRAL"],
    "celso.cfs": ["SRMG","SRDF","SRSP","SRSC","SRPE","CGAD"],
    "mateus.mcpa": ["SRPR", "SRPB", "DITEC"],
    "admin":  [
    'SRAC',
    'SRAL',
    'SRAP',
    'SRAM',
    'SRBA',
    'SRCE',
    'CGAD',
    'SRDF',
    'DITEC',
    'DIREN',
    'DTI',
    'SRES',
    'FIG',
    'SRGO',
    'SRMA',
    'SRMT',
    'SRMS',
    'SRMG',
    'SRPA',
    'SRPB',
    'SRPR',
    'SRPE',
    'SRPI',
    'SRRJ',
    'SRRN',
    'SRRS',
    'SRRO',
    'SRRR',
    'SRSC',
    'SRSP',
    'SRSE',
    'SRTO',
    'GERAL']
}

@app.get("/")
def read_root():
    return {"message": "API Levantamento Patrimonial ativa"}

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, form_data.username)
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/user_ugs")
def get_user_ugs(
    current_user: models.User = Depends(get_current_user)
):
    """
    Retorna a lista de UGs permitidas para o usuário autenticado.
    """
    return {"ugs": current_user.authorized_ugs, "perfil": "admin" if "GERAL" in current_user.authorized_ugs else "usuario"}

@app.post("/users/")
def create_user(
    username: str,
    email: str,
    password: str,
    authorized_ugs: list[str],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verifica se o usuário atual é admin
    if "GERAL" not in current_user.authorized_ugs:
        raise HTTPException(
            status_code=403,
            detail="Only admin users can create new users"
        )
    return crud.create_user(db, username, email, password, authorized_ugs)

@app.post("/levantamento/{ug}")
def save_levantamento(
    ug: str,
    data_type: str,
    content: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verifica se o usuário tem acesso à UG
    if ug not in current_user.authorized_ugs and "GERAL" not in current_user.authorized_ugs:
        raise HTTPException(
            status_code=403,
            detail="User not authorized for this UG"
        )
    return crud.save_levantamento_data(db, ug, data_type, content, current_user.id)

@app.get("/levantamento/{ug}")
def get_levantamento(
    ug: str,
    data_type: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verifica se o usuário tem acesso à UG
    if ug not in current_user.authorized_ugs and "GERAL" not in current_user.authorized_ugs:
        raise HTTPException(
            status_code=403,
            detail="User not authorized for this UG"
        )