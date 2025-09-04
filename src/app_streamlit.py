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
        # Aqui você pode mostrar o menu principal ou navegar para outras páginas
    else:
        st.error(result.get("error", "Erro ao credenciar"))