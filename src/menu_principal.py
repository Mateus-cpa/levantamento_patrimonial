import streamlit as st
import requests
import os
import json

from dotenv import load_dotenv

# Carrega as variáveis de ambiente do .env
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")

USERS_RAW = os.getenv("USERS_LOCAL")
try:
    if USERS_RAW:
        USERS = json.loads(USERS_RAW)
    else:
        USERS = {}
except json.JSONDecodeError:
    st.error("Erro ao carregar a variável USERS do arquivo .env. Verifique a sintaxe JSON.")
    USERS = {}

def configurar_pagina():
    st.set_page_config(
        page_title='Menu Principal',
        page_icon='🏠',
        layout='wide')
    
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "selected_ug" not in st.session_state:
        st.session_state.selected_ug = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "perfil" not in st.session_state:
        st.session_state.perfil = 'usuario'

    st.session_state.colunas_de_interesse = [
        'num tombamento', 'denominacao', 'status', 
        'marca_total', 'modelo_total', 'serie_total', 
        'localidade','acautelado para', 'tombo_antigo', 
        'ultimo levantamento', 'valor', 'especificacoes'
    ]

@st.cache_data
def get_ugs_for_user(username):
    """Busca as UGs e o perfil do usuário na API."""
    try:
        # Nota: Idealmente, esta chamada deve ser autenticada (via JWT)
        response = requests.get(f"{API_URL}/user_ugs", params={"username": username}, timeout=120)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"ugs": [], "perfil": "usuario", "error": str(e)}

def menu_navegacao(perfil="usuario"):
    """Exibe os botões de navegação conforme o perfil."""
    st.subheader('## Ir para:')
    col_levantamento, col_relatorio, col_status, col_atualizar, col_admin = st.columns(5)
    
    with col_levantamento:
        if st.button("Levantamento"):
            st.switch_page("pages/levantamento.py")
    with col_status:
        # Verifica se o arquivo processado local existe
        if st.session_state.selected_ug and os.path.exists(f'data_bronze/lista_bens-processado-{st.session_state.selected_ug}.csv'):
            if st.button("Status do Levantamento"):
                st.switch_page("pages/status_levantamento.py")
    with col_relatorio:
        if st.button("Relatório do Levantamento"):
            st.switch_page("pages/relatorio_levantamento.py")
    with col_atualizar:
        if perfil == 'analista' or perfil == 'admin':
            if st.button("Atualizar Base"):
                st.switch_page("pages/atualizar_base.py")
    with col_admin:
        # Botão para a futura tela de gerenciamento de usuários
        if perfil == 'admin':
            if st.button("Gerenciar Usuários"):
                # Você criaria este arquivo pages/gerenciar_usuarios.py
                st.switch_page("pages/gerenciar_usuarios.py")

def handle_login(username, password):
    """Lógica de autenticação local (para transição) ou via API (futuramente)."""
    # ⚠️ ATENÇÃO: Autenticação local apenas para demonstração do .env
    user_info = USERS.get(username)
    if user_info and user_info["senha"] == password:
        st.session_state.username = username
        st.session_state.local_perfil = user_info["perfil"]
        
        # Chamada à API para obter UGs (que ainda não exige senha)
        user_data = get_ugs_for_user(username)
        error = user_data.get("error")
        
        if error:
            st.session_state.is_authenticated = False
            st.session_state.username = None
            # Tratamento de erro de conexão
            st.error("❌ Falha ao carregar UGs da API. Tente novamente.")
            st.caption(f"Erro técnico: {error}")
            return False
        
        ugs_list = user_data.get("ugs", [])
        
        # Se a autenticação foi bem-sucedida, prossegue para seleção da UG
        st.session_state.ugs_list = ugs_list
        return True
    else:
        st.error("Usuário ou senha incorretos.")
        return False
    
                    
# -- TELA PRINCIPAL --
configurar_pagina()

st.title("Aplicativo de inventário patrimonial")
st.header("Credenciamento")
st.button("Reiniciar Sessão", on_click=lambda: st.session_state.clear())

users = ['Selecione um usuário', 'celso.cfs', 'miguel.mpf', 'pericles.pd', 'getulio.gbs', 'mateus.mcpa', 'admin']

if not users:
    st.warning("Nenhum usuário encontrado na variável de ambiente USERS. Verifique seu arquivo .env.")
else:
    if not st.session_state.is_authenticated:
        username = st.selectbox("Usuário", options=users)
        if username != 'Selecione um usuário':
            st.session_state.username = username
            with st.spinner("Carregando UGs..."):
                user_data = get_ugs_for_user(username)
            ugs_list = user_data.get("ugs", [])
            perfil = user_data.get("perfil", "usuario").strip().lower()
            error = user_data.get("error", None)
            if error:
                st.error(f"Erro ao buscar as UGs: {error}")
            else:
                selected_ug = st.selectbox("Selecione a UG para o levantamento:", options=['Selecione uma UG'] + ugs_list)
                if selected_ug != 'Selecione uma UG':
                    st.session_state.selected_ug = selected_ug
                    st.session_state.is_authenticated = True
                    st.session_state.perfil = perfil
                    st.success(f"Usuário '{username}' autenticado com UG {selected_ug}. Perfil: {perfil}")
                    menu_navegacao(perfil)
    else:
        perfil = st.session_state.get("perfil", "usuario").strip().lower()
        st.success(f"Usuário '{st.session_state.username}' autenticado com UG {st.session_state.selected_ug}. Perfil: {perfil}")
        menu_navegacao(perfil)

