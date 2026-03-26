import streamlit as st
import pandas as pd
import re

# Configuração da Página
st.set_page_config(page_title="Consulta Fiscal Golden/Nucleo", layout="wide")

def carregar_dados(caminho_arquivo):
    dados = []
    try:
        with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
            conteudo = f.read()
    except FileNotFoundError:
        return None

    linhas = conteudo.split('\n')
    for linha in linhas:
        # Regex para capturar a linha de dados principal
        match = re.search(r'^\s+([A-Z]{2})\s+([A-Z]{2})\s+([A-Z0-9]{3})\s+(\d{3})', linha)
        if match:
            p = linha.split()
            if len(p) >= 16:
                try:
                    # Criamos o dicionário com os dados exatos do relatório
                    item = {
                        "Origem": p[0],
                        "Destino": p[1],
                        "Trib": p[2],
                        "ST": p[3],
                        "Ent_Trib": p[7],
                        "Ent_Isento": p[8],
                        "Ent_Aliq": p[10],
                        "Ent_CTF": p[11],
                        "Sai_Trib": p[12],
                        "Sai_Isento": p[13],
                        "Sai_Aliq": p[15],
                        "Sai_CTF": p[16]
                    }
                    dados.append(item)
                except: continue
    return pd.DataFrame(dados)

# --- INTERFACE ---
st.title("📑 Sistema de Consulta Fiscal Avançado")
st.sidebar.header("Configurações Gerais")

empresa = st.sidebar.selectbox("Empresa", ["GOLDEN", "NUCLEO"])
arquivo_map = {"GOLDEN": "TRIBUTACOES_GOLDEN.txt", "NUCLEO": "TRIBUTACOES_NUCLEO.txt"}

df = carregar_dados(arquivo_map[empresa])

if df is not None and not df.empty:
    # --- BARRA LATERAL COM FILTROS AVANÇADOS ---
    st.sidebar.header("Filtros de Busca")
    
    # Filtros de Localização e Tipo
    f_origem = st.sidebar.multiselect("UF Origem", options=sorted(df['Origem'].unique()))
    f_destino = st.sidebar.multiselect("UF Destino", options=sorted(df['Destino'].unique()))
    f_trib = st.sidebar.multiselect("Cód. Tributação", options=sorted(df['Trib'].unique()))
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Filtros de Valores (Saída)")
    
    # Filtro por Situação Tributária (ST)
    f_st = st.sidebar.multiselect("Situação Tributária (ST)", options=sorted(df['ST'].unique()))
    
    # Filtro por Alíquota (Formatado para facilitar)
    f_aliq = st.sidebar.multiselect("Alíquota ICMS (%)", options=sorted(df['Sai_Aliq'].unique()))
    
    # Filtro por CTF
    f_ctf = st.sidebar.multiselect("Código CTF", options=sorted(df['Sai_CTF'].unique()))

    # --- APLICAÇÃO DOS FILTROS ---
    query = df.copy()
    if f_origem: query = query[query['Origem'].isin(f_origem)]
    if f_destino: query = query[query['Destino'].isin(f_destino)]
    if f_trib: query = query[query['Trib'].isin(f_trib)]
    if f_st: query = query[query['ST'].isin(f_st)]
    if f_aliq: query = query[query['Sai_Aliq'].isin(f_aliq)]
    if f_ctf: query = query[query['Sai_CTF'].isin(f_ctf)]

    # --- EXIBIÇÃO ---
    st.info(f"Resultados para **{empresa}** | {len(query)} registros encontrados")

    if query.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
    else:
        for _, row in query.iterrows():
            with st.expander(f"📍 {row['Origem']} ➔ {row['Destino']} | Trib: {row['Trib']} | ST: {row['ST']}", expanded=True):
                c1, c2 = st.columns(2)
                
                with c1:
                    st.markdown("**📥 ENTRADA**")
                    st.write(f"**ST:** {row['ST']}")
                    st.write(f"**Tributado:** {row['Ent_Trib']}%")
                    st.write(f"**Isento:** {row['Ent_Isento']}%")
                    st.write(f"**Alíquota:** {row['Ent_Aliq']}%")
                    st.write(f"**CTF:** {row['Ent_CTF']}")
                
                with c2:
                    st.markdown("**📤 SAÍDA**")
                    st.write(f"**ST:** {row['ST']}")
                    st.write(f"**Tributado:** {row['Sai_Trib']}%")
                    st.write(f"**Isento:** {row['Sai_Isento']}%")
                    st.write(f"**Alíquota:** {row['Sai_Aliq']}%")
                    st.write(f"**CTF:** {row['Sai_CTF']}")
else:
    st.error("Arquivo não encontrado. Verifique o nome no GitHub.")
