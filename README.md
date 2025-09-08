# Projeto de levantamento patrimonial

## 1. Integração com PostgreSQL

## 2. Construção de credenciamento

## 3. Importar base de dados

## 4. Construir tela de levantamento# levantamento_patrimonial

# Configurar e executar código
```bash
python -m venv .venv
pyenv local 3.13.0
source .venv/Scripts/activate
poetry init
poetry shell

```

```bash
poetry install
poetry run streamlit run src/app_streamlit.py

```

```bash
poetry run uvicorn src.main:app --reload
 ```