from src.database.config import engine
from src.database import models
from src.database.crud import create_user

def init_db():
    # Cria todas as tabelas
    models.Base.metadata.create_all(bind=engine)
    
    # Aqui você pode adicionar dados iniciais se necessário
    # Por exemplo, criar um usuário admin
    
if __name__ == "__main__":
    print("Criando tabelas do banco de dados...")
    init_db()
    print("Tabelas criadas com sucesso!")