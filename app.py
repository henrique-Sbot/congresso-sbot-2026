import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import google.generativeai as genai

# ----------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E DESIGN PREMIUM SBOT
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard Executivo SBOT 2026",
    page_icon="📊",
    layout="wide"
)

# Cores Oficiais SBOT
VERDE_SBOT = "#046A38"
CINZA_SBOT = "#333F48"

# Estilização CSS Premium para Cards e Sombras
st.markdown(f"""
    <style>
        body {{
            background-color: #F8F9FA;
        }}
        h1, h2, h3, h4 {{ 
            color: {VERDE_SBOT} !important; 
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }}
        
        /* Layout dos Cards Premium */
        div[data-testid="stMetric"] {{
            background: linear-gradient(135deg, #FFFFFF 0%, #F8F9FA 100%);
            border: 1px solid #E2E8F0;
            border-top: 4px solid {VERDE_SBOT};
            padding: 18px;
            border-radius: 10px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        
        div[data-testid="stMetricLabel"] {{
            color: {CINZA_SBOT} !important;
            font-size: 13px !important;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        div[data-testid="stMetricValue"] {{
            color: {VERDE_SBOT} !important;
            font-size: 30px !important;
            font-weight: 800;
        }}

        section[data-testid="stSidebar"] {{
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }}
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------
st.sidebar.image("https://sbot.org.br/wp-content/uploads/2021/04/logo-sbot.png", width=180)
st.sidebar.title("Configurações")
GEMINI_API_KEY = st.sidebar.text_input("Google AI Studio API Key", type="password")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ----------------------------------------------------
# CARREGAMENTO DE DADOS
# ----------------------------------------------------
@st.cache_data(ttl=180)
def carregar_dados_icongresso(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        req = requests.get(url, headers=headers, timeout=20)
        if req.status_code == 200:
            tabelas = pd.read_html(io.StringIO(req.text))
            for df in tabelas:
                if df.shape[0] > 0 and df.shape[1] > 1:
                    df.columns = [str(col).strip().lower() for col in df.columns]
                    return df
    except Exception as e:
        st.error(f"Erro ao carregar URL: {e}")
    return None

URL_ATIVIDADE = "https://bit.ly/Qtd_inscritos_Atividade"
URL_PALESTRANTES = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/30501/type/quantitativo/idioma_ext/1/cc_ext/190"
URL_PATROCINADOS = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/1977/type/quantitativo/idioma_ext/1/cc_ext/190"

# ----------------------------------------------------
# CABEÇALHO DO DASHBOARD
# ----------------------------------------------------
st.title("📊 Dashboard Executivo - Congresso SBOT 2026")
st.caption("Painel Integrado ao iCongresso")
st.divider()

# Variáveis globais para o Resumo dos Módulos
qtd_pagas, qtd_cortesia, qtd_voucher, total_geral_congresso = 0, 0, 0, 0
tot_palestrantes, aceito, pendente, rejeitado = 0, 0, 0, 0
qtd_vendidas, qtd_efetivadas, qtd_nao_efetivadas = 0, 0, 0

# ====================================================
# SESSÃO 1: INSCRIÇÕES GERAIS (CONGRESSO)
# ====================================================
st.header("1. Inscrições Gerais (Congresso)")
df_atividade = carregar_dados_icongresso(URL_ATIVIDADE)

if df_atividade is not None and not df_atividade.empty:
    col_nome = [c for c in df_atividade.columns if any(k in c for k in ['nome', 'atividade', 'descri'])][0]
    
    df_congresso_only = df_atividade[
        df_atividade[col_nome].astype(str).str.contains("CONGRESSO", case=False, na=False) &
        ~df_atividade[col_nome].astype(str).str.contains("ULTRASSONOGRAFIA|ONDAS DE CHOQUE|CUSME", case=False, na=False)
    ]

    def extrair_val(df, termo):
        cols = [c for c in df.columns if termo in c]
        if cols and not df.empty:
            return int(pd.to_numeric(df[cols[0]], errors='coerce').fillna(0).sum())
        return 0

    if not df_congresso_only.empty:
        qtd_pagas = extrair_val(df_congresso_only, 'qtd_inscrito')
        qtd_cortesia = extrair_val(df_congresso_only, 'qtd_cortesia')
        qtd_voucher = extrair_val(df_congresso_only, 'voucher')
        total_geral_congresso = extrair_val(df_congresso_only, 'qtd_total')

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inscrições Pagas", f"{qtd_pagas:,}".replace(",", "."))
    c2.metric("Inscrições Cortesia", f"{qtd_cortesia:,}".replace(",", "."))
    c3.metric("Voucher Cortesia", f"{qtd_voucher:,}".replace(",", "."))
    c4.metric("Total Geral (Congresso)", f"{total_geral_congresso:,}".replace(",", "."))

    with st.expander("📄 Ver detalhamento geral por atividades"):
        st.dataframe(df_atividade, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 2: PALESTRANTES
# ====================================================
st.header("2. Palestrantes")
df_palestrantes = carregar_dados_icongresso(URL_PALESTRANTES)

if df_palestrantes is not None and not df_palestrantes.empty:
    col_status = [c for c in df_palestrantes.columns if 'status' in c or 'convite' in c][0]
    col_qtd = [c for c in df_palestrantes.columns if 'quantidade' in c or 'qtd' in c][0]

    def pegar_qtd(status_nome):
        filtro = df_palestrantes[df_palestrantes[col_status].astype(str).str.contains(status_nome, case=False, na=False)]
        if not filtro.empty:
            return int(pd.to_numeric(filtro[col_qtd].values[0], errors='coerce'))
        return 0

    aceito = pegar_qtd("Aceitou")
    pendente = pegar_qtd("Convite Enviado") + pegar_qtd("Cadastrado")
    rejeitado = pegar_qtd("Rejeitado")
    
    filtro_total = df_palestrantes[df_palestrantes[col_status].isna() | (df_palestrantes[col_status].astype(str) == 'None')]
    if not filtro_total.empty:
        tot_palestrantes = int(pd.to_numeric(filtro_total[col_qtd].values[0], errors='coerce'))
    else:
        tot_palestrantes = aceito + pendente + rejeitado

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Total de Palestrantes", f"{tot_palestrantes:,}".replace(",", "."))
    p2.metric("Convite Aceito", f"{aceito:,}".replace(",", "."))
    p3.metric("Convite Pendente", f"{pendente:,}".replace(",", "."))
    p4.metric("Convite Rejeitado", f"{rejeitado:,}".replace(",", "."))

    with st.expander("📄 Ver tabela completa de status dos palestrantes"):
        st.dataframe(df_palestrantes, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 3: INSCRIÇÕES PATROCINADAS (CONVÊNIOS)
# ====================================================
st.header("3. Inscrições Patrocinadas")
df_patrocinadas = carregar_dados_icongresso(URL_PATROCINADOS)

GRUPOS_EXCLUIR = [
    "CONVÊNIO - APROVADOS TEOT 2026",
    "CONVÊNIO - EX PRESIDENTES",
    "CONVÊNIO - REMIDOS SBOT",
    "CONVÊNIO MEMBROS CEC 2026",
    "Desconto aplicado de 25% devido a inscrição no SBOTLAB 2026",
    "Desconto aplicado de R$ 115,00 devido pagamento da anuidade via APP.",
    "Desconto aplicado de R$ 230,00 devido pagamento da anuidade via APP.",
    "Desconto aplicado de R$ 345,00 devido pagamento da anuidade via APP.",
    "PALESTRANTES SBOT 2026"
]

if df_patrocinadas is not None and not df_patrocinadas.empty:
    col_conv = [c for c in df_patrocinadas.columns if 'convenio' in c or 'empresa' in c or 'descri' in c][0]
    df_patroc_filtrado = df_patrocinadas[~df_patrocinadas[col_conv].astype(str).str.strip().isin(GRUPOS_EXCLUIR)]

    col_vagas = [c for c in df_patrocinadas.columns if 'vagas (convênio)' in c or 'vagas' in c][0]
    col_conf = [c for c in df_patrocinadas.columns if 'confirmadas' in c][0]
    col_preencher = [c for c in df_patrocinadas.columns if 'preencher' in c][0]

    qtd_vendidas = int(pd.to_numeric(df_patroc_filtrado[col_vagas], errors='coerce').fillna(0).sum())
    qtd_efetivadas = int(pd.to_numeric(df_patroc_filtrado[col_conf], errors='coerce').fillna(0).sum())
    qtd_nao_efetivadas = int(pd.to_numeric(df_patroc_filtrado[col_preencher], errors='coerce').fillna(0).sum())

    m1, m2, m3 = st.columns(3)
    m1.metric("Quantidade Vendida", f"{qtd_vendidas:,}".replace(",", "."))
    m2.metric("Inscrições Efetivadas", f"{qtd_efetivadas:,}".replace(",", "."))
    m3.metric("Inscrições NÃO Efetivadas", f"{qtd_nao_efetivadas:,}".replace(",", "."))

    with st.expander("📄 Ver detalhamento das inscrições patrocinadas"):
        st.dataframe(df_patroc_filtrado, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 4: RESUMO CONSOLIDADOR DOS MÓDULOS (NOVO)
# ====================================================
st.header("4. Resumo Consolidado dos Módulos")
st.write("Visão geral simplificada para acompanhamento rápido da diretoria:")

# Cálculo do Total Geral Geral de Inscritos (Congresso + Patrocinados Efetivados)
total_participantes = total_geral_congresso + qtd_efetivadas

resumo_data = {
    "Módulo": [
        "1. Inscrições Gerais", 
        "2. Palestrantes", 
        "3. Inscrições Patrocinadas", 
        "TOTAL CONSOLIDADO EVENTO"
    ],
    "Métrica Principal": [
        f"{total_geral_congresso} Inscritos Totais ({qtd_pagas} Pagas)",
        f"{tot_palestrantes} Total ({aceito} Convites Aceitos)",
        f"{qtd_vendidas} Vagas Vendidas ({qtd_efetivadas} Efetivadas)",
        f"{total_participantes} Participantes Confirmados"
    ],
    "Status / Pendência": [
        f"{qtd_cortesia + qtd_voucher} CORTESIAS / VOUCHERS",
        f"{pendente} PENDENTES DE RESPOSTA",
        f"{qtd_nao_efetivadas} VAGAS A PREENCHER",
        "STATUS EM TEMPO REAL"
    ]
}

df_resumo = pd.DataFrame(resumo_data)
st.table(df_resumo)

# ====================================================
# AGENTE IA - GOOGLE AI STUDIO (GEMINI)
# ====================================================
st.divider()
st.subheader("🤖 Diagnóstico de Inteligência Executiva")

if GEMINI_API_KEY:
    if st.button("✨ Gerar Análise Estratégica"):
        with st.spinner("Analisando métricas..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Gere um resumo executivo baseado em {total_participantes} participantes confirmados no Congresso SBOT 2026."
            response = model.generate_content(prompt)
            st.markdown(response.text)
