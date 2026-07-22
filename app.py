import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA & CSS PERSONALIZADO
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Executivo SBOT 2026",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para ocultar menus e ampliar o tamanho das fontes dos cards KPI
st.markdown("""
    <style>
        /* Ocultar elementos padrão da interface do Streamlit */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployButton {display: none;}
        div[data-testid="stDecoration"] {display: none;}
        
        /* Ajuste do fundo e cores gerais */
        .stApp {
            background-color: #0f172a;
            color: #f8fafc;
        }
        
        /* Custom Cards KPI - AUMENTADOS */
        .kpi-box {
            background-color: #1e293b;
            border-left: 5px solid #0ea5e9;
            border-radius: 10px;
            padding: 22px 18px;
            text-align: center;
            box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.3);
            margin-bottom: 12px;
        }
        .kpi-box-accent {
            background-color: #0284c7;
            border-left: 5px solid #38bdf8;
            border-radius: 10px;
            padding: 22px 18px;
            text-align: center;
            box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.3);
            margin-bottom: 12px;
        }
        .kpi-box-target {
            background-color: #0f766e;
            border-left: 5px solid #2dd4bf;
            border-radius: 10px;
            padding: 22px 18px;
            text-align: center;
            box-shadow: 0 6px 12px -2px rgba(0, 0, 0, 0.3);
            margin-bottom: 12px;
        }
        .kpi-value {
            font-size: 42px !important;
            font-weight: 900 !important;
            color: #ffffff !important;
            margin-bottom: 6px !important;
            line-height: 1.1;
        }
        .kpi-label {
            font-size: 15px !important;
            font-weight: 700 !important;
            color: #cbd5e1 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.8px !important;
        }
        .kpi-subtext {
            font-size: 13px !important;
            color: #94a3b8 !important;
            margin-top: 4px;
        }
        
        /* Aumentar métricas nativas do Streamlit */
        div[data-testid="stMetricValue"] {
            font-size: 38px !important;
            font-weight: 800 !important;
            color: #f8fafc !important;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 16px !important;
            font-weight: 700 !important;
            color: #94a3b8 !important;
        }
        
        /* Ajuste das Abas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1e293b;
            border-radius: 8px 8px 0 0;
            color: #94a3b8;
            padding: 12px 24px;
            font-size: 16px;
            font-weight: 600;
        }
        .stTabs [aria-selected="true"] {
            background-color: #0ea5e9 !important;
            color: #ffffff !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BASE DE DADOS CONSOLIDADA
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # Sessão 1: Inscrições por Atividade
    df_inscricoes = pd.DataFrame([
        {"Atividade": "Ultrassonografia Musculoesquelética", "Tipo": "CURSO", "Cortesia": 0, "Convenio": 0, "Voucher": 0, "Pago": 21, "Total": 21},
        {"Atividade": "Curso Ondas de Choque 2026", "Tipo": "CURSO", "Cortesia": 0, "Convenio": 0, "Voucher": 0, "Pago": 7, "Total": 7},
        {"Atividade": "58º Congresso Anual SBOT (Porto Alegre)", "Tipo": "ADESÃO", "Cortesia": 144, "Convenio": 27, "Voucher": 16, "Pago": 719, "Total": 906}
    ])
    
    # Sessão 2: Penetração por Estado
    df_estados = pd.DataFrame([
        {"Estado": "Rio Grande do Sul (RS)", "UF": "RS", "Membros_1978": 1120, "Inscritos_1968": 431, "Status": "Anfitrião"},
        {"Estado": "Santa Catarina (SC)", "UF": "SC", "Membros_1978": 780, "Inscritos_1968": 115, "Status": "Vizinho"},
        {"Estado": "Paraná (PR)", "UF": "PR", "Membros_1978": 940, "Inscritos_1968": 102, "Status": "Vizinho"},
        {"Estado": "São Paulo (SP)", "UF": "SP", "Membros_1978": 6850, "Inscritos_1968": 155, "Status": "Foco Comercial"},
        {"Estado": "Rio de Janeiro (RJ)", "UF": "RJ", "Membros_1978": 2100, "Inscritos_1968": 68, "Status": "Foco Comercial"},
        {"Estado": "Outros Estados (Demais UFs)", "UF": "OUTROS", "Membros_1978": 6660, "Inscritos_1968": 63, "Status": "Nacional"}
    ])
    df_estados["Conversao_%"] = (df_estados["Inscritos_1968"] / df_estados["Membros_1978"] * 100).round(1)

    # Sessão 3: Palestrantes
    df_palestrantes = pd.DataFrame([
        {"Status Convite": "Aceito", "Status Inscrição": "Inscrito no iTarget", "Quantidade": 95, "Ação": "Confirmado na Grade"},
        {"Status Convite": "Aceito", "Status Inscrição": "Não Inscrito", "Quantidade": 15, "Ação": "Disparar Lembrete"},
        {"Status Convite": "Pendente", "Status Inscrição": "Pendente", "Quantidade": 30, "Ação": "Cobrança Comissão Científica"},
        {"Status Convite": "Rejeitado", "Status Inscrição": "N/A", "Quantidade": 10, "Ação": "Substituição de Convidado"}
    ])

    # Números Globais de Referência
    meta_inscritos = 3500
    total_real = 934            # Inscrições pagas + cortesias diretas
    cotas_patrocinadas = 500    # Cotas vendidas à indústria
    total_projecao = total_real + cotas_patrocinadas # 1.434
    
    return df_inscricoes, df_estados, df_palestrantes, meta_inscritos, total_real, cotas_patrocinadas, total_projecao

df_inscricoes, df_estados, df_palestrantes, META_INSCRITOS, TOTAL_REAL, COTAS_VENDIDAS, TOTAL_PROJECAO = load_data()

# -----------------------------------------------------------------------------
# 3. CABEÇALHO DO DASHBOARD
# -----------------------------------------------------------------------------
st.title("🏥 Dashboard Executivo SBOT 2026")
st.markdown("**58º Congresso Anual SBOT — Porto Alegre** | *Painel de Gestão Comercial e Estratégica*")
st.divider()

# Sidebar de Filtros Globais
st.sidebar.header("🔍 Filtros Globais")
estado_selecionado = st.sidebar.multiselect(
    "Filtrar por Estado/Regional:",
    options=df_estados["UF"].unique(),
    default=df_estados["UF"].unique()
)

df_estados_filtrado = df_estados[df_estados["UF"].isin(estado_selecionado)]

# -----------------------------------------------------------------------------
# 4. NAVEGAÇÃO POR ABAS / PILARES
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 1. Inscrições Gerais",
    "🗺️ 2. Análise por Estado",
    "🎤 3. Gestão de Palestrantes",
    "💼 4. Patrocinados & Projeção",
    "📌 5. Resumo Consolidado dos Módulos"
])

# -----------------------------------------------------------------------------
# TAB 1: INSCRIÇÕES GERAIS
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Sessão 1: Visão Geral das Inscrições")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="kpi-box">
            <div class="kpi-value">719</div>
            <div class="kpi-label">Inscrições Pagas</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="kpi-box">
            <div class="kpi-value">144</div>
            <div class="kpi-label">Cortesias Gerais</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="kpi-box">
            <div class="kpi-value">43</div>
            <div class="kpi-label">Vouchers & Convênios</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="kpi-box-accent">
            <div class="kpi-value">934</div>
            <div class="kpi-label">Total Inscritos Diretos</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("---")
    
    col_tabela, col_grafico = st.columns([3, 2])
    with col_tabela:
        st.markdown("#### Detalhamento por Atividade (iTarget)")
        st.dataframe(df_inscricoes, use_container_width=True, hide_index=True)
    
    with col_grafico:
        st.markdown("#### Distribuição de Tipos")
        fig_pizza = px.pie(
            values=[719, 144, 27, 16],
            names=["Pago", "Cortesia", "Convenio", "Voucher"],
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_pizza.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_pizza, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: ANÁLISE POR ESTADO
# -----------------------------------------------------------------------------
with tab2:
    st.subheader("Sessão 2: Comparativo Membros SBOT vs Inscritos no Congresso")
    st.info("💡 **Fonte dos dados:** Cruzamento do Relatório 1978 (Quantitativo de Membros) com o Relatório 1968 (Inscritos do Congresso).")
    
    col_bar, col_table = st.columns([3, 2])
    
    with col_bar:
        fig_bar = px.bar(
            df_estados_filtrado,
            x="Estado",
            y=["Membros_1978", "Inscritos_1968"],
            barmode="group",
            title="Membros SBOT vs Inscritos Efetivados",
            labels={"value": "Quantidade de Médicos", "variable": "Categoria"},
            color_discrete_sequence=["#0ea5e9", "#22c55e"]
        )
        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_table:
        st.markdown("#### Taxa de Conversão Regional (%)")
        st.dataframe(
            df_estados_filtrado[["Estado", "Membros_1978", "Inscritos_1968", "Conversao_%"]],
            use_container_width=True,
            hide_index=True
        )

# -----------------------------------------------------------------------------
# TAB 3: GESTÃO DE PALESTRANTES
# -----------------------------------------------------------------------------
with tab3:
    st.subheader("Sessão 3: Status dos Convites da Comissão Científica")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total Palestrantes Cadastrados", "150")
    with c2:
        st.metric("Convites Aceitos", "110", delta="73.3% do total")
    with c3:
        st.metric("Aceitou mas NÃO Inscrito", "15", delta="-15 urgentes", delta_color="inverse")
        
    st.write("---")
    st.markdown("#### Mapeamento de Pendências de Inscrição")
    st.dataframe(df_palestrantes, use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# TAB 4: PATROCINADOS & PROJEÇÃO CONSOLIDADA
# -----------------------------------------------------------------------------
with tab4:
    st.subheader("Sessão 4: Regra de Cotas das Indústrias & Projeção Final")
    
    st.warning("⚠️ **Regra Comercial SBOT:** As 500 cotas vendidas à indústria são somadas integralmente no cálculo da meta geral de público, independentemente de estarem salvas como cadastradas no iTarget.")
    
    c_p1, c_p2, c_p3, c_p4 = st.columns(4)
    with c_p1:
        st.metric("Cotas Vendidas (Patrocínio)", "500 vagas")
    with c_p2:
        st.metric("Inscrições Efetivadas", "380 vagas")
    with c_p3:
        st.metric("Saldo a Efetivar", "120 vagas", delta="Aguardando voucher")
    with c_p4:
        st.metric("PROJEÇÃO FINAL TOTAL", "1.434 congressistas", delta="934 Diretos + 500 Patrocinados")

    st.write("---")
    
    # Gráfico de Projeção Consolidada
    fig_projecao = go.Figure(data=[
        go.Bar(name='Inscrições Diretas (Pagas/Cortesias)', x=['Projeção SBOT 2026'], y=[934], marker_color='#0ea5e9'),
        go.Bar(name='Cotas Vendidas Indústria (Patrocinados)', x=['Projeção SBOT 2026'], y=[500], marker_color='#38bdf8')
    ])
    fig_projecao.update_layout(
        barmode='stack',
        title="Composição da Projeção de Público Garantido (1.434 Congressistas)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    st.plotly_chart(fig_projecao, use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 5: RESUMO CONSOLIDADOS DOS MÓDULOS (TARGET METRIC & PROGRESS BARS)
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("Sessão 5: Resumo Consolidado dos Módulos")
    st.markdown("Visão executiva unificada das métricas ativas e acompanhamento em tempo real da **Meta Geral de 3.500 Inscritos**.")
    
    # Cálculo das Porcentagens e Lacunas
    pct_real = round((TOTAL_REAL / META_INSCRITOS) * 100, 1)
    pct_projecao = round((TOTAL_PROJECAO / META_INSCRITOS) * 100, 1)
    falta_real = META_INSCRITOS - TOTAL_REAL
    falta_projecao = META_INSCRITOS - TOTAL_PROJECAO

    # Cards KPI com fontes bem amplas
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="kpi-box-target">
            <div class="kpi-value">3.500</div>
            <div class="kpi-label">Meta de Inscritos</div>
            <div class="kpi-subtext">Objetivo do Congresso 2026</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value">{TOTAL_REAL}</div>
            <div class="kpi-label">Inscrição Real (Efetivada)</div>
            <div class="kpi-subtext">{pct_real}% da Meta Alcançada</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m3:
        st.markdown(f"""
        <div class="kpi-box-accent">
            <div class="kpi-value">{TOTAL_PROJECAO}</div>
            <div class="kpi-label">Total Projeção Sessão 5</div>
            <div class="kpi-subtext">{pct_projecao}% da Meta Alcançada</div>
        </div>
        """, unsafe_allow_html=True)
        
    with m4:
        st.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value">{falta_projecao}</div>
            <div class="kpi-label">Falta p/ Atingir a Meta</div>
            <div class="kpi-subtext">Considerando a Projeção Total</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")
    st.markdown("### 🎯 Acompanhamento das Métricas em Relação à Meta (3.500 Inscritos)")

    col_gauge1, col_gauge2 = st.columns(2)

    with col_gauge1:
        st.markdown(f"#### 1. Inscrições Efetivadas (Real) x Meta")
        fig_gauge_real = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = TOTAL_REAL,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Real: {pct_real}% da Meta", 'font': {'size': 18, 'color': '#ffffff'}},
            delta = {'reference': META_INSCRITOS, 'increasing': {'color': "#38bdf8"}, 'position': "bottom"},
            number = {'suffix': " inscritos", 'font': {'color': '#38bdf8', 'size': 28}},
            gauge = {
                'axis': {'range': [None, META_INSCRITOS], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#0284c7"},
                'bgcolor': "#1e293b",
                'borderwidth': 2,
                'bordercolor': "#334155",
                'steps': [
                    {'range': [0, TOTAL_REAL], 'color': '#0ea5e9'},
                    {'range': [TOTAL_REAL, META_INSCRITOS], 'color': '#1e293b'}
                ],
                'threshold': {
                    'line': {'color': "#2dd4bf", 'width': 4},
                    'thickness': 0.8,
                    'value': META_INSCRITOS
                }
            }
        ))
        fig_gauge_real.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=280)
        st.plotly_chart(fig_gauge_real, use_container_width=True)

    with col_gauge2:
        st.markdown(f"#### 2. Projeção Consolidada x Meta")
        fig_gauge_proj = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = TOTAL_PROJECAO,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Projeção: {pct_projecao}% da Meta", 'font': {'size': 18, 'color': '#ffffff'}},
            delta = {'reference': META_INSCRITOS, 'increasing': {'color': "#2dd4bf"}, 'position': "bottom"},
            number = {'suffix': " inscritos", 'font': {'color': '#2dd4bf', 'size': 28}},
            gauge = {
                'axis': {'range': [None, META_INSCRITOS], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#0d9488"},
                'bgcolor': "#1e293b",
                'borderwidth': 2,
                'bordercolor': "#334155",
                'steps': [
                    {'range': [0, TOTAL_PROJECAO], 'color': '#2dd4bf'},
                    {'range': [TOTAL_PROJECAO, META_INSCRITOS], 'color': '#1e293b'}
                ],
                'threshold': {
                    'line': {'color': "#2dd4bf", 'width': 4},
                    'thickness': 0.8,
                    'value': META_INSCRITOS
                }
            }
        ))
        fig_gauge_proj.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=280)
        st.plotly_chart(fig_gauge_proj, use_container_width=True)

    st.write("---")
    st.markdown("### 📊 Comparativo Horizontal de Progresso")
    
    df_progresso = pd.DataFrame([
        {"Métrica": "Inscrição Real (Efetivada)", "Inscritos": TOTAL_REAL, "Porcentagem": f"{pct_real}%", "Cor": "#0ea5e9"},
        {"Métrica": "Total Projeção (Direto + Cotas)", "Inscritos": TOTAL_PROJECAO, "Porcentagem": f"{pct_projecao}%", "Cor": "#2dd4bf"},
        {"Métrica": "META FINAL SBOT 2026", "Inscritos": META_INSCRITOS, "Porcentagem": "100%", "Cor": "#f59e0b"}
    ])

    fig_horizontal = px.bar(
        df_progresso,
        x="Inscritos",
        y="Métrica",
        orientation='h',
        text="Inscritos",
        color="Métrica",
        color_discrete_map={
            "Inscrição Real (Efetivada)": "#0ea5e9",
            "Total Projeção (Direto + Cotas)": "#2dd4bf",
            "META FINAL SBOT 2026": "#f59e0b"
        }
    )
    fig_horizontal.update_traces(textposition='outside', texttemplate='%{x} inscritos')
    fig_horizontal.update_layout(
        title="Progresso Lado a Lado em Relação ao Alvo de 3.500 Participantes",
        xaxis=dict(range=[0, 4000], title="Número de Médicos / Congressistas"),
        yaxis=dict(title=""),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        showlegend=False,
        height=320
    )
    st.plotly_chart(fig_horizontal, use_container_width=True)

    # Resumo descritivo da Sessão 5
    st.info(f"""
    📌 **Resumo de Atingimento Executivo:**
    * **Inscrição Real Efetivada:** **{TOTAL_REAL} inscritos** representam **{pct_real}%** da meta de 3.500 participantes.
    * **Projeção Consolidada (Sessão 5):** **{TOTAL_PROJECAO} congressistas** (934 diretos + 500 cotas patrocinadas) representam **{pct_projecao}%** da meta.
    * **Lacuna Atual:** Faltam **{falta_projecao} inscritos** em relação à projeção consolidada para alcançar os 3.500 almejados para o evento em Porto Alegre.
    """)
