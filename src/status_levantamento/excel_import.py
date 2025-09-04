from fastapi import APIRouter, UploadFile
import pandas as pd
import psycopg2
from src.utils.env_loader import get_db_config

router = APIRouter()

@router.post("/import_excel")
async def import_excel(file: UploadFile):
    df = pd.read_excel(await file.read())
    db = get_db_config()
    conn = psycopg2.connect(**db)
    cur = conn.cursor()
    for _, row in df.iterrows():
        cur.execute(
            "UPDATE base_dados SET coluna1=%s, coluna2=%s WHERE id=%s",
            (row['coluna1'], row['coluna2'], row['id'])
        )
    conn.commit()
    cur.close()
    conn.close()
    return {"success": True}