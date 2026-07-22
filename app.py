import streamlit as st

# 1. Configuração da Página com a Logo e Título
st.set_page_config(
    page_title="Congresso SBOT | Porto Alegre 2026",
    page_icon="https://sbot.org.br/wp-content/uploads/2021/04/favicon.png",
    layout="wide"
)

# 2. Injeção de CSS para Paleta de Cores SBOT
sbot_css = """
<style>
    /* Cores Globais SBOT */
    :root {
        --sbot-green: #046A38;
        --sbot-dark-gray: #333F48;
        --sbot-light-gray: #F4F6F7;
    }

    /* Estilização de Títulos */
    h1, h2, h3 {
        color: var(--sbot-green) !important;
        font-family: 'Gothan', 'Helvetica Neue', sans-serif !important;
    }

    /* Barra Lateral (Sidebar) */
    [data-testid="stSidebar"] {
        background-color: var(--sbot-dark-gray) !important;
        color: #FFFFFF !important;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    /* Métricas / Cards */
    [data-testid="stMetricValue"] {
        color: var(--sbot-green) !important;
        font-weight: bold;
    }

    /* Botões */
    div.stButton > button:first-child {
        background-color: var(--sbot-green) !important;
        color: white !important;
        border-radius: 4px;
        border: none;
    }

    div.stButton > button:first-child:hover {
        background-color: #03522c !important;
    }

    /* Caixas de Alerta / Informação */
    .stAlert {
        border-left-color: var(--sbot-green) !important;
    }
</style>
"""
st.markdown(sbot_css, unsafe_allow_html=True)

# 3. Exibição da Logo na Sidebar / Topo
st.sidebar.image(
    "https://sbot.org.br/wp-content/uploads/2021/04/logo-sbot.png", 
    use_container_width=True
)

st.title("Congresso SBOT | Porto Alegre 2026")
