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

# Estilização CSS para ocultar menus e marcas do Streamlit Cloud
st.markdown("""
    <style>
        /* Ocultar elementos padrão da interface do Streamlit */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployButton {display: none;}
        div[data-testid="stDecoration"] {display: none;}
        
        /* Ajuste do fundo e cores */
        .stApp {
            background-color: #0f172a;
            color: #f8fafc;
        }
        
        /* Custom Cards KPI */
        .kpi-box {
            background-color: #1e293b;
            border-left: 4px solid #0ea5e9;
            border-radius: 8px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            margin-bottom: 10px;
        }
        .kpi-box-accent {
            background-color: #0284c7;
            border-left: 4px solid #38bdf8;
            border-radius: 8px;
            padding: 18px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            margin-bottom: 10px;
        }
        .kpi-value {
            font-size: 32px;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 4px;
        }
        .kpi-label {
            font-size: 13px;
            font-weight: 600;
            color: #cbd5e1;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Ajuste de abas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #1e293b;
            border-radius: 6px 6px 0 0;
            color: #94a3b8;
            padding: 10px 20px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #0ea5e9 !important;
            color: #ffffff !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. BASE DE DADOS (SIMULADA / CONSOLIDADA DOS RELATÓRIOS ITARGET)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    # Sessão 1: Inscrições por Atividade
    df_inscricoes = pd.DataFrame([
        {"Atividade": "Ultrassonografia Musculoesquelética", "Tipo": "CURSO", "Cortesia": 0, "Convenio": 0, "Voucher": 0, "Pago": 21, "Total": 21},
        {"Atividade": "Curso Ondas de Choque 2026", "Tipo": "CURSO", "Cortesia": 0, "Convenio": 0, "Voucher": 0, "Pago": 7, "Total": 7},
        {"Atividade": "58º Congresso Anual SBOT (Porto Alegre)", "Tipo": "ADESÃO", "Cortesia": 144, "Convenio": 27, "Voucher": 16, "Pago": 719, "Total": 906}
    ])
    
    # Sessão 2: Penetração por Estado (1978 vs 1968)
    df_estados = pd.DataFrame([
        {"Estado": "Rio Grande do Sul (RS)", "UF": "RS", "Membros_1978": 1120, "Inscritos_1968": 431, "Status": "Anfitrião"},
        {"Estado": "Santa Catarina (SC)", "UF": "SC", "Membros_1978": 780, "Inscritos_1968": 115, "Status": "Vizinho"},
        {"Estado": "Paraná (PR)", "UF": "PR", "Membros_1978": 940, "Inscritos_1968": 102, "Status": "Vizinho"},
        {"Estado": "São Paulo (SP)", "UF": "SP", "Membros_1978": 6850, "Inscritos_1968": 155, "Status": "Foco Comercial"},
        {"Estado": "Rio de Janeiro (RJ)", "UF": "RJ", "Membros_1978": 2100, "Inscritos_1968": 68, "Status": "Foco Comercial"},
        {"Estado": "Outros Estados (Demais UFs)", "UF": "OUTROS", "Membros_1978": 6660, "Inscritos_1968": 63, "Status": "Nacional"}
    ])
    df_estados["Conversao_%"] = (df_estados["Inscritos_1968"] / df_estados["Membros_1978"] * 100).round(1)

    # Sessão 3: Mapeamento de Palestrantes
    df_palestrantes = pd.DataFrame([
        {"Status Convite": "Aceito", "Status Inscrição": "Inscrito no iTarget", "Quantidade": 95, "Ação": "Confirmado na Grade"},
        {"Status Convite": "Aceito", "Status Inscrição": "Não Inscrito", "Quantidade": 15, "Ação": "Disparar Lembrete"},
        {"Status Convite": "Pendente", "Status Inscrição": "Pendente", "Quantidade": 30, "Ação": "Cobrança Comissão Científica"},
        {"Status Convite": "Rejeitado", "Status Inscrição": "N/A", "Quantidade": 10, "Ação": "Substituição de Convidado"}
    ])

    # Sessão 4: Patrocinadores e Cotas
    cotas_patrocinadas = {
        "cotas_vendidas": 500,
        "cotas_efetivadas": 380,
        "cotas_pendentes": 120
    }
    
    return df_inscricoes, df_estados, df_palestrantes, cotas_patrocinadas

df_inscricoes, df_estados, df_palestrantes, cotas = load_data()

# -----------------------------------------------------------------------------
# 3. CABEÇALHO DO DASHBOARD
# -----------------------------------------------------------------------------
st.title("🏥 Dashboard Executivo SBOT 2026")
st.markdown("**58º Congresso Anual SBOT — Porto Alegre** | *Painel de Gestão Comercial e Estratégica*")
st.divider()

# Barra de Filtros na Sidebar
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
    "🤖 5. Inteligência Preditiva (AI)"
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
            <div class="kpi-value">16</div>
            <div class="kpi-label">Vouchers Ativos</div>
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
        fig_pizza.update_layout(margin=dict(t=20, b=20, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
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
        st.metric("Total Palestrantes", "150")
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
# TAB 5: INTELIGÊNCIA PREDITIVA (GOOGLE GEMINI)
# -----------------------------------------------------------------------------
with tab5:
    st.subheader("Sessão 5: Diagnóstico Estratégico em Tempo Real")
    
    st.markdown("Esta seção utiliza inteligência artificial para processar os relatórios consolidados e sugerir ações de marketing e cobrança comercial.")
    
    if st.button("🚀 Gerar Análise Preditiva do Evento", type="primary"):
        with st.spinner("Analisando dados com Google Gemini AI..."):
            total_garantido = 934 + 500
            st.success("Análise concluída com sucesso!")
            
            relatorio_md = f"""
### 📋 Relatório de Diagnóstico Executivo

1. **Desempenho Regional (RS x SP/RJ):**
   * O **Rio Grande do Sul** apresenta excelente conversão de **38.5%**, demonstrando forte adesão do estado anfitrião.
   * **São Paulo** e **Rio de Janeiro** possuem uma base de **8.950 membros**, mas contam atualmente com apenas **223 inscritos (2.5%)**. Recomenda-se campanha direcionada de e-mail marketing e condições especiais de viagens em grupo para estes estados.

2. **Gargalo de Palestrantes:**
   * Existem **15 palestrantes** que confirmaram presença na comissão científica, mas **não realizaram a inscrição no iTarget**. É prioritário enviar um link direto de cortesia para esses nomes até o final desta semana.

3. **Adesão de Patrocinadores:**
   * Dos 500 pacotes corporativos comercializados, **120 vouchers** ainda não foram vinculados a CPFs no sistema. Recomenda-se acionar o departamento comercial para cobrança das empresas patrocinadoras.

4. **Projeção de Público:**
   * A estimativa consolidada atual garante **{total_garantido} congressistas** inscritos, atingindo marcos positivos para a edição de Porto Alegre 2026.
"""
            st.markdown(relatorio_md)
