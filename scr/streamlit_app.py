import sys
import streamlit as st
from services.auth import carregar_usuarios, salvar_usuario, autenticar
from components.dashboard import exibir_dashboard
from components.segmentacao import exibir_segmentacao
from components.metas_funil import exibir_calculadora
from components.churn import exibir_churn
# Importação comentada para MVP inicial
# from components.tamsamsom import exibir_tamsamsom
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PIL import Image

# Carregando a logo
logo_path = os.path.join(os.path.dirname(__file__), "assets", "don_logo.png")
logo_img = Image.open(logo_path)

# Configuração da página
st.set_page_config(
    page_title="SaaS",
    page_icon=logo_img,
    layout="wide"
)

# Inicialização de sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = ""
    
# Inicialização dos estados para dados calculados
if "icp_data" not in st.session_state:
    st.session_state["icp_data"] = None

# Tela de Login
def exibir_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Logo centralizada com tamanho menor
        st.image(logo_img, width=60, use_container_width=False)
        
        # Mensagem de boas-vindas
        st.markdown("""
        <div style='text-align: center; margin-bottom: 30px;'>
            <h1>Bem-vindo à Don!</h1>
            <p style='font-size: 18px; color: #666;'>
                Sua plataforma inteligente para análise e gestão de SaaS.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: left;'>
            <h1 style='font-size: 1.5rem;'>🔐 Login</h1>
        </div>
        """, unsafe_allow_html=True)
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

# Verificação de Login
if not st.session_state["logado"]:
    exibir_login()
    st.stop()

# SIDEBAR COM ABAS
col1, col2 = st.sidebar.columns([1, 3])
with col1:
    st.image(logo_img, width=50)
with col2:
    st.title("Cardápio")
st.sidebar.markdown(f"👤 **{st.session_state['usuario']}**")

# Botão de logout na sidebar
if st.sidebar.button("📤 Sair"):
    # Limpar todos os dados da sessão
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Seleção de páginas
pagina = st.sidebar.radio(
    "Navegação",
    ["📊 Análise de ICP", 
     "🎯 Segmentação", 
     "📈 Metas & Projeções",
     "🔮 Previsão de Churn"] + 
    # TAM/SAM/SOM comentado para MVP inicial
    # ["🎯 TAM/SAM/SOM"] +
    (["⚙️ Administração"] if st.session_state["usuario"] == "admin" else []),
    key="navegacao"
)

# Conteúdo principal baseado na seleção
if pagina == "📊 Análise de ICP":
    exibir_dashboard()
    
elif pagina == "🎯 Segmentação":
    exibir_segmentacao()

elif pagina == "📈 Metas & Projeções":
    exibir_calculadora()

elif pagina == "🔮 Previsão de Churn":
    exibir_churn()

# TAM/SAM/SOM comentado para MVP inicial
# elif pagina == "🎯 TAM/SAM/SOM":
#     exibir_tamsamsom()

elif pagina == "⚙️ Administração" and st.session_state["usuario"] == "admin":
    st.title("Painel Administrativo")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        usuarios = carregar_usuarios()
        st.markdown("### Usuários existentes:")
        for user in usuarios:
            st.markdown(f"- **{user}**")

    with col2:
        st.markdown("### Criar ou atualizar usuário")
        novo_user = st.text_input("Novo usuário ou existente")
        nova_senha = st.text_input("Senha", type="password", key="nova_senha")

        if st.button("Salvar usuário"):
            if novo_user and nova_senha:
                salvar_usuario(novo_user, nova_senha)
                st.success(f"Usuário '{novo_user}' salvo com sucesso.")
                st.rerun()
            else:
                st.error("Preencha o nome de usuário e a senha.")
