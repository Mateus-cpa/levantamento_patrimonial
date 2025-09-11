# Projeto de levantamento patrimonial

## 1. Integração com PostgreSQL

## 2. Construção de credenciamento

## 3. Importar base de dados

## 4. Construir tela de levantamento# levantamento_patrimonial

# Configurar e executar código

Ativa ambiente virtual
```bash
rm -r .venv
pyenv local 3.10.11
poetry init
poetry env use 3.10.11
poetry install
poetry run honcho start

```

Ativa FastAPI
```bash
poetry run uvicorn src.main:app --reload

```

Executa Streamlit
```bash
poetry run streamlit run src/app_streamlit.py

 ```