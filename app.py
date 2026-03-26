import streamlit as st
import pandas as pd
import re

# Configuração da Página
st.set_page_config(page_title="Consulta Fiscal Golden/Nucleo", layout="wide")

def carregar_dados(caminho_arquivo):
    dados = []
    try:
        # Usamos iso-8859-1 para evitar o UnicodeDecodeError em arquivos de ERP 
        with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
            conteudo = f.read()
    except FileNotFoundError:
        return None

    # Dividir o conteúdo por linhas para processar o relatório [cite: 4]
    linhas = conteudo.split('\n')
    
    for i, linha in enumerate(linhas):
        # Procuramos linhas que começam com a UF (ex: AC, CE, DF...) [cite: 4, 8, 17]
        match = re.search(r'^\s+([A-Z]{2})\s+([A-Z]{2})\s+([A-Z0-9]{3})\s+(\d{3})', linha)
        
        if match:
            partes = linha.split()
            # O relatório tem colunas fixas: Orig, Dest, Trib, ST... [cite: 4]
            # Verificamos se a linha tem os dados mínimos de tributação
            if len(partes) >= 16:
                try:
                    item = {
                        "Origem": partes[0],
                        "Destino": partes[1],
                        "Tributação": partes[2],
                        "ST": partes[3],
                        "Ent_Tributado": partes[7],
                        "Ent_Aliq": partes[10],
                        "Ent_CTF": partes[11],
                        "Sai_Tributado": partes[12],
                        "Sai_Aliq": partes[15],
                        "Sai_CTF": partes[16]
                    }
                    dados.append(item)
                except IndexError:
                    continue
    
    return pd.DataFrame(dados)

# --- INTERFACE ---
st.title("📑 Sistema de Consulta de Tributações")
st.markdown(f"**Data de Emissão do Relatório:** 26/03/2026") # Conforme o topo do seu TXT [cite: 3]
st.markdown("---")

# Seleção de Empresa na lateral
st.sidebar.header("Configurações")
empresa = st.sidebar.selectbox("Selecione a Empresa", ["GOLDEN", "NUCLEO"])

# Nomes de arquivos exatos conforme solicitado
arquivo_map = {
    "GOLDEN": "TRIBUTACOES_GOLDEN.txt",
    "NUCLEO": "TRIBUTACOES_NUCLEO.txt"
}

df = carregar_dados(arquivo_map[empresa])

if df is not None and not df.empty:
    # Filtros Dinâmicos
    st.sidebar.subheader("Filtros de Busca")
    f_origem = st.sidebar.multiselect("UF Origem", options=sorted(df['Origem'].unique()))
    f_destino = st.sidebar.multiselect("UF Destino", options=sorted(df['Destino'].unique()))
    f_trib = st.sidebar.multiselect("Cód. Tributação", options=sorted(df['Tributação'].unique()))

    # Aplicação dos filtros
    query = df.copy()
    if f_origem: query = query[query['Origem'].isin(f_origem)]
    if f_destino: query = query[query['Destino'].isin(f_destino)]
    if f_trib: query = query[query['Tributação'].isin(f_trib)]

    # Resumo
    st.info(f"Mostrando resultados para **{empresa}** | {len(query)} registros encontrados")

    # Exibição em formato de "Cards" simulando a interface do sistema
    for _, row in query.iterrows():
        with st.container():
            # Cabeçalho do Card
            st.markdown(f"### 📍 {row['Origem']} ➔ {row['Destino']} | Trib: {row['Tributação']} (ST: {row['ST']})")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📥 SEÇÃO ENTRADA**")
                # Exibe os valores de Entrada do relatório [cite: 4, 17]
                st.code(f"Tributado: {row['Ent_Tributado']}%\nAlíquota:  {row['Ent_Aliq']}%\nCTF:       {row['Ent_CTF']}")
            
            with col2:
                st.markdown("**📤 SEÇÃO SAÍDA**")
                # Exibe os valores de Saída do relatório [cite: 4, 17, 103]
                st.code(f"Tributado: {row['Sai_Tributado']}%\nAlíquota:  {row['Sai_Aliq']}%\nCTF:       {row['Sai_CTF']}")
            
            st.markdown("---")
else:
    st.error(f"Erro: O arquivo **{arquivo_map[empresa]}** não foi encontrado ou está ilegível.")
    st.warning("Verifique se o nome do arquivo no GitHub está exatamente como: TRIBUTACOES_GOLDEN.txt")
