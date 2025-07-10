import streamlit as st
from services.auth import autenticar, carregar_usuarios

def exibir_login():
    st.title("SaleSniper - 🔐 Login")
    usuarios = carregar_usuarios()

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password", key="senha_login")

    if st.button("Entrar"):
        if autenticar(usuario, senha, usuarios):
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")
