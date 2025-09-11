import streamlit as st
import requests
import os
import json
from utils.env_loader import get_users

def get_users_from_env():
    """
    Função auxiliar para carregar a lista de usuários para o Selectbox.
    """
    users_str = os.getenv("USERS")
    if users_str:
        try:
            # Substitui as aspas simples por duplas para compatibilidade
            users_str = users_str.replace("'", '"')
            users_dict = json.loads(users_str)
            return list(users_dict.keys())
        except json.JSONDecodeError:
            st.error("Erro ao carregar a lista de usuários do arquivo .env. Verifique a sintaxe JSON.")
            return []
    return []

API_URL = "http://127.0.0.1:8000"

st.title("Levantamento Patrimonial")

st.header("Credenciamento")
# A lista de usuários é carregada uma vez no início
users = ['Selecione um usuário', 'miguel.mpf', 'pericles.pd', 'getulio.gbs', 'admin']
if not users:
    st.warning("Nenhum usuário encontrado na variável de ambiente USERS. Verifique seu arquivo .env.")
else:
    # Use st.session_state para manter o estado de login
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
        st.session_state.username = None

    if not st.session_state.is_authenticated:
        # Se o usuário não estiver autenticado, mostre o formulário de login
        with st.form(key="login_form"):
            st.session_state.username = st.selectbox("Usuário", options=users)
            password = st.text_input("Senha", type="password")
            submit_button = st.form_submit_button("Entrar")

        if submit_button:
            with st.spinner("Autenticando..."):
                st.session_state.is_authenticated = True
                """try:
                    # Envia a requisição POST para a API de login
                    response = requests.post(
                        f"{API_URL}/login",
                        data={"username": username, "password": password}
                    )
                    
                    # Lança um erro se o status for 4xx ou 5xx
                    response.raise_for_status()

                    result = response.json()
                    
                    if result.get("success"):
                        st.success("Credenciado com sucesso!")
                        st.session_state.is_authenticated = True
                        st.session_state.username = username
                        st.experimental_rerun()  # Força uma nova execução
                    else:
                        st.error(f"Erro de login: {result.get('error', 'Resposta desconhecida')}")
                        st.session_state.is_authenticated = False

                except requests.exceptions.RequestException as e:
                    st.error(f"Erro de conexão: Não foi possível conectar à API em {API_URL}.")
                    st.error(f"Detalhes: {e}")
                except json.JSONDecodeError as e:
                    st.error(f"Erro ao processar a resposta da API. O servidor não retornou um JSON válido.")
                    st.error(f"Resposta bruta da API: {response.text}")

    else:"""
        # Se o usuário estiver autenticado, mostre o conteúdo protegido
        st.success(f"Bem-vindo, {st.session_state.username}!")
        
        st.subheader("Unidades Geradoras (UGs) Permitidas")
        try:
            ug_response = requests.get(
                f"{API_URL}/user_ugs",
                params={"username": st.session_state.username}
            )
            ug_response.raise_for_status()
            ugs_data = ug_response.json()
            ugs_list = ugs_data.get("ugs", [])
            
            if ugs_list:
                st.session_state.selected_ug = st.selectbox("Selecione a UG para o levantamento:", options=['Selecione uma UG'] + ugs_list)
                if st.session_state.selected_ug != 'Selecione uma UG':
                    st.navigation('src/levantamento/app_levantamento.py')
            else:
                st.warning("Nenhuma UG encontrada para este usuário.")

        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao buscar as UGs: {e}")
            
        st.button("Sair", on_click=lambda: (
            st.session_state.update(is_authenticated=False, username=None),
            st.experimental_rerun()
        ))