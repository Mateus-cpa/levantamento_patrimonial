from fastapi import FastAPI
from src.auth.credenciamento import router as auth_router
from src.menu.menu_principal import router as menu_router
from src.status_levantamento.excel_import import router as status_router
from src.levantamento.levantamento import router as levantamento_router

app = FastAPI(
    title="Levantamento Patrimonial API",
    description="API para gerenciamento de credenciamento, status de levantamento e inventário.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "API Levantamento Patrimonial ativa"}

app.include_router(auth_router)
app.include_router(menu_router)
app.include_router(status_router)
app.include_router(levantamento_router)