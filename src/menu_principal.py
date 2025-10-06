import streamlit as st
import requests
import os
import json
from utils.env_loader import get_users
#from st_pages import Page, add_page_title, show_pages

def configurar_pagina():
    st.set_page_config(
        page_title='Menu Principal',
        page_icon='🏠',
        layout='wide')
    st.session_state.is_authenticated = False
    st.session_state.selected_ug = None
    st.session_state.username = None
    st.session_state.colunas_de_interesse = ['denominacao', 'status', 
                            'marca_total', 'modelo_total', 'serie_total', 
                            'localidade','acautelado para', 'tombo_antigo', 
                            'ultimo levantamento', 'valor',
                            'especificacoes','num tombamento']




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
    st.subheader('## Ir para:')
    col1, col2, col3 = st.columns(3)
    with col1:
        botao_levantamento = st.button("Levantamento")
        if botao_levantamento:
            st.switch_page(f"pages/levantamento.py")
    with col2:
        if os.path.exists(f'data_bronze/lista_bens-processado-{st.session_state.selected_ug}.csv'):
            botao_status = st.button("Status do Levantamento")
            if botao_status:
                st.switch_page(f"pages/status_levantamento.py")
    with col3:
        if st.session_state.username == 'admin':
            botao_atualizar = st.button("Atualizar Base")
            if botao_atualizar:
                st.switch_page(f"pages/atualizar_base.py")

# -- TELA PRINCIPAL --
# Configuração da página
configurar_pagina()

API_URL = "https://levantamento-patrimonial-api.onrender.com"

st.session_state.lista_todas_ugs = [
                                    'CGAD','DITEC','DIREN','DTI',
                                    'FIG',
                                    'SRAC', 'SRAL', 'SRAP',
                                    'SRAM', 'SRBA', 'SRCE',
                                    'SRDF','SRES','SRGO',
                                    'SRMA','SRMT','SRMS',
                                    'SRMG','SRPA','SRPB',
                                    'SRPR','SRPE','SRPI',
                                    'SRRJ','SRRN','SRRS',
                                    'SRRO','SRRR','SRSC',
                                    'SRSP','SRSE','SRTO',
                                    'GERAL']

st.title("Aplicativo de inventário patrimonial")

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
                    params={"username": st.session_state.username}
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

        