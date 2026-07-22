import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai

# ----------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E DESIGN PREMIUM
# ----------------------------------------------------
st.set_page_config(
    page_title="Congresso SBOT | Porto Alegre 2026",
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
# FUNÇÕES AUXILIARES DE CARREGAMENTO E MAPEAMENTO
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

MAPA_ESTADOS = {
    'ACRE': 'AC', 'ALAGOAS': 'AL', 'AMAPA': 'AP', 'AMAZONAS': 'AM', 'BAHIA': 'BA',
    'CEARA': 'CE', 'DISTRITO FEDERAL': 'DF', 'ESPIRITO SANTO': 'ES', 'GOIAS': 'GO',
    'MARANHAO': 'MA', 'MATO GROSSO': 'MT', 'MATO GROSSO DO SUL': 'MS', 'MINAS GERAIS': 'MG',
    'PARA': 'PA', 'PARAIBA': 'PB', 'PARANA': 'PR', 'PERNAMBUCO': 'PE', 'PIAUI': 'PI',
    'RIO DE JANEIRO': 'RJ', 'RIO GRANDE DO NORTE': 'RN', 'RIO GRANDE DO SUL': 'RS',
    'RONDONIA': 'RO', 'RORAIMA': 'RR', 'SANTA CATARINA': 'SC', 'SAO PAULO': 'SP',
    'SERGIPE': 'SE', 'TOCANTINS': 'TO'
}

def normalizar_uf(texto):
    txt = str(texto).strip().upper()
    if len(txt) == 2:
        return txt
    for nome, sigla in MAPA_ESTADOS.items():
        if nome in txt:
            return sigla
    return None

# URLs do Sistema
URL_ATIVIDADE = "https://bit.ly/Qtd_inscritos_Atividade"
URL_PALESTRANTES = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/30501/type/quantitativo/idioma_ext/1/cc_ext/190"
URL_PATROCINADOS = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/1977/type/quantitativo/idioma_ext/1/cc_ext/190"
URL_MEMBROS_ESTADO = "https://icase.sbot.itarget.com.br/relatorio/relatorios/index/relid/1979/type/quantitativo/idioma_ext/1/cc_ext/1"
URL_INSCRITOS_ESTADO = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/1968/type/quantitativo/idioma_ext/1/cc_ext/190"

st.title("📊 Congresso SBOT | Porto Alegre 2026")
st.caption("Acompanhamento estratégico em tempo real, penetração por regional e projeções consolidadas")
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
# SESSÃO 3: INSCRIÇÕES PATROCINADAS
# ====================================================
st.markdown('<div class="section-header">Sessão 3: Inscrições Patrocinadas</div>', unsafe_allow_html=True)
df_patrocinadas = carregar_dados_icongresso(URL_PATROCINADOS)

qtd_vagas_convenio, qtd_vagas_confirmadas, qtd_vagas_preencher = 0, 0, 0
df_patroc_filtrado = pd.DataFrame()

if df_patrocinadas is not None and not df_patrocinadas.empty:
    palavras_excluir = [
        "TEOT", "EX PRESIDENTES", "MEMBROS CEC", "REMIDOS", "PALESTRANTES", 
        "SBOTLAB", "ANUANIDADE VIA APP", "DESCONTO APLICADO", "SBOT DESCONTO ANUIDADE"
    ]
    padrao_regex = "|".join(palavras_excluir)
    
    mascara_linhas_indesejadas = df_patrocinadas.astype(str).apply(
        lambda col: col.str.contains(padrao_regex, case=False, na=False)
    ).any(axis=1)
    
    df_patroc_filtrado = df_patrocinadas[~mascara_linhas_indesejadas].copy()
    
    if len(df_patroc_filtrado) > 0:
        df_patroc_filtrado = df_patroc_filtrado.iloc[:-1].copy()

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
        <div class="stat-card"><div class="stat-value">{qtd_vagas_convenio:,}</div><div class="stat-label">Qtd. de Vagas (Convênio Vendido)</div></div>
        <div class="info-card"><div class="info-icon">🤝</div><div class="info-title">Total da Cota Comercial</div><div class="info-desc">Volume total de vagas comercializadas para patrocinadores.</div></div>
    '''.replace(",", "."), unsafe_allow_html=True)

with m2:
    st.markdown(f'''
        <div class="stat-card"><div class="stat-value blue">{qtd_vagas_confirmadas:,}</div><div class="stat-label">Qtd. de Vagas (Confirmadas)</div></div>
        <div class="info-card"><div class="info-icon">👤</div><div class="info-title">Vouchers Utilizados</div><div class="info-desc">Participantes já cadastrados nos cupons das patrocinadoras.</div></div>
    '''.replace(",", "."), unsafe_allow_html=True)

with m3:
    st.markdown(f'''
        <div class="stat-card orange"><div class="stat-value orange">{qtd_vagas_preencher:,}</div><div class="stat-label">Qtd. de Vagas a Preencher</div></div>
        <div class="info-card"><div class="info-icon">🔄</div><div class="info-title">Saldo Pendente</div><div class="info-desc">Vagas vendidas que ainda aguardam a indicação do congressista.</div></div>
    '''.replace(",", "."), unsafe_allow_html=True)

if not df_patroc_filtrado.empty:
    with st.expander("📄 Ver Detalhamento por Empresa Patrocinadora (Filtrado)", expanded=False):
        st.dataframe(df_patroc_filtrado, use_container_width=True)

st.divider()

# ====================================================
# SESSÃO 4: ANÁLISE POR ESTADO (MEMBROS X INSCRITOS)
# ====================================================
st.markdown('<div class="section-header">Sessão 4: Análise por Estado (Regional SBOT x Inscritos)</div>', unsafe_allow_html=True)

df_membros_raw = carregar_dados_icongresso(URL_MEMBROS_ESTADO)
df_inscritos_raw = carregar_dados_icongresso(URL_INSCRITOS_ESTADO)

ESTADOS_DESTAQUE = ["RS", "SC", "PR", "SP", "RJ"]

if df_membros_raw is not None and df_inscritos_raw is not None:
    try:
        # Tratamento Membros Totais (iCase)
        col_uf_m = df_membros_raw.columns[0]
        col_qtd_m = df_membros_raw.columns[-1]

        df_m = df_membros_raw[[col_uf_m, col_qtd_m]].copy()
        df_m.columns = ['UF_Raw', 'Membros']
        df_m['UF'] = df_m['UF_Raw'].apply(normalizar_uf)
        df_m['Membros'] = pd.to_numeric(df_m['Membros'], errors='coerce').fillna(0)
        df_m = df_m.dropna(subset=['UF']).groupby('UF')['Membros'].sum().reset_index()

        # Tratamento Inscritos Congresso (iCongresso)
        col_uf_i = df_inscritos_raw.columns[0]
        col_qtd_i = df_inscritos_raw.columns[-1]

        df_i = df_inscritos_raw[[col_uf_i, col_qtd_i]].copy()
        df_i.columns = ['UF_Raw', 'Inscritos']
        df_i['UF'] = df_i['UF_Raw'].apply(normalizar_uf)
        df_i['Inscritos'] = pd.to_numeric(df_i['Inscritos'], errors='coerce').fillna(0)
        df_i = df_i.dropna(subset=['UF']).groupby('UF')['Inscritos'].sum().reset_index()

        # Merge dos Dados
        df_geo = pd.merge(df_m, df_i, on='UF', how='outer').fillna(0)
        
        # Cálculo de Penetração
        df_geo['Penetracao'] = (df_geo['Inscritos'] / df_geo['Membros'] * 100).round(1)
        df_geo['Penetracao'] = df_geo['Penetracao'].replace([float('inf'), float('-inf')], 0).fillna(0)

        # Filtro de Destaques
        df_destaque = df_geo[df_geo['UF'].isin(ESTADOS_DESTAQUE)].copy()
        df_destaque = df_destaque.sort_values(by='Inscritos', ascending=False)

        # Cards dos Destaques Re-inseridos
        st.markdown("##### 📍 Destaque Regionais Estratégicas (RS, SC, PR, SP, RJ)")
        cols_dest = st.columns(len(ESTADOS_DESTAQUE))
        for idx, row in enumerate(df_destaque.itertuples()):
            with cols_dest[idx]:
                st.markdown(f'''
                    <div class="stat-card purple">
                        <div class="stat-value purple">{row.UF}</div>
                        <div class="stat-label">{int(row.Inscritos):,} Inscritos</div>
                        <div style="font-size: 11px; color: #64748B; margin-top: 4px;">
                            Base: {int(row.Membros):,} | <b>{row.Penetracao}%</b> da regional
                        </div>
                    </div>
                '''.replace(",", "."), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Gráficos Comparativos
        g1, g2 = st.columns(2)

        with g1:
            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(
                x=df_destaque['UF'], y=df_destaque['Membros'], name='Membros da Regional (iCase)', marker_color='#94A3B8'
            ))
            fig_comp.add_trace(go.Bar(
                x=df_destaque['UF'], y=df_destaque['Inscritos'], name='Inscritos no Congresso', marker_color='#0284C7'
            ))
            fig_comp.update_layout(
                title="Comparativo: Total de Membros x Inscritos (Top Regionais)",
                barmode='group',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=40, b=10)
            )
            st.plotly_chart(fig_comp, use_container_width=True)

        with g2:
            fig_pen = px.bar(
                df_geo.sort_values(by='Penetracao', ascending=False).head(12),
                x='UF',
                y='Penetracao',
                text='Penetracao',
                title="Top 12 Taxa de Penetração por Estado (% Membros Inscritos)",
                color_discrete_sequence=['#10B981']
            )
            fig_pen.update_traces(texttemplate='%{text}%', textposition='outside')
            fig_pen.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis_title="% de Penetração"
            )
            st.plotly_chart(fig_pen, use_container_width=True)

        # Tabela Visível Diretamente sem Expander
        st.markdown("##### 📄 Comparativo Detalhado por Estado")
        st.dataframe(
            df_geo.sort_values(by='Inscritos', ascending=False).rename(
                columns={
                    'UF': 'Estado/UF', 
                    'Membros': 'Membros Totais (iCase)', 
                    'Inscritos': 'Inscritos Congresso (iCongresso)', 
                    'Penetracao': '% Penetração'
                }
            ),
            use_container_width=True
        )

    except Exception as e:
        st.error(f"Erro ao calcular a análise por estado: {e}")

st.divider()

# ====================================================
# SESSÃO 5: RESUMO CONSOLIDADO
# ====================================================
st.markdown('<div class="section-header">Sessão 5: Resumo Consolidado dos Módulos</div>', unsafe_allow_html=True)

# REGRA DE CONTAGEM SOLICITADA: Total Membros Inscritos + Palestrantes Aceitos + Vagas Patrocinadas Cadastradas
projecao_confirmados_global = total_geral_congresso + aceito + qtd_vagas_confirmadas

# Card Centralizado e Highlighted no Centro da Tela
_, col_centro, _ = st.columns([1, 2, 1])

with col_centro:
    st.markdown(f'''
        <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-top: 5px solid #10B981; border-radius: 12px; padding: 22px; text-align: center; box-shadow: 0px 4px 12px rgba(0,0,0,0.03); margin-bottom: 25px;">
            <div style="font-size: 11px; font-weight: 800; color: #10B981; text-transform: uppercase; letter-spacing: 0.8px;">🎯 CONTAGEM FINAL DE CONFIRMADOS</div>
            <div style="font-size: 18px; font-weight: 800; color: #0F172A; margin-top: 4px;">Inscritos + Palestrantes Aceitos + Patrocinados Cadastrados</div>
            <div style="font-size: 42px; font-weight: 800; color: #10B981; margin: 8px 0;">{projecao_confirmados_global:,}</div>
            <div style="font-size: 12px; color: #64748B;">
                <b>Inscritos Gerais:</b> {total_geral_congresso:,} | <b>Palestrantes Aceitos:</b> {aceito:,} | <b>Patrocinados Cadastrados:</b> {qtd_vagas_confirmadas:,}
            </div>
        </div>
    '''.replace(",", "."), unsafe_allow_html=True)

# Tabela do Resumo Consolidado
resumo_data = {
    "Módulo / Área": [
        "1. Inscrições Gerais", 
        "2. Palestrantes Convocados", 
        "3. Inscrições Patrocinadas", 
        "CONTAGEM FINAL CONSOLIDADA"
    ],
    "Métrica Principal": [
        f"{total_geral_congresso:,} Inscritos Totais",
        f"{aceito:,} Palestrantes Aceitos",
        f"{qtd_vagas_confirmadas:,} Patrocinados Cadastrados",
        f"{projecao_confirmados_global:,} Público Final Confirmado"
    ],
    "Status Operacional": [
        f"{qtd_pagas:,} Pagas | {qtd_cortesia:,} Cortesias | {qtd_vouchers:,} Vouchers",
        f"{tot_palestrantes:,} Convocados ({pendente:,} Pendentes / {rejeitado:,} Rejeitados)",
        f"{qtd_vagas_convenio:,} Total Vagas Vendidas ({qtd_vagas_preencher:,} Pendentes)",
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
                Atue como consultor sênior do Congresso SBOT Porto Alegre 2026. Analise:
                - Contagem Final Consolidada: {projecao_confirmados_global} participantes.
                - Inscritos diretos no Congresso: {total_geral_congresso} (Pagas: {qtd_pagas}).
                - Palestrantes Aceitos: {aceito} de {tot_palestrantes}.
                - Patrocinados Cadastrados: {qtd_vagas_confirmadas} de {qtd_vagas_convenio} vagas vendidas (Pendente: {qtd_vagas_preencher}).
                
                Forneça 3 estratégias de engajamento para alavancar a penetração nas regionais do RS, SC e PR.
                """
                response = model.generate_content(prompt)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Erro ao consultar Gemini: {e}")
else:
    st.info("💡 Insira sua API Key do Google AI Studio na barra lateral para liberar os diagnósticos da IA.")
