from fastapi import APIRouter, Form
from src.utils.env_loader import get_users

router = APIRouter()

@router.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    users = get_users()
    if username in users and users[username] == password:
        return {"success": True}
    return {"success": False, "error": "Credenciais inválidas"}