# 📦 Levantamento Patrimonial
Este projeto implementa uma solução de inventário e levantamento patrimonial utilizando uma arquitetura moderna e desacoplada: um frontend interativo em Streamlit e um backend robusto em FastAPI, com persistência de dados no PostgreSQL.

# 🏗️ Arquitetura do Projeto
O projeto segue a arquitetura Cliente-Servidor, onde o frontend (Streamlit) consome a API RESTful (FastAPI) para acessar dados e realizar a autenticação.

| Componente | Tecnologia | Função Principal | 
| --- | --- | --- | 
| Frontend | Streamlit | Interface de usuário (UI), formulários de login e levantamento, visualização de status e relatórios. |
| Backend (API) | FastAPI | Lógica de negócios, autenticação segura (futuramente com JWT), gerenciamento de usuários e UGs, e interface com o Banco de Dados.|
| Banco de Dados | PostgreSQL | Persistência de dados de usuários, senhas (hashed), perfis, UGs de acesso e possivelmente os dados do inventário principal. | 

# ✨ Funcionalidades
- Credenciamento Seguro: Login via usuário e senha, utilizando variáveis de ambiente para a lista de usuários (em transição para PostgreSQL).
- Seleção de UG: Após o login, o usuário seleciona a Unidade Gestora (UG) permitida para o levantamento.
- Módulos de Navegação:
    - Levantamento: Página principal para a entrada de dados do inventário.
    - Status do Levantamento: Acompanhamento do progresso.
    - Relatório do Levantamento: Geração de relatórios.
    - Atualizar Base (Admin): Funcionalidade para administradores carregarem novos dados-base.
    - Gerenciar Usuários (Admin - Futuro): Tela para administradores criarem e gerenciarem perfis, senhas e permissões de UGs.

# 📁 Estrutura de Pastas
```
/levantamento_patrimonial
├── .env                  # Variáveis de ambiente e segredos
├── main.py               # Servidor FastAPI
├── menu_principal.py     # Frontend Streamlit (Página principal/Login)
├── src/
│   ├── auth/
│   │   ├── credenciamento.py # Lógica autenticação (futuro JWT)
│   ├── db/
│   │   ├── database.py       # Configuração do Motor SQLAlchemy e Sessões
│   │   └── model.py          # Modelos ORM (User, UG, InventoryItem)
│   ├── levantamento/
│   │   └── gerar_etiqueta.py
│   ├── pages/
│   │   ├── atualizar_base.py
│   │   ├── levantamento.py
│   │   └── ... (outras páginas)
│   └── utils/
├── .gitignore
├── .python-version
├── packages.txt
├── Procfile              # Conecta Streamlit e FastAPI
├── requirements.txt      # Dependências para Streamlit
├── poetry.lock
└── pyproject.toml
```

# ⚙️ Configuração e Instalação
Pré-requisitos:
1. Python 3.8+
2. PostgreSQL (local ou remoto)


## Configuração do Ambiente Virtual
É recomendado usar um ambiente virtual para isolar as dependências:
```
deactivate # Desativa venv atual
rm -r .venv
pyenv local 3.10.11
poetry init
poetry env use 3.10.11
poetry install
poetry run honcho start # Se o projeto estiver pronto
```


## 2. Configuração do Arquivo .env

Crie um arquivo chamado .env na raiz do projeto e configure as variáveis de ambiente.

**ATENÇÃO**: Para o desenvolvimento local, a variável USERS é utilizada para o formulário de login no Streamlit. No entanto, o objetivo final é migrar para o `DATABASE_URL`.

```
# .env

# --- Configuração da API ---
API_URL=http://localhost:8000  # URL para a API FastAPI

# --- Credenciais do PostgreSQL (Obrigatório para o Backend) ---
# Formato: postgresql://<user>:<password>@<host>:<port>/<dbname>
DATABASE_URL=postgresql://user_db:senha_segura@localhost:5432/patrimonio_db

# --- Usuários Locais (Apenas para o Frontend Streamlit, durante a transição) ---
# Estrutura: 
USERS='{
    "admin": {"password": "adminxxx", "perfil": "admin", "acesso": ["GERAL"]},
    "usuario.xxx": {"password": "xxx", "perfil": "usuario", "acesso": ["Ug1", "Ug2"]}
}'
```

# 🚀 Como Executar
Iniciar o Servidor FastAPI (Backend) e Streamlit (Frontend)
Inicie o servidor a partir do diretório raiz. 

O main.py irá automaticamente criar as tabelas no PostgreSQL ao iniciar.
```
poetry run honcho start
```

O servidor estará acessível em http://localhost:8000.


O Streamlit abrirá no seu navegador, geralmente em http://localhost:8501.

# 🔒 Próximos Passos (Segurança e Robustez)
O projeto está em processo de migração. As melhorias futuras mais importantes são:
1. Autenticação JWT (JSON Web Tokens): Implementar a geração de tokens no endpoint POST /login do FastAPI e exigir que todos os outros endpoints (incluindo /user_ugs) usem o token no cabeçalho Authorization.
2. Migração Completa dos Dados: Mover a lista de UGs e a lógica de permissões do USER_UGS hardcoded para as tabelas User e UGs no PostgreSQL.
3. Tela de Gestão de Perfis: Implementar a página pages/gerenciar_usuarios.py para que o administrador possa gerenciar usuários diretamente no frontend, persistindo os dados no PostgreSQL.