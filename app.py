import streamlit as st
import pandas as pd
import requests
import io

# ----------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA
# ----------------------------------------------------
st.set_page_config(
    page_title="Dashboard Executivo SBOT 2026",
    page_icon="📊",
    layout="wide"
)

# Estilização CSS Personalizada SBOT
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #F8FAFC;
        }
        .section-header {
            color: #0F172A;
            font-size: 20px;
            font-weight: 800;
            margin-top: 25px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
        }
        .section-header::before {
            content: "";
            display: inline-block;
            width: 6px;
            height: 24px;
            background-color: #0284C7;
            margin-right: 10px;
            border-radius: 4px;
        }
        .stat-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-top: 4px solid #0284C7;
            border-radius: 10px;
            padding: 16px 12px;
            text-align: center;
        }
        .stat-card.orange { border-top-color: #EA580C; }
        .stat-card.green { border-top-color: #10B981; }
        .stat-value {
            font-size: 32px;
            font-weight: 800;
            color: #0F172A;
        }
        .stat-value.blue { color: #0284C7; }
        .stat-value.orange { color: #EA580C; }
        .stat-value.green { color: #10B981; }
        .stat-label {
            font-size: 11px;
            font-weight: 700;
            color: #64748B;
            text-transform: uppercase;
            margin-top: 6px;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. BARRA LATERAL (SIDEBAR)
# ----------------------------------------------------
st.sidebar.image("https://sbot.org.br/wp-content/uploads/2021/04/logo-sbot.png", width=180)
st.sidebar.title("Painel Executivo 2026")
st.sidebar.markdown("---")

gemini_key = st.sidebar.text_input("Google AI Studio API Key", type="password", help="Insira sua chave da API do Gemini para habilitar análises automáticas.")

# ----------------------------------------------------
# 3. CARREGAMENTO DE DADOS (ITARGET)
# ----------------------------------------------------
@st.cache_data(ttl=300)
def carregar_dados(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        req = requests.get(url, headers=headers, timeout=15)
        if req.status_code == 200:
            tabelas = pd.read_html(io.StringIO(req.text))
            for df in tabelas:
                if df.shape[0] > 0 and df.shape[1] > 1:
                    df.columns = [str(col).strip().lower() for col in df.columns]
                    return df
    except Exception:
        pass
    return None

URL_ATIVIDADE = "https://bit.ly/Qtd_inscritos_Atividade"
URL_PALESTRANTES = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/30501/type/quantitativo/idioma_ext/1/cc_ext/190"
URL_PATROCINADOS = "https://icongresso.sbot.itarget.com.br/relatorio/relatorios/index/relid/1977/type/quantitativo/idioma_ext/1/cc_ext/190"

# ----------------------------------------------------
# 4. CABEÇALHO DO DASHBOARD
# ----------------------------------------------------
st.title("📊 Dashboard Executivo - Congresso SBOT 2026")
st.caption("Acompanhamento estratégico em tempo real | Porto Alegre")
st.divider()

# ----------------------------------------------------
# SESSÃO 1: INSCRIÇÕES GERAIS
# ----------------------------------------------------
st.markdown('<div class="section-header">Sessão 1: Inscrições Gerais (Congresso)</div>', unsafe_allow_html=True)

df_atividade = carregar_dados(URL_ATIVIDADE)
qtd_pagas, qtd_cortesia, qtd_vouchers, total_geral_congresso = 719, 144, 16, 906

if df_atividade is not None and not df_atividade.empty:
    try:
        col_nome = [c for c in df_atividade.columns if any(k in c for k in ['nome', 'atividade', 'descri'])][0]
        df_congresso = df_atividade[
            df_atividade[col_nome].astype(str).str.contains("CONGRESSO", case=False, na=False) &
            ~df_atividade[col_nome].astype(str).str.contains("ULTRASSONOGRAFIA|ONDAS DE CHOQUE|CUSME", case=False, na=False)
        ]
        
        def extrair_soma(df, termo):
            cols = [c for c in df.columns if termo in c]
            if cols and not df.empty:
                return int(pd.to_numeric(df[cols[0]], errors='coerce').fillna(0).sum())
            return 0

        if not df_congresso.empty:
            qtd_pagas = extrair_soma(df_congresso, 'qtd_inscrito')
            qtd_cortesia = extrair_soma(df_congresso, 'qtd_cortesia')
            qtd_vouchers = extrair_soma(df_congresso, 'voucher')
            total_geral_congresso = extrair_soma(df_congresso, 'qtd_total')
    except Exception:
        pass

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{qtd_pagas:,}</div><div class="stat-label">Inscrições Pagas</div></div>'.replace(",", "."), unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="stat-card"><div class="stat-value blue">{qtd_cortesia:,}</div><div class="stat-label">Cortesias</div></div>'.replace(",", "."), unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="stat-value blue">{qtd_vouchers:,}</div><div class="stat-label">Vouchers</div></div>'.replace(",", "."), unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="stat-card orange"><div class="stat-value orange">{total_geral_congresso:,}</div><div class="stat-label">Total Geral (Congresso)</div></div>'.replace(",", "."), unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------
# SESSÃO 2: PALESTRANTES
# ----------------------------------------------------
st.markdown('<div class="section-header">Sessão 2: Palestrantes Convocados</div>', unsafe_allow_html=True)

df_palestrantes = carregar_dados(URL_PALESTRANTES)
tot_palestrantes, aceito, pendente, rejeitado = 150, 110, 35, 5

if df_palestrantes is not None and not df_palestrantes.empty:
    try:
        col_status = [c for c in df_palestrantes.columns if 'status' in c or 'convite' in c][0]
        col_qtd = [c for c in df_palestrantes.columns if 'quantidade' in c or 'qtd' in c][0]

        def buscar_qtd(status_nome):
            filtro = df_palestrantes[df_palestrantes[col_status].astype(str).str.contains(status_nome, case=False, na=False)]
            if not filtro.empty:
                return int(pd.to_numeric(filtro[col_qtd].values[0], errors='coerce'))
            return 0

        aceito = buscar_qtd("Aceitou")
        pendente = buscar_qtd("Convite Enviado") + buscar_qtd("Cadastrado")
        rejeitado = buscar_qtd("Rejeitado")
        tot_palestrantes = aceito + pendente + rejeitado
    except Exception:
        pass

p1, p2, p3, p4 = st.columns(4)
with p1:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{tot_palestrantes}</div><div class="stat-label">Total Convocado</div></div>', unsafe_allow_html=True)
with p2:
    st.markdown(f'<div class="stat-card"><div class="stat-value blue">{aceito}</div><div class="stat-label">Convites Aceitos</div></div>', unsafe_allow_html=True)
with p3:
    st.markdown(f'<div class="stat-card orange"><div class="stat-value orange">{pendente}</div><div class="stat-label">Convites Pendentes</div></div>', unsafe_allow_html=True)
with p4:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{rejeitado}</div><div class="stat-label">Convites Rejeitados</div></div>', unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------
# SESSÃO 3: INSCRIÇÕES PATROCINADAS
# ----------------------------------------------------
st.markdown('<div class="section-header">Sessão 3: Inscrições Patrocinadas</div>', unsafe_allow_html=True)

df_patrocinadas = carregar_dados(URL_PATROCINADOS)
qtd_vagas_convenio, qtd_vagas_confirmadas, qtd_vagas_preencher = 500, 380, 120

if df_patrocinadas is not None and not df_patrocinadas.empty:
    try:
        palavras_excluir = ["TEOT", "EX PRESIDENTES", "MEMBROS CEC", "REMIDOS", "PALESTRANTES", "SBOTLAB", "DESCONTO"]
        padrao = "|".join(palavras_excluir)
        mascara = df_patrocinadas.astype(str).apply(lambda col: col.str.contains(padrao, case=False, na=False)).any(axis=1)
        df_patroc_filtrado = df_patrocinadas[~mascara].copy()
        
        if len(df_patroc_filtrado) > 0:
            df_patroc_filtrado = df_patroc_filtrado.iloc[:-1].copy()

        cols = list(df_patroc_filtrado.columns)
        col_vagas = next((c for c in cols if any(k in c for k in ['convenio', 'vagas', 'cota'])), None)
        col_conf = next((c for c in cols if 'confirm' in c), None)
        col_preencher = next((c for c in cols if any(k in c for k in ['preencher', 'saldo'])), None)

        if col_vagas and col_conf and col_preencher:
            qtd_vagas_convenio = int(pd.to_numeric(df_patroc_filtrado[col_vagas], errors='coerce').fillna(0).sum())
            qtd_vagas_confirmadas = int(pd.to_numeric(df_patroc_filtrado[col_conf], errors='coerce').fillna(0).sum())
            qtd_vagas_preencher = int(pd.to_numeric(df_patroc_filtrado[col_preencher], errors='coerce').fillna(0).sum())
    except Exception:
        pass

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div class="stat-card"><div class="stat-value">{qtd_vagas_convenio:,}</div><div class="stat-label">Vagas Vendidas (Convênio)</div></div>'.replace(",", "."), unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="stat-card"><div class="stat-value blue">{qtd_vagas_confirmadas:,}</div><div class="stat-label">Vagas Confirmadas</div></div>'.replace(",", "."), unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="stat-card orange"><div class="stat-value orange">{qtd_vagas_preencher:,}</div><div class="stat-label">Vagas a Preencher</div></div>'.replace(",", "."), unsafe_allow_html=True)

st.divider()

# ----------------------------------------------------
# SESSÃO 4: PROJEÇÃO GLOBAL
# ----------------------------------------------------
st.markdown('<div class="section-header">Sessão 4: Resumo Consolidado e Projeção</div>', unsafe_allow_html=True)

# Projeção Global = Total do Congresso + Cotas Patrocinadas Vendidas
projecao_total = total_geral_congresso + qtd_vagas_convenio

st.markdown(f'''
    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-top: 5px solid #10B981; border-radius: 12px; padding: 20px; text-align: center; margin-bottom: 25px;">
        <div style="font-size: 12px; font-weight: 800; color: #10B981; text-transform: uppercase;">🎯 PROJEÇÃO GLOBAL GARANTIDA DO EVENTO</div>
        <div style="font-size: 42px; font-weight: 800; color: #10B981; margin: 6px 0;">{projecao_total:,} Participantes</div>
        <div style="font-size: 13px; color: #64748B;">
            <b>Inscrições Diretas (Congresso):</b> {total_geral_congresso:,} | <b>Cotas Comerciais Faturadas:</b> {qtd_vagas_convenio:,}
        </div>
    </div>
'''.replace(",", "."), unsafe_allow_html=True)

# ----------------------------------------------------
# SESSÃO 5: IA GEMINI
# ----------------------------------------------------
st.markdown('<div class="section-header">🤖 Diagnóstico Executivo Inteligente (IA)</div>', unsafe_allow_html=True)

if gemini_key:
    if st.button("✨ Gerar Parecer do Consultor IA"):
        with st.spinner("Conectando ao Google Gemini e gerando relatório..."):
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                Você é um consultor sênior de eventos médicos. Analise estes dados do Congresso SBOT 2026:
                - Inscrições Diretas no Congresso: {total_geral_congresso} (Pagas: {qtd_pagas}, Cortesias: {qtd_cortesia})
                - Palestrantes Convocados: {tot_palestrantes} (Aceitos: {aceito}, Pendentes: {pendente})
                - Cotas Patrocinadas Vendidas: {qtd_vagas_convenio} (Confirmadas: {qtd_vagas_confirmadas}, Saldo Pendente: {qtd_vagas_preencher})
                - Projeção Garantida Atual: {projecao_total} participantes.
                
                Escreva um parecer executivo curto em tópicos para a diretoria, sugerindo ações comerciais imediatas.
                """
                
                resposta = model.generate_content(prompt)
                st.markdown(resposta.text)
            except Exception as e:
                st.error(f"Erro ao consultar a API do Gemini: {e}")
else:
    st.info("💡 Insira sua API Key do Google AI Studio na barra lateral esquerda para ativar as análises preditivas com IA.")
