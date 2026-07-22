import streamlit as st
import pandas as pd
import requests
import io
import re
import google.generativeai as genai

# Configuração principal da página
st.set_page_config(
    page_title="Congresso SBOT | Porto Alegre 2026",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada de alta precisão
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #F8FAFC;
        }

        .main-header {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            color: #FFFFFF;
            padding: 24px 30px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 20px rgba(15, 23, 42, 0.12);
        }
        .main-header h1 {
            color: #FFFFFF !important;
            font-size: 28px;
            font-weight: 800;
            margin: 0;
        }
        .main-header p {
            color: #94A3B8;
            font-size: 14px;
            margin-top: 6px;
            margin-bottom: 0;
        }

        .section-header {
            color: #0F172A;
            font-size: 20px;
            font-weight: 800;
            margin-top: 25px;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
        }
        .section-header::before {
            content: "";
            display: inline-block;
            width: 6px;
            height: 24px;
            background-color: #0284C7;
            margin-right: 12px;
            border-radius: 4px;
        }

        .stat-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: 4px solid #0284C7;
            border-radius: 10px 10px 0px 0px;
            padding: 18px 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }
        .stat-card.orange { border-top-color: #EA580C; }
        .stat-card.green { border-top-color: #10B981; }
        .stat-card.purple { border-top-color: #8B5CF6; }
        
        .stat-value {
            font-size: 32px;
            font-weight: 800;
            color: #0F172A;
            line-height: 1;
        }
        .stat-value.blue { color: #0284C7; }
        .stat-value.orange { color: #EA580C; }
        .stat-value.green { color: #10B981; }
        .stat-value.purple { color: #8B5CF6; }
        
        .stat-label {
            font-size: 11px;
            font-weight: 700;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 8px;
        }

        .info-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: none;
            border-radius: 0px 0px 10px 10px;
            padding: 14px 16px;
            margin-bottom: 20px;
            min-height: 110px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        }
        .info-icon { font-size: 30px; margin-bottom: 4px; }
        .info-title { font-size: 15px; font-weight: 700; color: #0F172A; margin-bottom: 4px; }
        .info-desc { font-size: 13px; color: #64748B; line-height: 1.4; }

        .ai-box {
            background: #F0F9FF;
            border: 1px solid #BAE6FD;
            border-left: 5px solid #0284C7;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

st.sidebar.image("https://sbot.org.br/wp-content/uploads/2021/04/logo-sbot.png", width=180)
st.sidebar.title("Painel Executivo")
st.sidebar.markdown("---")

GEMINI_API_KEY = st.sidebar.text_input("Google AI Studio API Key", type="password", help="Insira sua chave para ativar o diagnóstico preditivo por IA")

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        st.sidebar.success("⚡ Gemini AI Conectado!")
    except Exception as e:
        st.sidebar.error("Erro ao configurar API Gemini.")

st.sidebar.markdown("---")
st.sidebar.info("📌 **Atualização Dinâmica:** Os dados são sincronizados diretamente com as APIs e relatórios HTML do iTarget.")

@st.cache_data(ttl=180)
def carregar_dados_icongresso(url):
    """Carrega e limpa tabelas extraídas das URLs de relatórios iTarget."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        req = requests.get(url, headers=headers, timeout=20)
        if req.status_code == 200:
            tabelas = pd.read_html(io.StringIO(req.text))
            for df in tabelas:
                if df.shape[0] > 0 and df.shape[1] > 1:
                    df.columns = [str(col).strip().lower() for col in df.columns]
                    return df
    except Exception as e:
        pass
    return None

MAPA_ESTADOS = {
    'ACRE': 'AC', 'ALAGOAS': 'AL', 'AMAPA': 'AP', 'AMAZONAS': 'AM', 'BAHIA': 'BA',
    'CEARA': 'CE', 'DISTRITO FEDERAL': 'DF', 'ESPIRITO SANTO': 'ES', 'GOIAS': 'GO',
    'MARANHAO': 'MA', 'MATO GROSSO DO SUL': 'MS', 'MATO GROSSO': 'MT', 'MINAS GERAIS': 'MG',
    'PARA': 'PA', 'PARAIBA': 'PB', 'PARANA': 'PR', 'PERNAMBUCO': 'PE', 'PIAUI': 'PI',
    'RIO DE JANEIRO': 'RJ', 'RIO GRANDE DO NORTE': 'RN', 'RIO GRANDE DO SUL': 'RS',
    'RONDONIA': 'RO', 'RORAIMA': 'RR', 'SANTA CATARINA': 'SC', 'SAO PAULO': 'SP',
    'SERGIPE': 'SE', 'TOCANTINS': 'TO'
}

def normalizar_uf(texto):
    """Mapeia nomes completos de estados para siglas de UF."""
    txt = str(texto).strip().upper()
    if txt in MAPA_ESTADOS.values():
        return txt
    for nome, sigla in MAPA_ESTADOS.items():
        if nome in txt:
            return sigla
    return None

def extrair_dados_geograficos(df, nome_valor):
    """Extrai siglas de UF e valores numéricos associados de tabelas brutas."""
    registros = []
    if df is None or df.empty:
        return pd.DataFrame(columns=['UF', nome_valor])

    for _, row in df.iterrows():
        uf_encontrada = None
        valor_encontrado = 0
        
        for cell in row.values:
            uf_test = normalizar_uf(cell)
            if uf_test:
                uf_encontrada = uf_test
                break
        
        if uf_encontrada:
            for cell in reversed(row.values):
                val_str = str(cell).replace('.', '').replace(',', '.').strip()
                if val_str.isdigit():
                    valor_encontrado = int(val_str)
                    break
                else:
                    nums = re.findall(
