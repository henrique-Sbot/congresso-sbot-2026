import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai

st.set_page_config(
    page_title="Dashboard Executivo | SBOT Porto Alegre 2026",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #F8FAFC;
        }

        .header-banner {
            background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
            padding: 30px 40px;
            border-radius: 16px;
            color: #FFFFFF;
            margin-bottom: 25px;
            box-shadow: 0 10px 25px rgba(15, 23, 42, 0.15);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header-title {
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 30px;
            font-weight: 800;
            color: #FFFFFF;
            margin: 0;
            letter-spacing: -0.5px;
        }

        .header-subtitle {
            font-size: 14px;
            color: #94A3B8;
            margin-top: 6px;
        }

        .header-badge {
            background: rgba(14, 165, 233, 0.2);
            color: #38BDF8;
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 8px 18px;
            border-radius: 30px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
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
            background-color: #0284C7;
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
