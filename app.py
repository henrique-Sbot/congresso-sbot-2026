import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai

st.set_page_config(
    page_title="Dashboard Executivo | SBOT Porto Alegre 2026",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização CSS personalizada para ocultar cabeçalho, rodapé, barra lateral e menus do Streamlit
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
        
        /* Ocultar barra superior, logo do Streamlit, menu, ícone do Git e barra lateral */
        header[data-testid="stHeader"],
        [data-testid="stHeader"],
        #MainMenu,
        footer,
        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapseButton"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Ajustar espaçamento e largura da página */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
            max-width: 98% !important;
        }

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #F8FAFC;
        }

        .header-banner {
            background: #FFFFFF;
            padding: 22px 30px;
            border-radius: 16px;
            color: #0F172A;
            margin-bottom: 25px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid #E2E8F0;
            border-left: 6px solid #006854;
        }

        .header-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 26px;
            font-weight: 800;
            color: #0F172A;
            margin: 0;
            letter-spacing: -0.5px;
        }

        .header-subtitle {
            font-size: 14px;
            color: #64748B;
            margin-top: 4px;
            font-weight: 500;
        }

        .header-badge {
            background: #E6F4F1;
            color: #006854;
            border: 1px solid rgba(0, 104, 84, 0.25);
            padding: 8px 18px;
            border-radius: 30px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            white-space: nowrap;
        }

        .section-header {
            color: #0F172A;
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 20px;
            font-weight: 700;
            margin-top: 25px;
            margin-bottom: 18px;
            display: flex;
            align-items: center;
        }

        .section-header::before {
            content: "";
            display: inline-block;
            width: 5px;
            height: 22px;
            background-color: #006854;
            margin-right: 12px;
            border-radius: 4px;
        }

        .stat-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: 4px solid #0284C7;
            border-radius: 12px;
            padding: 22px;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease;
        }

        .stat-card.accent {
            background: #0284C7;
            border-top: 4px solid #38BDF8;
        }

        .stat-card.accent .stat-value, .stat-card.accent .stat-label {
            color: #FFFFFF !important;
        }

        .stat-card.dark {
            background: #0F172A;
            border-top: 4px solid #38BDF8;
        }

        .stat-card.dark .stat-value, .stat-card.dark .stat-label {
            color: #FFFFFF !important;
        }

        .stat-value {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 34px;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.1;
        }

        .stat-label {
            font-size: 12px;
            font-weight: 600;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-top: 8px;
        }

        .info-box {
            background-color: #F0F9FF;
            border-left: 4px solid #0284C7;
            border-radius: 8px;
            padding: 16px 20px;
            margin-top: 20px;
            font-size: 14px;
            color: #0C4A6E;
        }

        .alert-box {
            background-color: #FEF2F2;
            border-left: 4px solid #EF4444;
            border-radius: 8px;
            padding: 16px 20px;
            margin-top: 20px;
            font-size: 14px;
            color: #991B1B;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
def carregar_dados_inscricoes():
    """Carrega os dados das inscrições por atividade (Relatório iTarget)"""
    dados = [
        {"Nome da Atividade": "58º Congresso Anual SBOT (Porto Alegre)", "Tipo": "ADESÃO", "Cortesia": 144, "Convenios": 27, "Voucher": 16, "Inscrito Pago": 719, "Total Geral": 906},
        {"Nome da Atividade": "Ultrassonografia Musculoesquelética", "Tipo": "CURSO", "Cortesia": 0, "Convenios": 0, "Voucher": 0, "Inscrito Pago": 21, "Total Geral": 21},
        {"Nome da Atividade": "Curso Ondas de Choque 2026", "Tipo": "CURSO", "Cortesia": 0, "Convenios": 0, "Voucher": 0, "Inscrito Pago": 7, "Total Geral": 7},
    ]
    return pd.DataFrame(dados)

@st.cache_data(ttl=300)
def carregar_dados_regionais():
    """Carrega dados dos Membros (Relatório 1978) vs. Inscritos no Congresso (Relatório 1968)"""
    dados = [
        {"Estado": "Rio Grande do Sul", "UF": "RS", "Membros_SBOT": 1120, "Inscritos_Congresso": 431, "Destaque": "Estado Anfitrião"},
        {"Estado": "Santa Catarina", "UF": "SC", "Membros_SBOT": 780, "Inscritos_Congresso": 115, "Destaque": "Regional Sul Próxima"},
        {"Estado": "Paraná", "UF": "PR", "Membros_SBOT": 940, "Inscritos_Congresso": 102, "Destaque": "Regional Sul"},
        {"Estado": "São Paulo", "UF": "SP", "Membros_SBOT": 6850, "Inscritos_Congresso": 155, "Destaque": "Maior Base Nacional"},
        {"Estado": "Rio de Janeiro", "UF": "RJ", "Membros_SBOT": 2100, "Inscritos_Congresso": 68, "Destaque": "Polo Sudeste"},
        {"Estado": "Minas Gerais", "UF": "MG", "Membros_SBOT": 1450, "Inscritos_Congresso": 42, "Destaque": "Sudeste"},
        {"Estado": "Outras UFs", "UF": "OUTROS", "Membros_SBOT": 5210, "Inscritos_Congresso": 21, "Destaque": "Demais Regiões"},
    ]
    df = pd.DataFrame(dados)
    df["Taxa_Conversao"] = (df["Inscritos_Congresso"] / df["Membros_SBOT"] * 100).round(1)
    return df

@st.cache_data(ttl=300)
def carregar_dados_palestrantes():
    """Carrega controle de palestrantes e status de convite/inscrição"""
    dados = [
        {"Palestrante": "Dr. Carlos Alberto Silva", "Especialidade": "Joelho", "UF": "RS", "Convite": "Aceito", "Status_Inscricao": "Inscrito", "Acao_Recomendada": "Confirmado na Grade"},
        {"Palestrante": "Dra. Ana Maria Oliveira", "Especialidade": "Ombro e Cotovelo", "UF": "SP", "Convite": "Aceito", "Status_Inscricao": "Pendente", "Acao_Recomendada": "Enviar Lembrete Urgente"},
        {"Palestrante": "Dr. Roberto Mendes", "Especialidade": "Quadril", "UF": "RJ", "Convite": "Aceito", "Status_Inscricao": "Pendente", "Acao_Recomendada": "Enviar Lembrete Urgente"},
        {"Palestrante": "Dr. Paulo Henrique Souza", "Especialidade": "Trauma", "UF": "PR", "Convite": "Pendente", "Status_Inscricao": "Pendente", "Acao_Recomendada": "Cobrança Ativa Comissão"},
        {"Palestrante": "Dr. Fernando Costa", "Especialidade": "Coluna", "UF": "MG", "Convite": "Rejeitado", "Status_Inscricao": "N/A", "Acao_Recomendada": "Substituir na Grade"},
    ]
    return pd.DataFrame(dados)

df_inscricoes = carregar_dados_inscricoes()
df_regionais = carregar_dados_regionais()
df_palestrantes = carregar_dados_palestrantes()

# Banner principal totalmente limpo
st.markdown("""
    <div class="header-banner">
        <div>
            <div class="header-title">58º Congresso Anual SBOT • Porto Alegre 2026</div>
            <div class="header-subtitle">Painel Executivo de Acompanhamento de Inscritos & Métricas Globais</div>
        </div>
        <div style="text-align: right;">
            <span class="header-badge">🟢 Sincronizado • iTarget</span>
        </div>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Inscrições Gerais", 
    "🗺️ Análise Regional", 
    "🎙️ Palestrantes", 
    "💼 Patrocinados & Projeção",
    "🤖 Inteligência Artificial"
])

with tab1:
    st.markdown('<div class="section-header">Sessão 1: Inscrições Gerais e Atividades</div>', unsafe_allow_html=True)
    
    total_pagos = int(df_inscricoes["Inscrito Pago"].sum())
    total_cortesias = int(df_inscricoes["Cortesia"].sum())
    total_vouchers = int(df_inscricoes["Voucher"].sum())
    total_diretos = int(df_inscricoes["Total Geral"].sum())
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total_pagos:,}</div><div class="stat-label">Inscrições Pagas</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total_cortesias:,}</div><div class="stat-label">Inscrições Cortesia</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total_vouchers:,}</div><div class="stat-label">Vouchers Emitidos</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card accent"><div class="stat-value">{total_diretos:,}</div><div class="stat-label">Total Inscritos Diretos</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([1.2, 1])
    with col_left:
        st.subheader("Detalhamento por Atividade (Relatório 1968)")
        st.dataframe(df_inscricoes, use_container_width=True, hide_index=True)
    
    with col_right:
        st.subheader("Distribuição por Tipo")
        fig_pie = px.pie(
            df_inscricoes, 
            names="Nome da Atividade", 
            values="Total Geral", 
            color_discrete_sequence=px.colors.qualitative.Bold,
            hole=0.4
        )
        fig_pie.update_layout(margin=dict(t=20, b=20, l=10, r=10), showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.markdown('<div class="section-header">Sessão 2: Comparativo Membros (1978) vs. Inscritos (1968)</div>', unsafe_allow_html=True)
    
    ufs_selecionadas = st.multiselect(
        "🎯 Filtrar UFs para Análise:",
        options=df_regionais["UF"].unique(),
        default=df_regionais["UF"].unique()
    )
    
    df_reg_filtrado = df_regionais[df_regionais["UF"].isin(ufs_selecionadas)]
    
    total_membros = int(df_reg_filtrado["Membros_SBOT"].sum())
    total_inscritos_reg = int(df_reg_filtrado["Inscritos_Congresso"].sum())
    taxa_conversao_global = round((total_inscritos_reg / total_membros * 100), 1) if total_membros > 0 else 0
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total_membros:,}</div><div class="stat-label">Base Membros SBOT</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{total_inscritos_reg:,}</div><div class="stat-label">Inscritos Selecionados</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card accent"><div class="stat-value">{taxa_conversao_global}%</div><div class="stat-label">Taxa Média Conversão</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="stat-card dark"><div class="stat-value">RS (38.5%)</div><div class="stat-label">Líder de Conversão</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader("Taxa de Conversão de Membros por Estado (%)")
    fig_bar = px.bar(
        df_reg_filtrado, 
        x="UF", 
        y="Taxa_Conversao", 
        text="Taxa_Conversao",
        color="Taxa_Conversao",
        color_continuous_scale="Blues",
        labels={"Taxa_Conversao": "Conversão (%)", "UF": "Estado"}
    )
    fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_bar.update_layout(margin=dict(t=30, b=20, l=10, r=10), showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Tabela de Penetração Regional")
    st.dataframe(
        df_reg_filtrado,
        column_config={
            "Estado": "Estado",
            "UF": "UF",
            "Membros_SBOT": st.column_config.NumberColumn("Membros SBOT", format="%d"),
            "Inscritos_Congresso": st.column_config.NumberColumn("Inscritos no Congresso", format="%d"),
            "Taxa_Conversao": st.column_config.ProgressColumn(
                "Taxa de Conversão (%)",
                format="%.1f%%",
                min_value=0,
                max_value=100
            ),
            "Destaque": "Destaque"
        },
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.markdown('<div class="section-header">Sessão 3: Monitoramento de Grade & Palestrantes Convidados</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="stat-card"><div class="stat-value">150</div><div class="stat-label">Palestrantes Cadastrados</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="stat-card accent"><div class="stat-value">110</div><div class="stat-label">Aceitaram Convite</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="stat-card" style="border-top-color: #EF4444;"><div class="stat-value" style="color: #EF4444;">15</div><div class="stat-label">Aceitou e Não Inscrito (ALERTA)</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Mapeamento Individual de Palestrantes")
    st.dataframe(df_palestrantes, use_container_width=True, hide_index=True)

    st.markdown("""
        <div class="alert-box">
            <strong>⚠️ Ação Recomendada:</strong> Disparar e-mail de cobrança automática para os 15 palestrantes que aceitaram o convite da comissão científica, mas ainda não se inscreveram no sistema iTarget.
        </div>
    """, unsafe_allow_html=True)

with tab4:
    st.markdown('<div class="section-header">Sessão 4: Regra dos Patrocinados & Projeção Geral</div>', unsafe_allow_html=True)
    
    cotas_vendidas = 500
    cotas_efetivadas = 380
    saldo_pendente = cotas_vendidas - cotas_efetivadas
    total_projecao = total_diretos + cotas_vendidas
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card dark"><div class="stat-value">{cotas_vendidas}</div><div class="stat-label">Cotas Vendidas (Garantidas)</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-value">{cotas_efetivadas}</div><div class="stat-label">Resgates Efetivados</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card" style="border-top-color: #F59E0B;"><div class="stat-value" style="color: #D97706;">{saldo_pendente}</div><div class="stat-label">Saldo Pendente de Resgate</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <div class="stat-card accent" style="padding: 35px;">
            <div class="stat-value" style="font-size: 52px;">{total_projecao:,}</div>
            <div class="stat-label" style="font-size: 16px; color: #FFFFFF;">PROJEÇÃO TOTAL CONSOLIDADA DE CONGRESSISTAS</div>
            <p style="margin-top: 12px; font-size: 14px; opacity: 0.95; color: #E0F2FE;">
                Calculado somando <strong>{total_diretos:,}</strong> inscrições diretas + <strong>{cotas_vendidas}</strong> vagas vendidas à indústria patrocinadora.
            </p>
        </div>
    """, unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section-header">Sessão 5: Análise Preditiva & IA Executiva (Google Gemini)</div>', unsafe_allow_html=True)
    
    st.write("Gere um relatório executivo em tempo real com recomendações estratégicas para a diretoria da SBOT.")
    
    gemini_key = st.text_input("🔑 API Key do Google AI Studio (Gemini)", type="password", help="Cole sua chave de API do Gemini para habilitar análises automáticas.")
    
    if st.button("🚀 Gerar Análise Executiva com IA", type="primary"):
        if not gemini_key:
            st.warning("⚠️ Insira sua API Key do Google AI Studio para liberar a geração de relatórios.")
        else:
            try:
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Você é um consultor sênior de inteligência de mercado de eventos médicos para a SBOT.
                Analise os dados atuais do Congresso SBOT Porto Alegre 2026:
                - Inscrições Diretas no iTarget: {total_diretos} (Pagas: {total_pagos}, Cortesias: {total_cortesias})
                - Projeção Consolidada com Patrocínios: {total_projecao} congressistas
                - Penetração por Estado: RS tem 38.5% de conversão (anfitrião). SP (2.3%) e RJ (3.2%) possuem baixa adesão até o momento.
                - Vagas Patrocinadas: 500 vendidas, 380 resgatadas, 120 pendentes.
                - Palestrantes: 15 palestrantes confirmados ainda não se inscreveram no sistema.
                
                Elabore um relatório executivo contendo:
                1. Diagnóstico Geral do Evento
                2. Gargalos Estratégicos Identificados
                3. Três Ações Imediatas de Marketing/Comercial recomendadas
                """
                
                with st.spinner("Conectando ao Google Gemini e gerando análise executiva..."):
                    resposta = model.generate_content(prompt)
                    st.markdown("### 📋 Relatório Executivo Gerado")
                    st.write(resposta.text)
            except Exception as e:
                st.error(f"Erro ao processar análise via Gemini: {str(e)}")

st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #94A3B8; font-size: 12px;'>Dashboard Executivo SBOT Porto Alegre 2026</p>", 
    unsafe_allow_html=True
)
