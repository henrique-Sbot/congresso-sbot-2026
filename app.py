import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import google.generativeai as genai

# ----------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E DESIGN PREMIUM
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard Executivo SBOT 2026",
    page_icon="📊",
    layout="wide"
)

# Estilização CSS personalizada
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #F8FAFC;
        }

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

        .stat-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: 4px solid #0284C7;
            border-radius: 10px 10px 0px 0px;
            padding: 18px 12px;
            text-align: center;
        }
        .stat-card.orange { border-top-color: #EA580C; }
        .stat-card.green { border-top-color: #10B981; }
        
        .stat-value {
            font-size: 36px;
            font-weight: 800;
            color: #0F172A;
            line-height: 1;
        }
        .stat-value.blue { color: #0284C7; }
        .stat-value.orange { color: #EA580C; }
        .stat-value.green { color: #10B981; }
        
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
            padding: 16px;
            margin-bottom: 20px;
            min-height: 115px;
        }
        .info-icon { font-size: 20px; margin-bottom: 6px; }
        .info-title { font-size: 13px; font-weight: 700; color: #0F172A; margin-bottom: 4px; }
        .info-desc { font-size: 12px; color: #64748B; line-height: 1.4; }

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
# FUNÇÃO DE CARREGAMENTO E TRATAMENTO
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
        st.error(f"Erro na conexão: {e}")
    return None

URL_ATIVIDADE = "https://bit.ly/Qtd_inscritos_Atividade"
URL_PALESTRANTES = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/30501/type/quantitativo/idioma_ext/1/cc_ext/190"
URL_PATROCINADOS = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/1977/type/quantitativo/idioma_ext/1/cc_ext/190"
URL_ESTADOS = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/1802/type/quantitativo/idioma_ext/1/cc_ext/190"

st.title("📊 Dashboard Executivo - Congresso SBOT 2026")
st.caption("Acompanhamento estratégico em tempo real e projeções consolidadas")
st.divider()

# ====================================================
# SESSÃO 1: INSCRIÇÕES GERAIS (CONGRESSO)
# ====================================================
st.markdown('<div class="section-header">Sessão 1: Inscrições Gerais (Congresso)</div>', unsafe_allow_html=True)
df_atividade = carregar_dados_icongresso(URL_ATIVIDADE)

qtd_pagas, qtd_cortesia, qtd_vouchers, total_geral_congresso = 0, 0, 0, 0

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
        qtd_vouchers = extrair_val(df_congresso_only, 'voucher')
        total_geral_congresso = extrair_val(df_congresso_only, 'qtd_total')

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f'''
        <div class="stat-card"><div class="stat-value">{qtd_pagas:,}</div><div class="stat-label">Inscrições Pagas</div></div>
        <div class="info-card"><div class="info-icon">💳</div><div class="info-title">Pagamentos Efetivados</div><div class="info-desc">Congressistas com pagamento confirmado no sistema.</div></div>
    '''.replace(",", "."), unsafe_allow_html=True)

with c2:
    st.markdown(f'''
        <div class="stat-card"><div class="stat-value blue">{qtd_cortesia:,}</div><div class="stat-label">Cortesias</div></div>
        <div class="info-card"><div class="info-icon">🎁</div><div class="info-title">Isenções Diretas</div><div class="info-desc">Cortesias cedidas à diretoria e convidados institucionais.</div></div>
    '''.replace(",", "."), unsafe_allow_html=True)

with c3:
    st.markdown(f'''
        <div class="stat-card"><div class="stat-value blue">{qtd_vouchers:,}</div><div class="stat-label">Vouchers</div></div>
        <div class="info-card"><div class="info-icon">🎟️</div><div class="info-title">Códigos Utilizados</div><div class="info-desc">Inscrições ativadas por meio de cupons promocionais.</div></div>
    '''.replace(",", "."), unsafe_allow_html=True)

with c4:
    st.markdown(f'''
        <div class="stat-card orange"><div class="stat-value orange">{total_geral_congresso:,}</div><div class="stat-label">Total Geral (Congresso)</div></div>
        <div class="info-card"><div class="info-icon">📈</div><div class="info-title">Público Ativo</div><div class="info-desc">Somatório total de inscritos na atividade do congresso.</div></div>
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
    st.markdown(f'''<div class="stat-card"><div class="stat-value">{tot_palestrantes}</div><div class="stat-label">Total Convocado</div></div>''', unsafe_allow_html=True)
with p2:
    st.markdown(f'''<div class="stat-card"><div class="stat-value blue">{aceito}</div><div class="stat-label">Convites Aceitos</div></div>''', unsafe_allow_html=True)
with p3:
    st.markdown(f'''<div class="stat-card orange"><div class="stat-value orange">{pendente}</div><div class="stat-label">Convites Pendentes</div></div>''', unsafe_allow_html=True)
with p4:
    st.markdown(f'''<div class="stat-card"><div class="stat-value">{rejeitado}</div><div class="stat-label">Convites Rejeitados</div></div>''', unsafe_allow_html=True)

if df_palestrantes is not None and not df_palestrantes.empty:
    with st.expander("📄 Ver Detalhamento do Status dos Palestrantes", expanded=False):
        st.dataframe(df_palestrantes, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 3: INSCRIÇÕES PATROCINADAS (SOMA MANUAL REAL)
# ====================================================
st.markdown('<div class="section-header">Sessão 3: Inscrições Patrocinadas</div>', unsafe_allow_html=True)
df_patrocinadas = carregar_dados_icongresso(URL_PATROCINADOS)

qtd_vagas_convenio, qtd_vagas_confirmadas, qtd_vagas_preencher = 0, 0, 0
df_patroc_filtrado = pd.DataFrame()

if df_patrocinadas is not None and not df_patrocinadas.empty:
    # 1. Filtro por palavras-chave institucionais/descontos
    palavras_excluir = [
        "TEOT", "EX PRESIDENTES", "MEMBROS CEC", "REMIDOS", "PALESTRANTES", 
        "SBOTLAB", "ANUANIDADE VIA APP", "DESCONTO APLICADO", "SBOT DESCONTO ANUIDADE"
    ]
    padrao_regex = "|".join(palavras_excluir)
    
    mascara_linhas_indesejadas = df_patrocinadas.astype(str).apply(
        lambda col: col.str.contains(padrao_regex, case=False, na=False)
    ).any(axis=1)
    
    df_patroc_filtrado = df_patrocinadas[~mascara_linhas_indesejadas].copy()
    
    # 2. REMOÇÃO EXPLICITA DA ÚLTIMA LINHA (Linha de Totais da Planilha Original)
    if len(df_patroc_filtrado) > 0:
        df_patroc_filtrado = df_patroc_filtrado.iloc[:-1].copy()

    # 3. Mapeamento das colunas numéricas
    colunas = list(df_patroc_filtrado.columns)
    col_vagas = next((c for c in colunas if any(k in c for k in ['convenio', 'vagas', 'cota'])), colunas[3] if len(colunas) > 3 else None)
    col_conf = next((c for c in colunas if 'confirm' in c), colunas[4] if len(colunas) > 4 else None)
    col_preencher = next((c for c in colunas if any(k in c for k in ['preencher', 'saldo', 'restante'])), colunas[5] if len(colunas) > 5 else None)

    # 4. Cálculo próprio das linhas restantes
    if col_vagas and col_conf and col_preencher:
        qtd_vagas_convenio = int(pd.to_numeric(df_patroc_filtrado[col_vagas], errors='coerce').fillna(0).sum())
        qtd_vagas_confirmadas = int(pd.to_numeric(df_patroc_filtrado[col_conf], errors='coerce').fillna(0).sum())
        qtd_vagas_preencher = int(pd.to_numeric(df_patroc_filtrado[col_preencher], errors='coerce').fillna(0).sum())

m1, m2, m3 = st.columns(3)

with m1:
    st.markdown(f'''
        <div class="stat-card"><div class="stat-value">{qtd_vagas_convenio:,}</div><div class="stat-label">Qtd. de Vagas (Convênio)</div></div>
        <div class="info-card"><div class="info-icon">🤝</div><div class="info-title">Total da Cota Comercial</div><div class="info-desc">Volume de vagas vendidas para empresas patrocinadoras.</div></div>
    '''.replace(",", "."), unsafe_allow_html=True)

with m2:
    st.markdown(f'''
        <div class="stat-card"><div class="stat-value blue">{qtd_vagas_confirmadas:,}</div><div class="stat-label">Qtd. de Vagas (Confirmadas)</div></div>
        <div class="info-card"><div class="info-icon">👤</div><div class="info-title">Vouchers Utilizados</div><div class="info-desc">Participantes cadastrados pelas patrocinadoras.</div></div>
    '''.replace(",", "."), unsafe_allow_html=True)

with m3:
    st.markdown(f'''
        <div class="stat-card orange"><div class="stat-value orange">{qtd_vagas_preencher:,}</div><div class="stat-label">Qtd. de Vagas a Preencher</div></div>
        <div class="info-card"><div class="info-icon">🔄</div><div class="info-title">Saldo Disponível</div><div class="info-desc">Cotas vendidas pendentes de indicação de nome.</div></div>
    '''.replace(",", "."), unsafe_allow_html=True)

if not df_patroc_filtrado.empty:
    with st.expander("📄 Ver Detalhamento por Empresa Patrocinadora (Filtrado)", expanded=False):
        st.dataframe(df_patroc_filtrado, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 4: DISTRIBUIÇÃO GEOGRÁFICA POR ESTADO (UF)
# ====================================================
st.markdown('<div class="section-header">Sessão 4: Distribuição Geográfica (UF)</div>', unsafe_allow_html=True)
df_estados = carregar_dados_icongresso(URL_ESTADOS)

if df_estados is not None and not df_estados.empty:
    try:
        # Identificação inteligente das colunas
        col_uf = next((c for c in df_estados.columns if any(k in c for k in ['uf', 'estado', 'sigla'])), df_estados.columns[0])
        col_total = next((c for c in df_estados.columns if any(k in c for k in ['total', 'qtd', 'inscritos'])), df_estados.columns[-1])

        df_uf_clean = df_estados.copy()
        df_uf_clean[col_total] = pd.to_numeric(df_uf_clean[col_total], errors='coerce').fillna(0)
        
        # Filtra linhas válidas de UF (removendo totais)
        df_uf_clean = df_uf_clean[df_uf_clean[col_uf].astype(str).str.len() <= 3]
        df_uf_clean = df_uf_clean.sort_values(by=col_total, ascending=False)

        top_uf = df_uf_clean.iloc[0][col_uf] if not df_uf_clean.empty else "-"
        top_uf_qtd = int(df_uf_clean.iloc[0][col_total]) if not df_uf_clean.empty else 0
        total_uf_inscritos = int(df_uf_clean[col_total].sum())

        e1, e2 = st.columns([1, 2])

        with e1:
            st.markdown(f'''
                <div class="stat-card green"><div class="stat-value green">{top_uf} ({top_uf_qtd})</div><div class="stat-label">Maior Concentração</div></div>
                <div class="info-card"><div class="info-icon">📍</div><div class="info-title">Estado Líder</div><div class="info-desc">Unidade federativa com maior participação de congressistas até o momento.</div></div>
            ''', unsafe_allow_html=True)

            st.markdown(f'''
                <div class="stat-card"><div class="stat-value">{total_uf_inscritos:,}</div><div class="stat-label">Total Mapeado por UF</div></div>
                <div class="info-card"><div class="info-icon">🗺️</div><div class="info-title">Abrangência Nacional</div><div class="info-desc">Soma de congressistas cadastrados com UF válida no sistema.</div></div>
            '''.replace(",", "."), unsafe_allow_html=True)

        with e2:
            fig = px.bar(
                df_uf_clean.head(10),
                x=col_uf,
                y=col_total,
                text=col_total,
                labels={col_uf: "Estado (UF)", col_total: "Inscritos"},
                title="Top 10 Estados com Maior Volume de Inscritos",
                color_discrete_sequence=["#0284C7"]
            )
            fig.update_traces(textposition='outside')
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=40, b=10),
                xaxis_title="",
                yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)

        with st.expander("📄 Ver Tabela Completa por Estado (UF)", expanded=False):
            st.dataframe(df_uf_clean[[col_uf, col_total]].rename(columns={col_uf: "UF", col_total: "Inscritos"}), use_container_width=True)

    except Exception as e:
        st.warning(f"Não foi possível processar a distribuição por estados: {e}")

st.divider()

# ====================================================
# SESSÃO 5: RESUMO CONSOLIDADO
# ====================================================
st.markdown('<div class="section-header">Sessão 5: Resumo Consolidado dos Módulos</div>', unsafe_allow_html=True)

# Projeção Global = Total Geral Congresso + Palestrantes Aceitos + Vagas Patrocinadas Confirmadas
projecao_confirmados = total_geral_congresso + aceito + qtd_vagas_confirmadas

# Card Centralizado e Compacto no Centro da Tela
_, col_centro, _ = st.columns([1, 2, 1])

with col_centro:
    st.markdown(f'''
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-top: 5px solid #10B981; border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0px 4px 12px rgba(0,0,0,0.03); margin-bottom: 25px;">
            <div style="font-size: 11px; font-weight: 800; color: #10B981; text-transform: uppercase; letter-spacing: 0.8px;">🎯 MÉTRICA DE PROJEÇÃO GLOBAL</div>
            <div style="font-size: 18px; font-weight: 800; color: #0F172A; margin-top: 4px;">Projeção (Inscrições Confirmadas)</div>
            <div style="font-size: 38px; font-weight: 800; color: #10B981; margin: 8px 0;">{projecao_confirmados:,}</div>
            <div style="font-size: 11px; color: #64748B;">
                <b>Congresso:</b> {total_geral_congresso:,} | <b>Palestrantes:</b> {aceito:,} | <b>Patrocinados:</b> {qtd_vagas_confirmadas:,}
            </div>
        </div>
    '''.replace(",", "."), unsafe_allow_html=True)

# Tabela do Resumo Consolidado
resumo_data = {
    "Módulo / Área": [
        "1. Inscrições Gerais", 
        "2. Palestrantes", 
        "3. Inscrições Patrocinadas", 
        "PROJEÇÃO GLOBAL DO EVENTO"
    ],
    "Métrica Principal": [
        f"{total_geral_congresso:,} Inscritos Totais",
        f"{tot_palestrantes:,} Convocados Total",
        f"{qtd_vagas_convenio:,} Vagas Vendidas",
        f"{projecao_confirmados:,} Confirmados Gerais"
    ],
    "Status Operacional": [
        f"{qtd_pagas:,} Pagas | {qtd_cortesia:,} Cortesias | {qtd_vouchers:,} Vouchers",
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
            try:
                model = genai.GenerativeModel('gemini-2.5-flash')
                prompt = f"""
                Atue como consultor sênior de eventos médicos da SBOT. Analise este cenário do Congresso SBOT 2026:
                - Projeção de Inscrições Confirmadas: {projecao_confirmados}
                - Inscrições Gerais do Congresso: {total_geral_congresso} (Pagas: {qtd_pagas}, Cortesias: {qtd_cortesia})
                - Vagas Patrocinadas: {qtd_vagas_convenio} Vendidas ({qtd_vagas_preencher} a Preencher)
                - Palestrantes: {aceito} Aceitos de {tot_palestrantes} convocados.
                
                Gere um parecer direto com 3 pontos de ação prioritários para a diretoria aumentar as inscrições pagas e o preenchimento dos patrocínios.
                """
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro ao consultar Gemini: {e}")
else:
    st.info("💡 Insira sua API Key do Google AI Studio na barra lateral para liberar os diagnósticos da IA.")
