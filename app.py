import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import google.generativeai as genai

# ----------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E TEMA VISUAL SBOT
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard SBOT 2026",
    page_icon="📊",
    layout="wide"
)

# Cores Oficiais da Marca SBOT
VERDE_SBOT = "#046A38"  # Pantone 562C
CINZA_SBOT = "#333F48"  # Pantone 432

st.markdown(f"""
    <style>
        /* Tipografia e Títulos com a cor oficial */
        h1, h2, h3, h4 {{ color: {VERDE_SBOT} !important; font-family: 'Gothan', sans-serif; }}
        .stMetricValue {{ color: {VERDE_SBOT} !important; font-weight: bold; }}
        
        /* Botão estilizado */
        .stButton>button {{
            background-color: {VERDE_SBOT} !important;
            color: white !important;
            border-radius: 6px;
            border: none;
        }}
        /* Fundo da Sidebar */
        section[data-testid="stSidebar"] {{
            background-color: #F4F6F8;
        }}
    </style>
""", unsafe_unsafe_html=True if hasattr(st, 'unsafe_html') else True)

# ----------------------------------------------------
# CONFIGURAÇÃO DE SIDEBAR
# ----------------------------------------------------
st.sidebar.image("https://sbot.org.br/wp-content/uploads/2021/04/logo-sbot.png", width=180)
st.sidebar.title("Configurações")
GEMINI_API_KEY = st.sidebar.text_input("Google AI Studio API Key", type="password")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ----------------------------------------------------
# FUNÇÃO DE CARREGAMENTO SEGURO VIA REQUESTS
# ----------------------------------------------------
@st.cache_data(ttl=300)
def carregar_tabela(url):
    """Carrega as tabelas HTML via requisição HTTP para evitar erros de arquivo local."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            tables = pd.read_html(response.text)
            if tables:
                return tables[0]
    except Exception as e:
        st.error(f"Erro ao conectar com a base de dados: {e}")
    return None

# Endereços oficiais das bases
URL_ATIVIDADE = "https://bit.ly/Qtd_inscritos_Atividade"
URL_PALESTRANTES = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/30501/type/quantitativo/idioma_ext/1/cc_ext/190"
URL_PATROCINADOS = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/1977/type/quantitativo/idioma_ext/1/cc_ext/190"

# ----------------------------------------------------
# CABEÇALHO DO DASHBOARD
# ----------------------------------------------------
st.title("📊 Dashboard Executivo - Congresso SBOT 2026")
st.caption("Painel integrado em tempo real às bases do iCongresso")
st.divider()

# ====================================================
# SESSÃO 1: INSCRIÇÕES GERAIS (CONGRESSO)
# ====================================================
st.header("1. Inscrições Gerais (Congresso)")

df_atividade = carregar_tabela(URL_ATIVIDADE)

if df_atividade is not None:
    col_nome = [c for c in df_atividade.columns if 'Nome' in c or 'Atividade' in c or 'descri' in c.lower()][0]
    
    # FILTRO ESTREITO: APENAS a linha referente à Inscrição Principal do Congresso nos Cards
    df_congresso_only = df_atividade[
        df_atividade[col_nome].astype(str).str.contains("CONGRESSO", case=False, na=False) &
        ~df_atividade[col_nome].astype(str).str.contains("ULTRASSONOGRAFIA|ONDAS DE CHOQUE|CUSME", case=False, na=False)
    ]

    if not df_congresso_only.empty:
        qtd_pagas = df_congresso_only['qtd_inscrito'].values[0] if 'qtd_inscrito' in df_congresso_only.columns else 0
        qtd_cortesia = df_congresso_only['qtd_cortesia'].values[0] if 'qtd_cortesia' in df_congresso_only.columns else 0
        qtd_voucher = df_congresso_only['qtde_voucher_cortesia'].values[0] if 'qtde_voucher_cortesia' in df_congresso_only.columns else 0
        total_geral_congresso = df_congresso_only['qtd_total'].values[0] if 'qtd_total' in df_congresso_only.columns else 0
    else:
        qtd_pagas, qtd_cortesia, qtd_voucher, total_geral_congresso = 0, 0, 0, 0

    # Exibição dos CARDS exclusivos do Congresso
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inscrições Pagas", f"{qtd_pagas}")
    c2.metric("Inscrições Cortesia", f"{qtd_cortesia}")
    c3.metric("Voucher Cortesia", f"{qtd_voucher}")
    c4.metric("Total Geral (Congresso)", f"{total_geral_congresso}")

    # Tabela Completa (incluindo Cursos de Ultrassonografia e Ondas de Choque)
    with st.expander("📄 Ver detalhamento geral por atividades (Inclui Cursos de Ultrassonografia e Ondas de Choque)"):
        st.dataframe(df_atividade, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 2: PALESTRANTES
# ====================================================
st.header("2. Palestrantes")

df_palestrantes = carregar_tabela(URL_PALESTRANTES)

if df_palestrantes is not None:
    # Ajuste e consolidação das nomenclaturas de métricas solicitadas
    tot_palestrantes = df_palestrantes['qtd_total'].sum() if 'qtd_total' in df_palestrantes.columns else 0
    aceito = df_palestrantes['qtd_sim'].sum() if 'qtd_sim' in df_palestrantes.columns else 0
    pendente = df_palestrantes['qtd_pendente'].sum() if 'qtd_pendente' in df_palestrantes.columns else 0
    rejeitado = df_palestrantes['qtd_nao'].sum() if 'qtd_nao' in df_palestrantes.columns else 0

    # 1) Cards com Nomenclaturas Específicas
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Total de Palestrantes", f"{tot_palestrantes}")
    p2.metric("Convite Aceito", f"{aceito}")
    p3.metric("Convite Pendente", f"{pendente}")
    p4.metric("Convite Rejeitado", f"{rejeitado}")

    st.subheader("⚠️ Palestrantes que Aceitaram mas NÃO se Inscreveram")
    
    # 2) Gráfico/Tabela de Palestrantes que aceitaram e não fizeram inscrição
    if 'qtd_sim' in df_palestrantes.columns and 'qtd_inscrito' in df_palestrantes.columns:
        df_aceito_sem_inscricao = df_palestrantes.copy()
        df_aceito_sem_inscricao['pendentes_inscricao'] = df_aceito_sem_inscricao['qtd_sim'] - df_aceito_sem_inscricao['qtd_inscrito']
        
        col_categoria = df_palestrantes.columns[0]
        fig_palestrantes = px.bar(
            df_aceito_sem_inscricao,
            x=col_categoria,
            y='pendentes_inscricao',
            labels={col_categoria: 'Categoria', 'pendentes_inscricao': 'Aceitaram s/ Inscrição'},
            color_discrete_sequence=[VERDE_SBOT],
            title="Quantidade de Palestrantes com Convite Aceito Pendentes de Inscrição"
        )
        st.plotly_chart(fig_palestrantes, use_container_width=True)
    
    with st.expander("📄 Ver tabela completa de status dos palestrantes"):
        st.dataframe(df_palestrantes, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 3: INSCRIÇÕES PATROCINADAS (CONVÊNIOS)
# ====================================================
st.header("3. Inscrições Patrocinadas")

df_patrocinadas = carregar_tabela(URL_PATROCINADOS)

# Lista completa de exclusões solicitadas (Grupos/Anuidades/Palestrantes)
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

if df_patrocinadas is not None:
    col_convenio = [c for c in df_patrocinadas.columns if 'descri' in c.lower() or 'convenio' in c.lower() or 'grupo' in c.lower()][0]
    
    # Aplicação estrita do filtro de exclusão
    df_patroc_filtrado = df_patrocinadas[~df_patrocinadas[col_convenio].astype(str).isin(GRUPOS_EXCLUIR)]

    # Cálculo dos totais após exclusão
    qtd_vendidas = df_patroc_filtrado['qtd_total'].sum() if 'qtd_total' in df_patroc_filtrado.columns else 0
    qtd_efetivadas = df_patroc_filtrado['qtd_inscrito'].sum() if 'qtd_inscrito' in df_patroc_filtrado.columns else 0
    qtd_nao_efetivadas = qtd_vendidas - qtd_efetivadas

    m1, m2, m3 = st.columns(3)
    m1.metric("Quantidade Vendida", f"{qtd_vendidas}")
    m2.metric("Inscrições Efetivadas", f"{qtd_efetivadas}")
    m3.metric("Inscrições NÃO Efetivadas", f"{qtd_nao_efetivadas}")

    with st.expander("📄 Ver detalhamento das inscrições patrocinadas (Filtros aplicados)"):
        st.dataframe(df_patroc_filtrado, use_container_width=True)

# ====================================================
# AGENTE IA - GOOGLE AI STUDIO (GEMINI)
# ====================================================
st.divider()
st.subheader("🤖 Diagnóstico de Inteligência Executiva")

if GEMINI_API_KEY:
    if st.button("✨ Gerar Análise Estratégica"):
        with st.spinner("Analisando métricas..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""
            Como analista de dados da SBOT, com base nas métricas atualizadas:
            - Inscrições Congresso: {total_geral_congresso} totais ({qtd_pagas} pagas).
            - Palestrantes: {aceito} convites aceitos, {pendente} pendentes e {rejeitado} rejeitados.
            - Patrocinadores: {qtd_vendidas} vagas vendidas com {qtd_nao_efetivadas} ainda não efetivadas.
            
            Apresente 3 recomendações operacionais curtas e objetivas para a equipe do congresso.
            """
            response = model.generate_content(prompt)
            st.markdown(response.text)
