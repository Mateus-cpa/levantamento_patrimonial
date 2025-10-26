from fastapi import FastAPI, Query
from src.auth.credenciamento import router as auth_router
from src.levantamento.levantamento import router as levantamento_router

app = FastAPI(
    title="Levantamento Patrimonial API",
    description="API para gerenciamento de credenciamento, status de levantamento e inventário.",
    version="1.0.0"
)

# Exemplo de dados: mapeamento de usuários para UGs
USER_UGS = {
    "celso.cfs": ["SRMG","SRDF","SRSP","SRSC","SRPE","CGAD"],
    "fuch.mpf": ["SRPR"],
    "getulio.gbs": ["SRPR", "SRAL"],
    "mateus.mcpa": ["SRPR", "SRPB", "DITEC"],
    "miguel.mpf": ["SRPB", "SRPE"],
    "mona.mdnm": ["SRPR", "SRSC"],
    "pericles.pd": ["SRPB", "SRAC"],
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
    perfil = "admin" if username == "admin" else "usuario"
    return {"ugs": ugs, "perfil": perfil}

app.include_router(auth_router)
app.include_router(levantamento_router)