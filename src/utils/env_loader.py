from dotenv import load_dotenv
import os

load_dotenv()

def get_users():
    """
    Retorna um dicionário com os usuários e suas senhas.
    """
    return {k: v for k, v in os.environ.items() if k not in ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASS"]}

def get_db_config():
    return {
        "host": os.getenv("DB_HOST"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASS"),
    }