import streamlit as st
import pandas as pd
import requests
import io
import google.generativeai as genai

# ----------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E CSS
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard Executivo SBOT 2026",
    page_icon="📊",
    layout="wide"
)

# Estilização CSS inspirada no layout corporativo de referência
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #F8FAFC;
        }

        /* Títulos de Seção com barra vertical azul */
        .section-header {
            color: #0F172A;
            font-size: 22px;
            font-weight: 800;
            margin-top: 30px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
        .section-header::before {
            content: "";
            display: inline-block;
            width: 6px;
            height: 26px;
            background-color: #0284C7;
            margin-right: 12px;
            border-radius: 4px;
        }

        /* Estilo dos Cards Numéricos (KPIs) */
        .stat-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: 4px solid #0284C7;
            border-radius: 10px 10px 0px 0px;
            padding: 18px 12px;
            text-align: center;
        }
        .stat-card.orange {
            border-top-color: #EA580C;
        }
        .stat-value {
            font-size: 38px;
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
            letter-spacing: 0.5px;
            margin-top: 8px;
        }

        /* Estilo dos Cards Informativos (Abaixo dos Números) */
        .info-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: none;
            border-radius: 0px 0px 10px 10px;
            padding: 16px;
            margin-bottom: 20px;
            min-height: 120px;
        }
        .info-icon {
            font-size: 20px;
            margin-bottom: 6px;
        }
        .info-title {
            font-size: 14px;
            font-weight: 700;
            color: #0F172A;
            margin-bottom: 4px;
        }
        .info-desc {
            font-size: 12px;
            color: #64748B;
            line-height: 1.4;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------
st.sidebar.image("https://sbot.org.br/wp-content/uploads/2021/04/logo-sbot.png", width=180)
st.sidebar.title("Painel Executivo")
GEMINI_API_KEY = st.sidebar.text_input("Google AI Studio API Key", type="password")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# ----------------------------------------------------
# LEITURA DE DADOS
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
        st.error(f"Erro na conexão com iCongresso: {e}")
    return None

URL_ATIVIDADE = "https://bit.ly/Qtd_inscritos_Atividade"
URL_PALESTRANTES = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/30501/type/quantitativo/idioma_ext/1/cc_ext/190"
URL_PATROCINADOS = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/1977/type/quantitativo/idioma_ext/1/cc_ext/190"

st.title("📊 Dashboard Executivo - Congresso SBOT 2026")
st.caption("Acompanhamento estratégico consolidado e relatórios em tempo real")
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
            <div class="info-desc">Volume total de congressistas com pagamento confirmado no sistema.</div>
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
            <div class="info-desc">Cortesias concedidas e vouchers para convidados e diretoria.</div>
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
            <div class="info-desc">Somatório total de inscritos cadastrados na atividade principal.</div>
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
        <div class="stat-card"><div class="stat-value">{tot_palestrantes}</div><div class="stat-label">Total Convocado</div></div>
    ''', unsafe_allow_html=True)
with p2:
    st.markdown(f'''
        <div class="stat-card"><div class="stat-value blue">{aceito}</div><div class="stat-label">Convites Aceitos</div></div>
    ''', unsafe_allow_html=True)
with p3:
    st.markdown(f'''
        <div class="stat-card orange"><div class="stat-value orange">{pendente}</div><div class="stat-label">Convites Pendentes</div></div>
    ''', unsafe_allow_html=True)
with p4:
    st.markdown(f'''
        <div class="stat-card"><div class="stat-value">{rejeitado}</div><div class="stat-label">Convites Rejeitados</div></div>
    ''', unsafe_allow_html=True)

st.divider()

# ====================================================
# SESSÃO 3: INSCRIÇÕES PATROCINADAS (EXCLUSÃO AUTOMÁTICA)
# ====================================================
st.markdown('<div class="section-header">Sessão 3: Inscrições Patrocinadas</div>', unsafe_allow_html=True)
df_patrocinadas = carregar_dados_icongresso(URL_PATROCINADOS)

qtd_vagas_convenio, qtd_vagas_confirmadas, qtd_vagas_preencher = 0, 0, 0
df_patroc_filtrado = pd.DataFrame()

if df_patrocinadas is not None and not df_patrocinadas.empty:
    # Palavras-chave para expurgar totalmente da contagem e da visualização
    palavras_excluir = [
        "TEOT", "EX PRESIDENTES", "MEMBROS CEC", "REMIDOS", "PALESTRANTES", 
        "SBOTLAB", "ANUANIDADE VIA APP", "DESCONTO APLICADO", "SBOT DESCONTO ANUIDADE"
    ]
    
    padrao_regex = "|".join(palavras_excluir)
    
    # Filtra varrendo todas as colunas da tabela recebida do link
    mascara_linhas_indesejadas = df_patrocinadas.astype(str).apply(
        lambda col: col.str.contains(padrao_regex, case=False, na=False)
    ).any(axis=1)
    
    df_patroc_filtrado = df_patrocinadas[~mascara_linhas_indesejadas].copy()
    
    # Identifica colunas numéricas de Vagas (Convênio), Vagas (Confirmadas) e Vagas a Preencher
    colunas = list(df_patroc_filtrado.columns)
    col_vagas = next((c for c in colunas if any(k in c for k in ['convenio', 'vagas', 'cota'])), colunas[3] if len(colunas) > 3 else None)
    col_conf = next((c for c in colunas if 'confirm' in c), colunas[4] if len(colunas) > 4 else None)
    col_preencher = next((c for c in colunas if any(k in c for k in ['preencher', 'saldo', 'restante'])), colunas[5] if len(colunas) > 5 else None)

    if col_vagas and col_conf and col_preencher:
        qtd_vagas_convenio = int(pd.to_numeric(df_patroc_filtrado[col_vagas], errors='coerce').fillna(0).sum())
        qtd_vagas_confirmadas = int(pd.to_numeric(df_patroc_filtrado[col_conf], errors='coerce').fillna(0).sum())
        qtd_vagas_preencher = int(pd.to_numeric(df_patroc_filtrado[col_preencher], errors='coerce').fillna(0).sum())

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value">{qtd_vagas_convenio:,}</div>
            <div class="stat-label">Qtd. de Vagas (Convênio)</div>
        </div>
        <div class="info-card">
            <div class="info-icon">🤝</div>
            <div class="info-title">Total da Cota Comercial</div>
            <div class="info-desc">Volume de vagas vendidas exclusivamente para Empresas Patrocinadoras.</div>
        </div>
    '''.replace(",", "."), unsafe_allow_html=True)

with m2:
    st.markdown(f'''
        <div class="stat-card">
            <div class="stat-value blue">{qtd_vagas_confirmadas:,}</div>
            <div class="stat-label">Qtd. de Vagas (Confirmadas)</div>
        </div>
        <div class="info-card">
            <div class="info-icon">👤</div>
            <div class="info-title">Vouchers Utilizados</div>
            <div class="info-desc">Inscrições com cadastro efetivado pelos patrocinadores.</div>
        </div>
    '''.replace(",", "."), unsafe_allow_html=True)

with m3:
    st.markdown(f'''
        <div class="stat-card orange">
            <div class="stat-value orange">{qtd_vagas_preencher:,}</div>
            <div class="stat-label">Qtd. de Vagas a Preencher</div>
        </div>
        <div class="info-card">
            <div class="info-icon">🔄</div>
            <div class="info-title">Saldo Disponível</div>
            <div class="info-desc">Vouchers comercializados pendentes de indicação de nomes pelas empresas.</div>
        </div>
    '''.replace(",", "."), unsafe_allow_html=True)

if not df_patroc_filtrado.empty:
    with st.expander("📄 Ver Detalhamento por Empresa Patrocinadora (Filtrado)", expanded=False):
        st.dataframe(df_patroc_filtrado, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 4: RESUMO CONSOLIDADO
# ====================================================
st.markdown('<div class="section-header">Sessão 4: Resumo Consolidado dos Módulos</div>', unsafe_allow_html=True)

total_participantes = total_geral_congresso + qtd_vagas_confirmadas

resumo_data = {
    "Módulo / Área": [
        "1. Inscrições Gerais", 
        "2. Palestrantes", 
        "3. Inscrições Patrocinadas", 
        "TOTAL CONSOLIDADO EVENTO"
    ],
    "Métrica Principal": [
        f"{total_geral_congresso:,} Inscritos Totais",
        f"{tot_palestrantes:,} Convocados",
        f"{qtd_vagas_convenio:,} Vagas Vendidas",
        f"{total_participantes:,} Confirmados Gerais"
    ],
    "Status Operacional": [
        f"{qtd_pagas:,} Pagas | {qtd_cortesia:,} Cortesias",
        f"{aceito:,} Aceitos ({pendente:,} Pendentes)",
        f"{qtd_vagas_confirmadas:,} Confirmadas ({qtd_vagas_preencher:,} a Preencher)",
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
        with st.spinner("Analisando métricas do evento..."):
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"Gere um diagnóstico curto e executivo para a diretoria SBOT sobre: {total_participantes} participantes confirmados e {qtd_vagas_preencher} vagas de patrocínio a preencher."
            response = model.generate_content(prompt)
            st.markdown(response.text)
else:
    st.info("💡 Insira sua API Key do Google AI Studio na barra lateral para liberar os diagnósticos da IA.")
