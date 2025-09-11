from dotenv import load_dotenv
import os
import json

load_dotenv()

def get_users():
    """
    Retorna um dicionário com os usuários e suas senhas.
    """
    users_str = os.getenv("USERS")
    return json.loads(users_str)

def get_db_config():
    return {
        "host": os.getenv("DB_HOST"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
    }