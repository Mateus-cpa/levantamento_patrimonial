from fastapi import APIRouter

router = APIRouter()

@router.get("/menu")
def menu():
    return {
        "options": [
            "Status do Levantamento",
            "Inventário"
        ]
    }