\# STREAMING_CHUNK: Importing required packages...
import streamlit as st
import pandas as pd
import requests
import io
import re
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE PÁGINA E DESIGN PREMIUM (100% LIMPO SEM BARRAS LATERAIS OU MENUS)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Congresso SBOT | Porto Alegre 2026",
    page_icon="📊",
    layout="wide"
)

# STREAMING_CHUNK: Applying custom CSS styling for high-contrast, large cards and clean header...
st.markdown("""
    <style>
        /* Ocultar barra superior, ícone do GitHub, menu e 'Manage app' */
        [data-testid="stHeader"] { display: none !important; }
        footer { display: none !important; }
        #MainMenu { display: none !important; }
        .stDeployButton { display: none !important; }
        [data-testid="stSidebar"] { display: none !important; }
        div[class*="viewerBadge"] { display: none !important; }
        
        /* Ajuste do espaçamento do topo */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 96% !important;
        }

        /* Banner de Cabeçalho */
        .main-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            padding: 24px 30px;
            border-radius: 14px;
            color: white;
            margin-bottom: 25px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
            border-left: 6px solid #0ea5e9;
        }
        .main-header h1 {
            font-size: 2.2rem !important;
            font-weight: 800 !important;
            color: #ffffff !important;
            margin: 0 !important;
            letter-spacing: -0.5px;
        }
        .main-header p {
            font-size: 1.05rem !important;
            color: #94a3b8 !important;
            margin-top: 6px !important;
            margin-bottom: 0 !important;
        }

        /* METRIC CARDS - TAMANHOS DE FONTE AUMENTADOS */
        .metric-card {
            background: #ffffff;
            padding: 22px 18px !important;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            border-top: 4px solid #0ea5e9;
            box-shadow: 0 4px 15px rgba(0,0,0,0.04);
            text-align: center;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .metric-card.accent {
            background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%);
            border-top: 4px solid #38bdf8;
            color: white !important;
        }
        .metric-card.accent h2, .metric-card.accent p, .metric-card.accent .subtext {
            color: #ffffff !important;
        }
        .metric-card.gold {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            border-top: 4px solid #f59e0b;
            color: white !important;
        }
        .metric-card.gold h2 { color: #f59e0b !important; }
        .metric-card.gold p, .metric-card.gold .subtext { color: #f1f5f9 !important; }

        /* NÚMEROS E RÓTULOS MAIORES */
        .metric-card h2 {
            font-size: 3.2rem !important; /* AUMENTADO PARA GRANDE VISIBILIDADE */
            font-weight: 800 !important;
            margin: 4px 0 8px 0 !important;
            line-height: 1.0 !important;
            color: #0f172a;
        }
        .metric-card p {
            font-size: 1.05rem !important; /* RÓTULOS MAIS NÍTIDOS */
            font-weight: 700 !important;
            color: #475569;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 0 !important;
        }
        .metric-card .subtext {
            font-size: 0.9rem !important;
            color: #64748b;
            margin-top: 6px !important;
            font-weight: 500;
        }

        /* Títulos de Seção */
        .section-title {
            font-size: 1.35rem;
            font-weight: 700;
            color: #0f172a;
            margin: 20px 0 15px 0;
            padding-left: 10px;
            border-left: 4px solid #0ea5e9;
        }
    </style>
""", unsafe_allow_html=True)

# STREAMING_CHUNK: Rendering top header banner...
st.markdown("""
    <div class="main-header">
        <h1>📊 Congresso SBOT | Porto Alegre 2026</h1>
        <p>Acompanhamento executivo em tempo real, penetração por regional, controle de palestrantes e metas consolidadas.</p>
    </div>
""", unsafe_allow_html=True)

# STREAMING_CHUNK: Loading and caching dataset functions...
@st.cache_data(ttl=300)
def carregar_dados_inscritos():
    """Simulação/Carga parametrizada do relatório iTarget 1968 (Inscrições por Atividade/Categoria)"""
    data = [
        {"Nome Atividade": "58º Congresso Anual SBOT", "Tipo Atividade": "ADESÃO", "Cortesia": 144, "Convênios": 27, "Voucher": 16, "Inscrito Pago": 719, "TOTAL GERAL": 906},
        {"Nome Atividade": "Ultrassonografia Musculoesquelética", "Tipo Atividade": "CURSO", "Cortesia": 0, "Convênios": 0, "Voucher": 0, "Inscrito Pago": 21, "TOTAL GERAL": 21},
        {"Nome Atividade": "Curso Ondas de Choque 2026", "Tipo Atividade": "CURSO", "Cortesia": 0, "Convênios": 0, "Voucher": 0, "Inscrito Pago": 7, "TOTAL GERAL": 7}
    ]
    return pd.DataFrame(data)

@st.cache_data(ttl=300)
def carregar_dados_regionais():
    """Cruzamento dos relatórios iTarget 1978 (Sócios por Estado) x 1968 (Inscritos)"""
    data = [
        {"UF": "RS", "Estado": "Rio Grande do Sul", "Membros SBOT": 1120, "Inscritos": 431, "Categoria": "Anfitrião"},
        {"UF": "SC", "Estado": "Santa Catarina", "Membros SBOT": 780, "Inscritos": 115, "Categoria": "Sul"},
        {"UF": "PR", "Estado": "Paraná", "Membros SBOT": 940, "Inscritos": 102, "Categoria": "Sul"},
        {"UF": "SP", "Estado": "São Paulo", "Membros SBOT": 6850, "Inscritos": 155, "Categoria": "Sudeste"},
        {"UF": "RJ", "Estado": "Rio de Janeiro", "Membros SBOT": 2100, "Inscritos": 68, "Categoria": "Sudeste"},
        {"UF": "MG", "Estado": "Minas Gerais", "Membros SBOT": 1450, "Inscritos": 42, "Categoria": "Sudeste"},
        {"UF": "BA", "Estado": "Bahia", "Membros SBOT": 620, "Inscritos": 18, "Categoria": "Nordeste"},
        {"UF": "PE", "Estado": "Pernambuco", "Membros SBOT": 480, "Inscritos": 12, "Categoria": "Nordeste"},
        {"UF": "DF", "Estado": "Distrito Federal", "Membros SBOT": 510, "Inscritos": 15, "Categoria": "Centro-Oeste"},
        {"UF": "GO", "Estado": "Goiás", "Membros SBOT": 490, "Inscritos": 11, "Categoria": "Centro-Oeste"},
        {"UF": "Outros", "Estado": "Outros Estados", "Membros SBOT": 3110, "Inscritos": 23, "Categoria": "Outros"}
    ]
    df = pd.DataFrame(data)
    df["Taxa Conversão (%)"] = round((df["Inscritos"] / df["Membros SBOT"]) * 100, 1)
    return df

@st.cache_data(ttl=300)
def carregar_dados_palestrantes():
    """Dados do Relatório iTarget 1982 (Comissão Científica)"""
    data = [
        {"Status Convite": "Aceito", "Status Inscrição": "Inscrito Pago", "Qtd": 95},
        {"Status Convite": "Aceito", "Status Inscrição": "Isento / Cortesia", "Qtd": 50},
        {"Status Convite": "Aceito", "Status Inscrição": "Pendente Cadastro", "Qtd": 15},
        {"Status Convite": "Pendente Resposta", "Status Inscrição": "Não Inscrito", "Qtd": 30},
        {"Status Convite": "Recusado", "Status Inscrição": "Não Inscrito", "Qtd": 10}
    ]
    return pd.DataFrame(data)

df_geral = carregar_dados_inscritos()
df_regional = carregar_dados_regionais()
df_palestrantes = carregar_dados_palestrantes()

# STREAMING_CHUNK: Setting up application main tabs...
aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "1️⃣ Inscrições Gerais",
    "2️⃣ Análise Regional",
    "3️⃣ Palestrantes",
    "4️⃣ Patrocinados",
    "5️⃣ Resumo Consolidado dos Módulos"
])

# =============================================================================
# TAB 1: INSCRIÇÕES GERAIS
# =============================================================================
with aba1:
    st.markdown('<div class="section-title">Sessão 1: Inscrições Gerais (Congresso & Cursos)</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    pagos = df_geral["Inscrito Pago"].sum()
    cortesias = df_geral["Cortesia"].sum()
    vouchers = df_geral["Voucher"].sum()
    total_direto = df_geral["TOTAL GERAL"].sum()
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <p>Inscrições Pagas</p>
                <h2>{pagos:,}</h2>
                <div class="subtext">Pagamentos confirmados</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <p>Cortesias</p>
                <h2>{cortesias:,}</h2>
                <div class="subtext">Isenções diretas</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <p>Vouchers</p>
                <h2>{vouchers:,}</h2>
                <div class="subtext">Cupons/Promocionais</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <div class="metric-card accent">
                <p>Total Inscritos Diretos</p>
                <h2>{total_direto:,}</h2>
                <div class="subtext">Adesão + Cursos Ativos</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.write("### Detalhamento por Atividade (Relatório iTarget 1968)")
    st.dataframe(df_geral, use_container_width=True, hide_index=True)
    
    st.caption("🔗 **Fonte de Dados:** Relatório iTarget 1968 - Inscrições por Atividade.")

# =============================================================================
# TAB 2: ANÁLISE REGIONAL
# =============================================================================
with aba2:
    st.markdown('<div class="section-title">Sessão 2: Análise por Estado e Conversão de Sócios</div>', unsafe_allow_html=True)
    
    # Filtro integrado na aba
    ufs_disponiveis = df_regional["UF"].tolist()
    ufs_selecionadas = st.multiselect("Filtrar por Estados (UFs):", ufs_disponiveis, default=ufs_disponiveis)
    
    df_reg_filtrado = df_regional[df_regional["UF"].isin(ufs_selecionadas)]
    
    c1, c2, c3 = st.columns(3)
    with c1:
        total_membros = df_reg_filtrado["Membros SBOT"].sum()
        st.markdown(f"""
            <div class="metric-card">
                <p>Membros SBOT Base</p>
                <h2>{total_membros:,}</h2>
                <div class="subtext">Total no filtro</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        total_insc_reg = df_reg_filtrado["Inscritos"].sum()
        st.markdown(f"""
            <div class="metric-card">
                <p>Inscritos do Filtro</p>
                <h2>{total_insc_reg:,}</h2>
                <div class="subtext">Inscrições confirmadas</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        taxa_media = round((total_insc_reg / total_membros * 100), 1) if total_membros > 0 else 0
        st.markdown(f"""
            <div class="metric-card accent">
                <p>Taxa de Penetração</p>
                <h2>{taxa_media}%</h2>
                <div class="subtext">Conversão Média de Sócios</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    col_chart, col_table = st.columns([1.2, 1])
    
    with col_chart:
        fig_bar = px.bar(
            df_reg_filtrado, 
            x="UF", 
            y="Inscritos", 
            color="Taxa Conversão (%)",
            title="Inscritos por Estado x Taxa de Conversão",
            text="Inscritos",
            color_continuous_scale="Blues"
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(height=420)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_table:
        st.write("### Tabela de Penetração")
        st.dataframe(
            df_reg_filtrado[["UF", "Estado", "Membros SBOT", "Inscritos", "Taxa Conversão (%)"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Taxa Conversão (%)": st.column_config.ProgressColumn(
                    "Taxa Conversão (%)",
                    format="%.1f%%",
                    min_value=0,
                    max_value=40,
                ),
            }
        )

    st.caption("🔗 **Fonte de Dados:** Relatório iTarget 1978 (Membros por Estado) x Relatório 1968.")

# =============================================================================
# TAB 3: GESTÃO DE PALESTRANTES
# =============================================================================
with aba3:
    st.markdown('<div class="section-title">Sessão 3: Gestão de Palestrantes & Grade Científica</div>', unsafe_allow_html=True)
    
    total_palestrantes = df_palestrantes["Qtd"].sum()
    confirmados = df_palestrantes[df_palestrantes["Status Convite"] == "Aceito"]["Qtd"].sum()
    pendentes_insc = df_palestrantes[(df_palestrantes["Status Convite"] == "Aceito") & (df_palestrantes["Status Inscrição"] == "Pendente Cadastro")]["Qtd"].sum()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <p>Palestrantes Mapeados</p>
                <h2>{total_palestrantes}</h2>
                <div class="subtext">Grade Científica</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-card">
                <p>Convites Aceitos</p>
                <h2>{confirmados}</h2>
                <div class="subtext">Docentes confirmados</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="metric-card accent">
                <p>Aceitou e Não Inscrito</p>
                <h2>{pendentes_insc}</h2>
                <div class="subtext">Alerta de Lembrete Pendente</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        fig_pie = px.pie(
            df_palestrantes, 
            names="Status Convite", 
            values="Qtd", 
            title="Distribuição do Status dos Convites",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_p2:
        st.write("### Detalhamento por Status de Inscrição")
        st.dataframe(df_palestrantes, use_container_width=True, hide_index=True)

    st.caption("🔗 **Fonte de Dados:** Relatório iTarget 1982 - Comissão Científica e Palestrantes.")

# =============================================================================
# TAB 4: PATROCINADOS & COTAS
# =============================================================================
with aba4:
    st.markdown('<div class="section-title">Sessão 4: Inscrições Patrocinadas & Cotas Vendidas</div>', unsafe_allow_html=True)
    
    cotas_vendidas = 500
    cotas_efetivadas = 380
    saldo_pendente = cotas_vendidas - cotas_efetivadas
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
            <div class="metric-card gold">
                <p>Cotas Vendidas (Indústria)</p>
                <h2>{cotas_vendidas}</h2>
                <div class="subtext">Contratadas nos Pacotes</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-card">
                <p>Vagas Já Efetivadas</p>
                <h2>{cotas_efetivadas}</h2>
                <div class="subtext">Participantes Cadastrados</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="metric-card accent">
                <p>Saldo P / Resgatar</p>
                <h2>{saldo_pendente}</h2>
                <div class="subtext">Vouchers não resgatados</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 **Regra de Negócio Aplicada:** As 500 cotas vendidas aos patrocinadores são contabilizadas na projeção consolidada, pois já foram contratadas e garantidas financeiramente.")
    st.caption("🔗 **Fonte de Dados:** Relatório iTarget 1990 - Cotas Comerciais e Vouchers de Patrocínio.")

# =============================================================================
# TAB 5: RESUMO CONSOLIDADO DOS MÓDULOS (COM META E PROGRESSO)
# =============================================================================
with aba5:
    st.markdown('<div class="section-title">Sessão 5: Resumo Consolidado dos Módulos & Meta de Inscritos</div>', unsafe_allow_html=True)
    
    # Cálculos Consolidados
    META_OFICIAL = 3500
    inscritos_reais = df_geral["TOTAL GERAL"].sum() # 934 (Congresso + Cursos)
    projecao_total = inscritos_reais + cotas_vendidas # 934 + 500 = 1434
    
    pct_real_meta = round((inscritos_reais / META_OFICIAL) * 100, 1)
    pct_proj_meta = round((projecao_total / META_OFICIAL) * 100, 1)
    
    # CARDS COM VISIBILIDADE MAXIMIZADA E META DESTACADA
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f"""
            <div class="metric-card">
                <p>Inscrições Reais</p>
                <h2>{inscritos_reais:,}</h2>
                <div class="subtext">Inscritos Cadastrados Hoje</div>
            </div>
        """, unsafe_allow_html=True)
        
    with m2:
        st.markdown(f"""
            <div class="metric-card accent">
                <p>Projeção Consolidada</p>
                <h2>{projecao_total:,}</h2>
                <div class="subtext">Reais + 500 Cotas Indústria</div>
            </div>
        """, unsafe_allow_html=True)
        
    with m3:
        st.markdown(f"""
            <div class="metric-card gold">
                <p>Meta Oficial SBOT</p>
                <h2>{META_OFICIAL:,}</h2>
                <div class="subtext">Meta de Congressistas</div>
            </div>
        """, unsafe_allow_html=True)
        
    with m4:
        st.markdown(f"""
            <div class="metric-card">
                <p>Alcance da Meta</p>
                <h2>{pct_proj_meta}%</h2>
                <div class="subtext">Baseado na Projeção Total</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # STREAMING_CHUNK: Building custom Plotly Gauge Progress indicators for Goal achievement...
    st.write("### 🎯 Atingimento da Meta Oficial (3.500 Inscritos)")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        fig_gauge_real = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = inscritos_reais,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "<b>Inscrições Efetivadas (Real) x Meta</b>", 'font': {'size': 18, 'color': "#0f172a"}},
            delta = {'reference': META_OFICIAL, 'position': "bottom", 'relative': False, 'valueformat': ",d"},
            gauge = {
                'axis': {'range': [None, META_OFICIAL], 'tickwidth': 1, 'tickcolor': "#0f172a"},
                'bar': {'color': "#0284c7"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#cbd5e1",
                'steps': [
                    {'range': [0, 1750], 'color': '#f1f5f9'},
                    {'range': [1750, 3500], 'color': '#e0f2fe'}
                ],
                'threshold': {
                    'line': {'color': "#f59e0b", 'width': 4},
                    'thickness': 0.75,
                    'value': META_OFICIAL
                }
            }
        ))
        fig_gauge_real.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge_real, use_container_width=True)
        st.markdown(f"<p style='text-align: center; font-weight: 700; color: #0284c7;'>Atingimento Atual Real: <b>{pct_real_meta}%</b> da meta</p>", unsafe_allow_html=True)

    with col_g2:
        fig_gauge_proj = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = projecao_total,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "<b>Projeção Consolidada (+ Patrocínio) x Meta</b>", 'font': {'size': 18, 'color': "#0f172a"}},
            delta = {'reference': META_OFICIAL, 'position': "bottom", 'relative': False, 'valueformat': ",d"},
            gauge = {
                'axis': {'range': [None, META_OFICIAL], 'tickwidth': 1, 'tickcolor': "#0f172a"},
                'bar': {'color': "#0ea5e9"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#cbd5e1",
                'steps': [
                    {'range': [0, 1750], 'color': '#f1f5f9'},
                    {'range': [1750, 3500], 'color': '#e0f2fe'}
                ],
                'threshold': {
                    'line': {'color': "#f59e0b", 'width': 4},
                    'thickness': 0.75,
                    'value': META_OFICIAL
                }
            }
        ))
        fig_gauge_proj.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge_proj, use_container_width=True)
        st.markdown(f"<p style='text-align: center; font-weight: 700; color: #0ea5e9;'>Atingimento Projeção Consolidada: <b>{pct_proj_meta}%</b> da meta</p>", unsafe_allow_html=True)

    st.markdown("---")
    
    # MÓDULO INTELIGÊNCIA ARTIFICIAL - GOOGLE GEMINI
    st.write("### 🧠 Módulo Preditivo & Inteligência Artificial (Google Gemini)")
    
    api_key_input = st.text_input("Cole sua Chave da API (Google AI Studio) para gerar a análise preditiva:", type="password")
    
    if st.button("🚀 Gerar Análise Preditiva e Diagnóstico da Meta"):
        if not api_key_input:
            st.warning("⚠️ Insira uma chave de API válida do Google AI Studio.")
        else:
            try:
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Você é um consultor executivo sênior de eventos médicos da SBOT.
                Analise os dados do Congresso SBOT Porto Alegre 2026:
                - Meta Final de Inscrições: {META_OFICIAL} congressistas.
                - Inscrições Reais Cadastradas: {inscritos_reais} ({pct_real_meta}% da meta).
                - Projeção Consolidada (com 500 cotas patrocinadas): {projecao_total} ({pct_proj_meta}% da meta).
                - Estado Anfitrião (RS): 431 inscritos de 1.120 membros (38.5% conversão).
                - São Paulo (SP): 155 inscritos de 6.850 membros (2.3% conversão).
                - Palestrantes: 15 palestrantes aceitaram convite mas ainda não se inscreveram.
                
                Forneça um relatório conciso em tópicos com:
                1. Avaliação do ritmo atual em relação à Meta de 3.500 inscritos.
                2. Duas ações prioritárias para alavancar a conversão de SP e RJ.
                3. Recomendação para resgate das vagas patrocinadas e palestrantes pendentes.
                """
                
                with st.spinner("Analisando dados do congresso com Google Gemini AI..."):
                    resposta = model.generate_content(prompt)
                    st.success("Diagnóstico Preditivo Concluído!")
                    st.markdown(f"
```text\n{resposta.text}\n```")
            except Exception as e:
                st.error(f"Erro ao conectar com a API do Gemini: {e}")

# STREAMING_CHUNK: Concluding script execution...
