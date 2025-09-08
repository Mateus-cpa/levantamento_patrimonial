from fastapi import FastAPI, Query
from typing import List
from src.auth.credenciamento import router as auth_router
from src.menu.menu_principal import router as menu_router
from src.status_levantamento.excel_import import router as status_router
from src.levantamento.levantamento import router as levantamento_router

app = FastAPI(
    title="Levantamento Patrimonial API",
    description="API para gerenciamento de credenciamento, status de levantamento e inventário.",
    version="1.0.0"
)

# Exemplo de dados: mapeamento de usuários para UGs
USER_UGS = {
    "USER1": ["UG1", "UG2"],
    "USER2": ["UG2"],
    "admin": ["UG1", "UG2", "UG3"],
}

@app.get("/")
def read_root():
    return {"message": "API Levantamento Patrimonial ativa"}

@app.get("/user_ugs")
def get_user_ugs(username: str = Query(...)):
    """
    Retorna a lista de UGs permitidas para o usuário informado.
    """
    ugs = USER_UGS.get(username, [])
    return {"ugs": ugs}

app.include_router(auth_router)
app.include_router(menu_router)
app.include_router(status_router)
app.include_router(levantamento_router)