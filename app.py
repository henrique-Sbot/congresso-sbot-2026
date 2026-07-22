# ====================================================
# SESSÃO 3: INSCRIÇÕES PATROCINADAS (FILTRO AUTOMÁTICO)
# ====================================================
st.markdown('<div class="section-header">Sessão 3: Inscrições Patrocinadas</div>', unsafe_allow_html=True)
df_patrocinadas = carregar_dados_icongresso(URL_PATROCINADOS)

qtd_vagas_convenio, qtd_vagas_confirmadas, qtd_vagas_preencher = 0, 0, 0
df_patroc_filtrado = pd.DataFrame()

if df_patrocinadas is not None and not df_patrocinadas.empty:
    # 1. Palavras-chave que identificam as linhas que devem ser EXCLUÍDAS
    palavras_excluir = [
        "TEOT", "EX PRESIDENTES", "MEMBROS CEC", "REMIDOS", "PALESTRANTES", 
        "SBOTLAB", "ANUANIDADE VIA APP", "DESCONTO APLICADO", "SBOT DESCONTO ANUIDADE"
    ]
    
    # Criar uma expressão regular com todas as palavras-chave
    padrao_regex = "|".join(palavras_excluir)
    
    # 2. Transforma todo o conteúdo do DataFrame em texto simples para varrer todas as colunas de uma vez
    mascara_linhas_indesejadas = df_patrocinadas.astype(str).apply(
        lambda col: col.str.contains(padrao_regex, case=False, na=False)
    ).any(axis=1)
    
    # 3. Exclui definitivamente as linhas do DataFrame
    df_patroc_filtrado = df_patrocinadas[~mascara_linhas_indesejadas].copy()
    
    # 4. Mapeamento dinâmico das 3 colunas numéricas de referência
    colunas = list(df_patroc_filtrado.columns)
    
    # Busca dinamicamente pelos nomes das colunas de Vagas, Confirmadas e Saldo
    col_vagas = next((c for c in colunas if any(k in c for k in ['convenio', 'vagas', 'cota'])), colunas[3] if len(colunas) > 3 else None)
    col_conf = next((c for c in colunas if 'confirm' in c), colunas[4] if len(colunas) > 4 else None)
    col_preencher = next((c for c in colunas if any(k in c for k in ['preencher', 'saldo', 'restante'])), colunas[5] if len(colunas) > 5 else None)

    # Cálculo dos totais reais APENAS com as empresas patrocinadoras ativas
    if col_vagas and col_conf and col_preencher:
        qtd_vagas_convenio = int(pd.to_numeric(df_patroc_filtrado[col_vagas], errors='coerce').fillna(0).sum())
        qtd_vagas_confirmadas = int(pd.to_numeric(df_patroc_filtrado[col_conf], errors='coerce').fillna(0).sum())
        qtd_vagas_preencher = int(pd.to_numeric(df_patroc_filtrado[col_preencher], errors='coerce').fillna(0).sum())

# Exibição dos Cartões das 3 Colunas de Referência
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

# Tabela Limpa e Filtrada
if not df_patroc_filtrado.empty:
    with st.expander("📄 Ver Detalhamento por Empresa Patrocinadora (Filtrado)", expanded=False):
        st.dataframe(df_patroc_filtrado, use_container_width=True)
