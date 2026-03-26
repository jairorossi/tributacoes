import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Consulta Fiscal - Golden/Nucleo", layout="wide")

def carregar_dados(caminho_arquivo):
    dados = []
    try:
        with open(caminho_arquivo, 'r', encoding='iso-8859-1') as f:
            conteudo = f.read()
    except FileNotFoundError:
        return None

    # Processando linha a linha para capturar a lógica de colunas do relatório
    linhas = conteudo.split('\n')
    for linha in linhas:
        # Regex para capturar linhas de dados (Orig Dest Trib ST...)
        match = re.search(r'^\s+([A-Z]{2})\s+([A-Z]{2})\s+([A-Z0-9]{3})\s+(\d{3})', linha)
        if match:
            p = linha.split()
            if len(p) >= 16:
                try:
                    item = {
                        "Origem": p[0],
                        "Destino": p[1],
                        "Trib": p[2],
                        "ST": p[3], # Situação Tributária (Ex: 020, 000)
                        # ENTRADA
                        "Ent_Trib": p[7],
                        "Ent_Isento": p[8],
                        "Ent_Outras": p[9],
                        "Ent_Aliq": p[10],
                        "Ent_CTF": p[11],
                        # SAÍDA
                        "Sai_Trib": p[12],
                        "Sai_Isento": p[13],
                        "Sai_Outras": p[14],
                        "Sai_Aliq": p[15],
                        "Sai_CTF": p[16]
                    }
                    dados.append(item)
                except: continue
    return pd.DataFrame(dados)

st.title("📑 Consulta de Tributações por UF")
st.sidebar.header("Configurações")
empresa = st.sidebar.selectbox("Empresa", ["GOLDEN", "NUCLEO"])

arquivo_map = {"GOLDEN": "TRIBUTACOES_GOLDEN.txt", "NUCLEO": "TRIBUTACOES_NUCLEO.txt"}
df = carregar_dados(arquivo_map[empresa])

if df is not None and not df.empty:
    # Filtros
    origens = st.sidebar.multiselect("Origem", options=sorted(df['Origem'].unique()))
    destinos = st.sidebar.multiselect("Destino", options=sorted(df['Destino'].unique()))
    cod_trib = st.sidebar.multiselect("Cód. Tributação (Ex: T01)", options=sorted(df['Trib'].unique()))

    query = df.copy()
    if origens: query = query[query['Origem'].isin(origens)]
    if destinos: query = query[query['Destino'].isin(destinos)]
    if cod_trib: query = query[query['Trib'].isin(cod_trib)]

    for _, row in query.iterrows():
        # Layout inspirado no seu print original
        with st.expander(f"📍 {row['Origem']} para {row['Destino']} | Trib: {row['Trib']} | ST: {row['ST']}", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📥 Entrada")
                st.markdown(f"**Situação Tributária (ST):** `{row['ST']}`")
                st.write(f"**% Tributado:** {row['Ent_Trib']}%")
                st.write(f"**% Isento:** {row['Ent_Isento']}%")
                st.write(f"**Alíquota ICMS:** {row['Ent_Aliq']}%")
                st.write(f"**CTF:** {row['Ent_CTF']}")

            with col2:
                st.subheader("📤 Saída")
                st.markdown(f"**Situação Tributária (ST):** `{row['ST']}`")
                st.write(f"**% Tributado:** {row['Sai_Trib']}%")
                st.write(f"**% Isento:** {row['Sai_Isento']}%")
                st.write(f"**Alíquota ICMS:** {row['Sai_Aliq']}%")
                st.write(f"**CTF:** {row['Sai_CTF']}")
else:
    st.error("Arquivo não encontrado ou vazio.")
