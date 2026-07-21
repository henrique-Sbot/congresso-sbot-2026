import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import google.generativeai as genai

# ----------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E TEMA SBOT
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard SBOT 2026",
    page_icon="📊",
    layout="wide"
)

# Estilização CSS utilizando as Cores Oficiais da SBOT
VERDE_SBOT = "#046A38"  # Pantone 562C
CINZA_SBOT = "#333F48"   # Pantone 432

st.markdown(f"""
    <style>
        /* Estilo dos Títulos e Métricas */
        h1, h2, h3 {{ color: {VERDE_SBOT} !important; font-family: 'Gothan', sans-serif; }}
        .stMetricValue {{ color: {VERDE_SBOT} !important; font-weight: bold; }}
        .stButton>button {{
            background-color: {VERDE_SBOT} !important;
            color: white !important;
            border-radius: 8px;
            border: none;
        }}
        /* Estilo da barra lateral */
        section[data-testid="stSidebar"] {{
            background-color: #f4f6f8;
        }}
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# CONFIGURAÇÃO DA API GEMINI (GOOGLE AI STUDIO)
# ----------------------------------------------------
st.sidebar.image("https://sbot.org.br/wp-content/uploads/2021/04/logo-sbot.png", width=200)
st.sidebar.title("Configurações")
GEMINI_API_KEY = st.sidebar.text_input("Google AI Studio API Key", type="password")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ----------------------------------------------------
# FUNÇÃO PARA EXTRAIR DADOS DAS URLS
# ----------------------------------------------------
@st.cache_data(ttl=300)
def carregar_tabela(url):
    """Acessa a URL dinamicamente e lê a tabela HTML."""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            tables = pd.read_html(response.text)
            if tables:
                return tables[0]
    except Exception as e:
        st.error(f"Erro ao carregar dados do link: {e}")
    return None

# URLs Oficiais fornecidas
URL_ATIVIDADE = "https://bit.ly/Qtd_inscritos_Atividade"
URL_PALESTRANTES_STATUS = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/30501/type/quantitativo/idioma_ext/1/cc_ext/190"
URL_PATROCINADOS = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/1977/type/quantitativo/idioma_ext/1/cc_ext/190"

# ----------------------------------------------------
# TÍTULO PRINCIPAL
# ----------------------------------------------------
st.title("📊 Dashboard Executivo - Congresso SBOT 2026")
st.caption("Painel em tempo real integrado às bases do iCongresso")
st.divider()

# ====================================================
# SESSÃO 1: INSCRIÇÕES GERAIS (CONGRESSO)
# ====================================================
st.header("1. Inscrições Gerais (Congresso)")

df_atividade = carregar_tabela(URL_ATIVIDADE)

if df_atividade is not None:
    # Filtragem específica: APENAS a linha da 'INSCRIÇÃO PARA O 58º CONGRESSO ANUAL SBOT' para os CARDS
    # Cursos extras (Ultrassonografia, Ondas de Choque) NÃO entram nos Cards, apenas na tabela abaixo.
    col_nome = [c for c in df_atividade.columns if 'Nome' in c or 'Atividade' in c][0]
    df_congresso_only = df_atividade[df_atividade[col_nome].astype(str).str.contains("CONGRESSO", case=False, na=False)]

    if not df_congresso_only.empty:
        qtd_pagas = df_congresso_only['qtd_inscrito'].values[0] if 'qtd_inscrito' in df_congresso_only.columns else 0
        qtd_cortesia = df_congresso_only['qtd_cortesia'].values[0] if 'qtd_cortesia' in df_congresso_only.columns else 0
        qtd_voucher = df_congresso_only['qtde_voucher_cortesia'].values[0] if 'qtde_voucher_cortesia' in df_congresso_only.columns else 0
        total_geral_congresso = df_congresso_only['qtd_total'].values[0] if 'qtd_total' in df_congresso_only.columns else 0
    else:
        qtd_pagas, qtd_cortesia, qtd_voucher, total_geral_congresso = 0, 0, 0, 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inscrições Pagas", f"{qtd_pagas}")
    c2.metric("Inscrições Cortesia", f"{qtd_cortesia}")
    c3.metric("Voucher Cortesia", f"{qtd_voucher}")
    c4.metric("Total Geral (Congresso)", f"{total_geral_congresso}")

    with st.expander("📄 Ver detalhamento geral por atividades (incluindo Cursos CUSME e Ondas de Choque)"):
        st.dataframe(df_atividade, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 2: PALESTRANTES
# ====================================================
st.header("2. Palestrantes")

df_palestrantes = carregar_tabela(URL_PALESTRANTES_STATUS)

if df_palestrantes is not None:
    # Mapeamento dinâmico das colunas conforme o relatório retornado
    # Ajustar a lógica de soma com base nos cabeçalhos exatos do relatório 30501
    tot_palestrantes = df_palestrantes['qtd_total'].sum() if 'qtd_total' in df_palestrantes.columns else 0
    aceito = df_palestrantes['qtd_sim'].sum() if 'qtd_sim' in df_palestrantes.columns else 0
    pendente = df_palestrantes['qtd_pendente'].sum() if 'qtd_pendente' in df_palestrantes.columns else 0
    rejeitado = df_palestrantes['qtd_nao'].sum() if 'qtd_nao' in df_palestrantes.columns else 0

    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Total de Palestrantes", f"{tot_palestrantes}")
    p2.metric("Convite Aceito", f"{aceito}")
    p3.metric("Convite Pendente", f"{pendente}")
    p4.metric("Convite Rejeitado", f"{rejeitado}")

    st.subheader("⚠️ Alerta de Inscrição: Convite Aceito x Sem Inscrição")
    # Lógica para quantificar quem aceitou mas ainda não realizou inscrição
    if 'inscrito' in df_palestrantes.columns:
        palestrantes_pendentes_inscricao = df_palestrantes[(df_palestrantes['aceitou'] == 'Sim') & (df_palestrantes['inscrito'] == 'Não')]
        
        fig_palestrantes = px.bar(
            palestrantes_pendentes_inscricao,
            x='nome_palestrante' if 'nome_palestrante' in df_palestrantes.columns else df_palestrantes.columns[0],
            y='quantidade' if 'quantidade' in df_palestrantes.columns else df_palestrantes.columns[1],
            color_discrete_sequence=[VERDE_SBOT],
            title="Palestrantes que Aceitaram mas NÃO se Inscreveram"
        )
        st.plotly_chart(fig_palestrantes, use_container_width=True)
    else:
        st.info("Tabela de relacionamento 'Aceito x Inscrito' carregada diretamente abaixo:")
        st.dataframe(df_palestrantes, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 3: INSCRIÇÕES PATROCINADAS / CONVÊNIOS
# ====================================================
st.header("3. Inscrições Patrocinadas")

df_patrocinadas = carregar_tabela(URL_PATROCINADOS)

# Lista de Exclusões Obrigatórias
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
    col_descricao = [c for c in df_patrocinadas.columns if 'descri' in c.lower() or 'convenio' in c.lower() or 'grupo' in c.lower()][0]
    
    # Aplicação do Filtro de Exclusão dos Grupos
    df_filtrado_patrocinio = df_patrocinadas[~df_patrocinadas[col_descricao].astype(str).isin(GRUPOS_EXCLUIR)]
    
    # Cálculo das Métricas de Patrocínio
    qtd_vendidas = df_filtrado_patrocinio['qtd_total'].sum() if 'qtd_total' in df_filtrado_patrocinio.columns else 0
    qtd_efetivadas = df_filtrado_patrocinio['qtd_inscrito'].sum() if 'qtd_inscrito' in df_filtrado_patrocinio.columns else 0
    qtd_nao_efetivadas = qtd_vendidas - qtd_efetivadas

    m1, m2, m3 = st.columns(3)
    m1.metric("Quantidade de Inscrições Vendidas", f"{qtd_vendidas}")
    m2.metric("Inscrições Efetivadas", f"{qtd_efetivadas}")
    m3.metric("Inscrições NÃO Efetivadas", f"{qtd_nao_efetivadas}")

    with st.expander("📄 Ver tabela de convênios/patrocinados (Já com filtros aplicados)"):
        st.dataframe(df_filtrado_patrocinio, use_container_width=True)

# ====================================================
# AGENTE IA - GOOGLE AI STUDIO (GEMINI)
# ====================================================
st.divider()
st.subheader("🤖 Diagnóstico Estratégico com Gemini API")

if GEMINI_API_KEY:
    if st.button("✨ Gerar Análise Consolidada do Congresso"):
        with st.spinner("Analisando dados do iCongresso..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            Como especialista de dados da SBOT, analise o resumo atual das 3 frentes do Congresso SBOT 2026:
            1. Congresso: {qtd_pagas} pagas, {qtd_cortesia} cortesias, {qtd_voucher} vouchers (Total: {total_geral_congresso}).
            2. Palestrantes: {aceito} convites aceitos, {pendente} pendentes, {rejeitado} rejeitados.
            3. Patrocinadores: {qtd_vendidas} vagas vendidas, {qtd_efetivadas} efetivadas e {qtd_nao_efetivadas} pendentes de preenchimento.
            
            Gere um diagnóstico curto e direto recomendando ações operacionais imediatas.
            """
            
            response = model.generate_content(prompt)
            st.markdown(response.text)
