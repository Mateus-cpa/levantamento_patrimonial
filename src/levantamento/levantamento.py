from fastapi import APIRouter, Form
import psycopg2
from src.utils.env_loader import get_db_config

router = APIRouter()

@router.post("/add_levantamento")
def add_levantamento(numero_tombamento: str = Form(...), data_levantamento: str = Form(...), localidade_levantamento: str = Form(...), responsavel_levantamento: str = Form(...)):
    db = get_db_config()
    conn = psycopg2.connect(**db)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO levantamento (numero_tombamento, data_levantamento, localidade_levantamento, responsavel_levantamento) VALUES (%s, %s, %s, %s)",
        (numero_tombamento, data_levantamento, localidade_levantamento, responsavel_levantamento)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"success": True}