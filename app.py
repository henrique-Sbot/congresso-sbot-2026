import streamlit as st
import pandas as pd
import requests
import io
import google.generativeai as genai

# ----------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E DESIGN ULTRA-PREMIUM
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard Executivo SBOT 2026",
    page_icon="📊",
    layout="wide"
)

# Estilização CSS personalizada para recriar o visual exato da imagem
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #F4F6F8;
        }

        /* Títulos com barra vertical na esquerda */
        .section-header {
            color: #0F172A;
            font-size: 26px;
            font-weight: 800;
            margin-top: 25px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
        .section-header::before {
            content: "";
            display: inline-block;
            width: 5px;
            height: 28px;
            background-color: #0284C7;
            margin-right: 12px;
            border-radius: 4px;
        }

        /* Card Numérico (Top) */
        .stat-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: 4px solid #0284C7;
            border-radius: 12px 12px 6px 6px;
            padding: 20px;
            text-align: center;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.02);
            margin-bottom: 12px;
        }
        .stat-card.orange {
            border-top-color: #EA580C;
        }
        .stat-value {
            font-size: 42px;
            font-weight: 800;
            color: #0F172A;
            line-height: 1;
        }
        .stat-value.blue { color: #0284C7; }
        .stat-value.orange { color: #EA580C; }
        
        .stat-label {
            font-size: 11px;
            font-weight: 700;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-top: 8px;
        }

        /* Card Info Explicativo (Bottom) */
        .info-card {
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 20px;
            height: 100%;
            box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.02);
        }
        .info-icon {
            width: 38px;
            height: 38px;
            background-color: #E0F2FE;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            margin-bottom: 12px;
        }
        .info-title {
            font-size: 17px;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 8px;
        }
        .info-desc {
            font-size: 13px;
            color: #475569;
            line-height: 1.5;
        }

        /* Oculta marca d'água padrão do streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
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

st.title("📊 Dashboard Executivo - Congresso SBOT 2026")
st.caption("Acompanhamento estratégico em tempo real das inscrições e participantes")
st.divider()

# ====================================================
# SESSÃO 1: INSCRIÇÕES GERAIS (CONGRESSO)
# ====================================================
st.markdown('<div class="section-header">Sessão 1: Inscrições Gerais (Congresso)</div>', unsafe_allow_html=True)
df_atividade = carregar_dados_icongresso(URL_ATIVIDADE)

qtd_pagas, qtd_cortesia, total_geral_congresso = 0, 0, 0

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
        qtd_cortesia = extrair_val(df_congresso_only, 'qtd_cortesia') + extrair_val(df_congresso_only, 'voucher')
        total_geral_congresso = extrair_val(df_congresso_only, 'qtd_total')

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value">{qtd_pagas:,}</div>
            <div class="stat-label">Inscrições Pagas</div>
        </div>
        <div class="info-card">
            <div class="info-icon">💳</div>
            <div class="info-title">Inscrições Confirmadas</div>
            <div class="info-desc">Volume total de congressistas com pagamento confirmado diretamente no portal do evento.</div>
        </div>
    '''.replace(",", "."), unsafe_allow_html=True)

with c2:
    st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value blue">{qtd_cortesia:,}</div>
            <div class="stat-label">Cortesias e Vouchers</div>
        </div>
        <div class="info-card">
            <div class="info-icon">🎁</div>
            <div class="info-title">Isenções Liberadas</div>
            <div class="info-desc">Cortesias concedidas e vouchers ativados para convidados especiais e diretoria.</div>
        </div>
    '''.replace(",", "."), unsafe_allow_html=True)

with c3:
    st.markdown(f'''
        <div class="stat-card orange">
            <div class="stat-value orange">{total_geral_congresso:,}</div>
            <div class="stat-label">Total Geral (Congresso)</div>
        </div>
        <div class="info-card">
            <div class="info-icon">📈</div>
            <div class="info-title">Público do Congresso</div>
            <div class="info-desc">Somatório total de médicos e inscritos cadastrados na atividade principal.</div>
        </div>
    '''.replace(",", "."), unsafe_allow_html=True)

st.divider()

# ====================================================
# SESSÃO 2: PALESTRANTES
# ====================================================
st.markdown('<div class="section-header">Sessão 2: Palestrantes</div>', unsafe_allow_html=True)
df_palestrantes = carregar_dados_icongresso(URL_PALESTRANTES)

tot_palestrantes, aceito, pendente, rejeitado = 0, 0, 0, 0

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
    tot_palestrantes = aceito + pendente + rejeitado

p1, p2, p3, p4 = st.columns(4)

with p1:
    st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value">{tot_palestrantes}</div>
            <div class="stat-label">Total Convocado</div>
        </div>
    ''', unsafe_allow_html=True)

with p2:
    st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value blue">{aceito}</div>
            <div class="stat-label">Convites Aceitos</div>
        </div>
    ''', unsafe_allow_html=True)

with p3:
    st.markdown(f'''
        <div class="stat-card orange">
            <div class="stat-value orange">{pendente}</div>
            <div class="stat-label">Convites Pendentes</div>
        </div>
    ''', unsafe_allow_html=True)

with p4:
    st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value">{rejeitado}</div>
            <div class="stat-label">Convites Rejeitados</div>
        </div>
    ''', unsafe_allow_html=True)

st.divider()

# ====================================================
# SESSÃO 3: INSCRIÇÕES PATROCINADAS
# ====================================================
st.markdown('<div class="section-header">Sessão 3: Inscrições Patrocinadas</div>', unsafe_allow_html=True)
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

qtd_vendidas, qtd_efetivadas, qtd_nao_efetivadas = 0, 0, 0

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

with m1:
    st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value">{qtd_vendidas:,}</div>
            <div class="stat-label">Cotas Vendidas</div>
        </div>
        <div class="info-card">
            <div class="info-icon">🤝</div>
            <div class="info-title">Inscrições Vendidas</div>
            <div class="info-desc">Volume total de cortesias/vouchers negociados nos pacotes de patrocínio do congresso.</div>
        </div>
    '''.replace(",", "."), unsafe_allow_html=True)

with m2:
    st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value blue">{qtd_efetivadas:,}</div>
            <div class="stat-label">Efetivadas (Cadastradas)</div>
        </div>
        <div class="info-card">
            <div class="info-icon">👤</div>
            <div class="info-title">Efetivadas</div>
            <div class="info-desc">Participantes que já utilizaram o código do patrocinador e concluíram seu cadastro.</div>
        </div>
    '''.replace(",", "."), unsafe_allow_html=True)

with m3:
    st.markdown(f'''
        <div class="stat-card orange">
            <div class="stat-value orange">{qtd_nao_efetivadas:,}</div>
            <div class="stat-label">Não Efetivadas (Saldo)</div>
        </div>
        <div class="info-card">
            <div class="info-icon">🔄</div>
            <div class="info-title">Não Efetivadas</div>
            <div class="info-desc">Vouchers pendentes de utilização. Alerta gerado para cobrar o patrocinador antes do prazo final.</div>
        </div>
    '''.replace(",", "."), unsafe_allow_html=True)

st.divider()

# ====================================================
# SESSÃO 4: RESUMO CONSOLIDADOR DOS MÓDULOS
# ====================================================
st.markdown('<div class="section-header">Sessão 4: Resumo Consolidado dos Módulos</div>', unsafe_allow_html=True)

total_participantes = total_geral_congresso + qtd_efetivadas

resumo_data = {
    "Módulo / Área": [
        "1. Inscrições Gerais", 
        "2. Palestrantes", 
        "3. Inscrições Patrocinadas", 
        "TOTAL CONSOLIDADO EVENTO"
    ],
    "Métrica Principal": [
        f"{total_geral_congresso} Inscritos Totais",
        f"{tot_palestrantes} Total Convocados",
        f"{qtd_vendidas} Vagas Vendidas",
        f"{total_participantes} Confirmados Gerais"
    ],
    "Status Operacional": [
        f"{qtd_pagas} Pagas | {qtd_cortesia} Cortesias",
        f"{aceito} Aceitos ({pendente} Pendentes)",
        f"{qtd_efetivadas} Efetivadas ({qtd_nao_efetivadas} Saldo Pendente)",
        "BASE INTEGRADA EM TEMPO REAL"
    ]
}

st.table(pd.DataFrame(resumo_data))

# ====================================================
# AGENTE IA
# ====================================================
st.divider()
st.subheader("🤖 Diagnóstico de Inteligência Executiva")

if GEMINI_API_KEY:
    if st.button("✨ Gerar Análise Estratégica"):
        with st.spinner("Analisando métricas..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Gere um diagnóstico curto e executivo para a diretoria SBOT sobre: {total_participantes} participantes confirmados e {qtd_nao_efetivadas} vagas de patrocínio pendentes."
            response = model.generate_content(prompt)
            st.markdown(response.text)

