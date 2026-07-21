import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import google.generativeai as genai

# ----------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E DESIGN ESTILIZADO (CARDS)
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard SBOT 2026",
    page_icon="📊",
    layout="wide"
)

# Cores Oficiais SBOT
VERDE_SBOT = "#046A38"  # Pantone 562C
CINZA_SBOT = "#333F48"  # Pantone 432

# Estilização CSS personalizada para dar visual moderno de Cards
st.markdown(f"""
    <style>
        /* Títulos */
        h1, h2, h3, h4 {{ 
            color: {VERDE_SBOT} !important; 
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
        }}
        
        /* Container/Cards customizados */
        div[data-testid="stMetric"] {{
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-left: 5px solid {VERDE_SBOT};
            padding: 15px 20px;
            border-radius: 8px;
            box-shadow: 0px 2px 6px rgba(0,0,0,0.05);
        }}
        
        /* Estilo dos Rótulos dos Cards */
        div[data-testid="stMetricLabel"] {{
            color: {CINZA_SBOT} !important;
            font-size: 14px !important;
            font-weight: 600;
        }}
        
        /* Estilo dos Números dos Cards */
        div[data-testid="stMetricValue"] {{
            color: {VERDE_SBOT} !important;
            font-size: 28px !important;
            font-weight: bold;
        }}

        /* Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: #F8F9FA;
            border-right: 1px solid #EAEAEA;
        }}
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------
st.sidebar.image("https://sbot.org.br/wp-content/uploads/2021/04/logo-sbot.png", width=180)
st.sidebar.title("Painel de Controle")
GEMINI_API_KEY = st.sidebar.text_input("Google AI Studio API Key", type="password")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ----------------------------------------------------
# LEITURA ROBUSTA DOS DADOS
# ----------------------------------------------------
@st.cache_data(ttl=180)
def carregar_dados_icongresso(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        req = requests.get(url, headers=headers, timeout=20)
        if req.status_code == 200:
            # Tenta extrair todas as tabelas contidas na página
            tabelas = pd.read_html(io.StringIO(req.text))
            for df in tabelas:
                # Retorna a primeira tabela que tiver mais de 1 linha/coluna relevante
                if df.shape[0] > 0 and df.shape[1] > 1:
                    # Limpa nomes das colunas tirando espaços extras
                    df.columns = [str(col).strip().lower() for col in df.columns]
                    return df
    except Exception as e:
        st.error(f"Erro ao conectar com {url}: {e}")
    return None

# URLs Oficiais
URL_ATIVIDADE = "https://bit.ly/Qtd_inscritos_Atividade"
URL_PALESTRANTES = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/30501/type/quantitativo/idioma_ext/1/cc_ext/190"
URL_PATROCINADOS = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/1977/type/quantitativo/idioma_ext/1/cc_ext/190"

# ----------------------------------------------------
# CABEÇALHO DO DASHBOARD
# ----------------------------------------------------
st.title("📊 Dashboard Executivo - Congresso SBOT 2026")
st.caption("Acompanhamento em tempo real das inscrições e palestrantes")
st.divider()

# ====================================================
# SESSÃO 1: INSCRIÇÕES GERAIS (CONGRESSO)
# ====================================================
st.header("1. Inscrições Gerais (Congresso)")

df_atividade = carregar_dados_icongresso(URL_ATIVIDADE)

if df_atividade is not None and not df_atividade.empty:
    col_nome = [c for c in df_atividade.columns if any(k in c for k in ['nome', 'atividade', 'descri'])][0]
    
    # Exclui Ultrassonografia e Ondas de Choque dos Cards Principais
    df_congresso_only = df_atividade[
        df_atividade[col_nome].astype(str).str.contains("CONGRESSO", case=False, na=False) &
        ~df_atividade[col_nome].astype(str).str.contains("ULTRASSONOGRAFIA|ONDAS DE CHOQUE|CUSME", case=False, na=False)
    ]

    def extrair_valor(df, nome_col):
        cols = [c for c in df.columns if nome_col in c]
        if cols and not df.empty:
            val = pd.to_numeric(df[cols[0]], errors='coerce').fillna(0).sum()
            return int(val)
        return 0

    if not df_congresso_only.empty:
        qtd_pagas = extrair_valor(df_congresso_only, 'qtd_inscrito')
        qtd_cortesia = extrair_valor(df_congresso_only, 'qtd_cortesia')
        qtd_voucher = extrair_valor(df_congresso_only, 'voucher')
        total_geral_congresso = extrair_valor(df_congresso_only, 'qtd_total')
    else:
        qtd_pagas, qtd_cortesia, qtd_voucher, total_geral_congresso = 0, 0, 0, 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inscrições Pagas", f"{qtd_pagas:,}".replace(",", "."))
    c2.metric("Inscrições Cortesia", f"{qtd_cortesia:,}".replace(",", "."))
    c3.metric("Voucher Cortesia", f"{qtd_voucher:,}".replace(",", "."))
    c4.metric("Total Geral (Congresso)", f"{total_geral_congresso:,}".replace(",", "."))

    with st.expander("📄 Ver detalhamento geral por atividades (Inclui Ultrassonografia e Ondas de Choque)"):
        st.dataframe(df_atividade, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 2: PALESTRANTES
# ====================================================
st.header("2. Palestrantes")

df_palestrantes = carregar_dados_icongresso(URL_PALESTRANTES)

if df_palestrantes is not None and not df_palestrantes.empty:
    # Função auxiliar para somar colunas de forma segura
    def somar_col(df, termos):
        cols = [c for c in df.columns if any(t in c for t in termos)]
        if cols:
            return int(pd.to_numeric(df[cols[0]], errors='coerce').fillna(0).sum())
        return 0

    tot_palestrantes = somar_col(df_palestrantes, ['total', 'qtd_total'])
    aceito = somar_col(df_palestrantes, ['sim', 'aceito', 'qtd_sim'])
    pendente = somar_col(df_palestrantes, ['pendente', 'qtd_pendente'])
    rejeitado = somar_col(df_palestrantes, ['nao', 'não', 'rejeitado', 'qtd_nao'])

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Total de Palestrantes", f"{tot_palestrantes:,}".replace(",", "."))
    p2.metric("Convite Aceito", f"{aceito:,}".replace(",", "."))
    p3.metric("Convite Pendente", f"{pendente:,}".replace(",", "."))
    p4.metric("Convite Rejeitado", f"{rejeitado:,}".replace(",", "."))

    st.subheader("⚠️ Palestrantes que Aceitaram mas NÃO se Inscreveram")
    
    col_sim = [c for c in df_palestrantes.columns if 'sim' in c or 'aceito' in c]
    col_insc = [c for c in df_palestrantes.columns if 'inscrito' in c]

    if col_sim and col_insc:
        df_p = df_palestrantes.copy()
        df_p['sim_num'] = pd.to_numeric(df_p[col_sim[0]], errors='coerce').fillna(0)
        df_p['insc_num'] = pd.to_numeric(df_p[col_insc[0]], errors='coerce').fillna(0)
        df_p['pendentes_inscricao'] = df_p['sim_num'] - df_p['insc_num']
        
        col_cat = df_p.columns[0]
        fig_palestrantes = px.bar(
            df_p,
            x=col_cat,
            y='pendentes_inscricao',
            labels={col_cat: 'Categoria', 'pendentes_inscricao': 'Falta Inscrever'},
            color_discrete_sequence=[VERDE_SBOT],
            title="Aceitaram Convite mas ainda não completaram a Inscrição"
        )
        st.plotly_chart(fig_palestrantes, use_container_width=True)
    
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
    col_conv = df_patrocinadas.columns[0]
    
    # Aplica o filtro de exclusão dos convênios/descontos
    df_patroc_filtrado = df_patrocinadas[~df_patrocinadas[col_conv].astype(str).str.strip().isin(GRUPOS_EXCLUIR)]

    col_tot = [c for c in df_patroc_filtrado.columns if 'total' in c or 'qtd_total' in c]
    col_ins = [c for c in df_patroc_filtrado.columns if 'inscrito' in c or 'qtd_inscrito' in c]

    if col_tot and col_ins:
        qtd_vendidas = int(pd.to_numeric(df_patroc_filtrado[col_tot[0]], errors='coerce').fillna(0).sum())
        qtd_efetivadas = int(pd.to_numeric(df_patroc_filtrado[col_ins[0]], errors='coerce').fillna(0).sum())
        qtd_nao_efetivadas = qtd_vendidas - qtd_efetivadas
    else:
        qtd_vendidas, qtd_efetivadas, qtd_nao_efetivadas = 0, 0, 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Quantidade Vendida", f"{qtd_vendidas:,}".replace(",", "."))
    m2.metric("Inscrições Efetivadas", f"{qtd_efetivadas:,}".replace(",", "."))
    m3.metric("Inscrições NÃO Efetivadas", f"{qtd_nao_efetivadas:,}".replace(",", "."))

    with st.expander("📄 Ver detalhamento das inscrições patrocinadas"):
        st.dataframe(df_patroc_filtrado, use_container_width=True)

# ====================================================
# AGENTE IA - GOOGLE AI STUDIO (GEMINI)
# ====================================================
st.divider()
st.subheader("🤖 Diagnóstico de Inteligência Executiva")

if GEMINI_API_KEY:
    if st.button("✨ Gerar Análise Estratégica"):
        with st.spinner("Analisando métricas do iCongresso..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = "Gere um resumo executivo com 3 ações recomendadas com base nas inscrições do evento SBOT."
            response = model.generate_content(prompt)
            st.markdown(response.text)
