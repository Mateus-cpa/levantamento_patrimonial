import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.title("Levantamento Patrimonial")

st.header("Credenciamento")
username = st.text_input("Usuário")
password = st.text_input("Senha", type="password")

if st.button("Entrar"):
    response = requests.post(
        f"{API_URL}/login",
        data={"username": username, "password": password}
    )
    result = response.json()
    if result.get("success"):
        st.success("Credenciado com sucesso!")
        # Buscar UGs permitidas para o usuário
        ug_response = requests.get(
            f"{API_URL}/user_ugs",
            params={"username": username}
        )
        ug_list = ug_response.json().get("ugs", [])
        if ug_list:
            selected_ug = st.selectbox("Selecione a UG", ug_list)
            if st.button("Confirmar UG"):
                st.success(f"UG selecionada: {selected_ug}")
                # Continue o fluxo principal aqui
        else:
            st.error("Nenhuma UG disponível para este usuário.")
        # Aqui você pode mostrar o menu principal ou navegar para outras páginas
    else:
        st.error(result.get("error", "Erro ao credenciar"))