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

def menu_navegacao():
    col1, col2 = st.columns(2)
    with col1:
        botao_levantamento = st.button("Ir para Levantamento")
        if botao_levantamento:
            st.switch_page(f"pages/app_levantamento.py")
    with col2:
        if st.session_state.username == 'admin':
            botao_atualizar = st.button("Ir para Atualizar Base")
            if botao_atualizar:
                st.switch_page(f"pages/app_atualizar_base.py")

API_URL = "http://127.0.0.1:8000"

st.title("Aplicativo de invnentário patrimonial")

st.header("Credenciamento")
#reiniciar st.session_state
st.button("Reiniciar Sessão", on_click=lambda: st.session_state.clear())


# A lista de usuários é carregada uma vez no início
users = ['Selecione um usuário', 'miguel.mpf', 'pericles.pd', 'getulio.gbs', 'mateus.mcpa', 'admin']
if not users:
    st.warning("Nenhum usuário encontrado na variável de ambiente USERS. Verifique seu arquivo .env.")
else:
    # Use st.session_state para manter o estado de login
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
        st.session_state.username = None

    if not st.session_state.is_authenticated:
        # Se o usuário não estiver autenticado, mostre o formulário de login
        username = st.selectbox("Usuário", options= users)
        #password = st.text_input("Senha", type="password")
        if username != 'Selecione um usuário':
            st.session_state.username = username

                
        try:
            ug_response = requests.get(
                f"{API_URL}/user_ugs",
                params={"username": username}
            )
            ug_response.raise_for_status()
            ugs_data = ug_response.json()
            ugs_list = ugs_data.get("ugs", [])
            selected_ug = st.selectbox("Selecione a UG para o levantamento:", options=['Selecione uma UG'] + ugs_list)
            if selected_ug != 'Selecione uma UG':
                st.session_state.selected_ug = selected_ug
                st.session_state.is_authenticated = True
                menu_navegacao()


        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao buscar as UGs: {e}")
                
    else:
        st.success(f"Usuário '{st.session_state.username}' autenticado com UG {st.session_state.selected_ug}.")
        menu_navegacao()

        