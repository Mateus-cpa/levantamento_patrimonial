from fastapi import FastAPI, Query
from src.auth.credenciamento import router as auth_router
from src.levantamento.levantamento import router as levantamento_router
from pages.app_status_levantamento import router as status_router
#from src.menu.menu_principal import router as menu_router #problema importação por causa de __pycache__

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

@app.get("/user_ugs")
def get_user_ugs(username: str = Query(...)):
    """
    Retorna a lista de UGs permitidas para o usuário informado.
    """
    ugs = USER_UGS.get(username, [])
    return {"ugs": ugs}

app.include_router(auth_router)
#app.include_router(menu_router)
app.include_router(status_router)
app.include_router(levantamento_router)