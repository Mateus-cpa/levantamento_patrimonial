# Projeto de levantamento patrimonial

## 1. Integração com PostgreSQL

## 2. Construção de credenciamento

## 3. Importar base de dados

## 4. Construir tela de levantamento# levantamento_patrimonial

# Configurar e executar código

Ativa ambiente virtual
```bash
python -m venv .venv
pyenv local 3.10.11
source .venv/Scripts/activate
poetry init
poetry shell

```

Ativa FastAPI
```bash
poetry install
poetry run uvicorn src.main:app --reload

```

Executa Streamlit
```bash
poetry run streamlit run src/app_streamlit.py

 ```