import streamlit as st
import pandas as pd
import re

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
        match = re.search(r'^\s+([A-Z]{2})\s+([A-Z]{2})\s+([A-Z0-9]{3})\s+(\d{3})', linha)
        if match:
            p = linha.split()
            if len(p) >= 16:
                try:
                    item = {
                        "Origem": p[0], "Destino": p[1], "Trib": p[2], "ST": p[3],
                        "Ent_Trib": p[7], "Ent_Isento": p[8], "Ent_Aliq": p[10], "Ent_CTF": p[11],
                        "Sai_Trib": p[12], "Sai_Isento": p[13], "Sai_Aliq": p[15], "Sai_CTF": p[16]
                    }
                    dados.append(item)
                except: continue
    return pd.DataFrame(dados)

# --- INTERFACE ---
st.title("📑 Consulta Fiscal Inteligente")
st.sidebar.header("1. Empresa e Direção")

empresa = st.sidebar.selectbox("Empresa", ["GOLDEN", "NUCLEO"])
# NOVA OPÇÃO: Escolher qual coluna o filtro deve olhar
direcao = st.sidebar.radio("Filtrar valores baseados em:", ["Saída", "Entrada"])

prefixo = "Sai_" if direcao == "Saída" else "Ent_"
arquivo_map = {"GOLDEN": "TRIBUTACOES_GOLDEN.txt", "NUCLEO": "TRIBUTACOES_NUCLEO.txt"}

df = carregar_dados(arquivo_map[empresa])

if df is not None and not df.empty:
    st.sidebar.markdown("---")
    st.sidebar.header("2. Filtros de Localização")
    f_origem = st.sidebar.multiselect("UF Origem", options=sorted(df['Origem'].unique()))
    f_destino = st.sidebar.multiselect("UF Destino", options=sorted(df['Destino'].unique()))
    f_trib = st.sidebar.multiselect("Cód. Tributação", options=sorted(df['Trib'].unique()))
    
    st.sidebar.markdown("---")
    st.sidebar.header(f"3. Filtros de {direcao}")
    
    # Filtros dinâmicos baseados na direção escolhida
    f_st = st.sidebar.multiselect("Situação Tributária (ST)", options=sorted(df['ST'].unique()))
    f_aliq = st.sidebar.multiselect(f"Alíquota ICMS ({direcao})", options=sorted(df[f'{prefixo}Aliq'].unique()))
    f_trib_val = st.sidebar.multiselect(f"% Tributado ({direcao})", options=sorted(df[f'{prefixo}Trib'].unique()))
    f_ctf = st.sidebar.multiselect(f"Código CTF ({direcao})", options=sorted(df[f'{prefixo}CTF'].unique()))

    # --- APLICAÇÃO ---
    query = df.copy()
    if f_origem: query = query[query['Origem'].isin(f_origem)]
    if f_destino: query = query[query['Destino'].isin(f_destino)]
    if f_trib: query = query[query['Trib'].isin(f_trib)]
    if f_st: query = query[query['ST'].isin(f_st)]
    if f_aliq: query = query[query[f'{prefixo}Aliq'].isin(f_aliq)]
    if f_trib_val: query = query[query[f'{prefixo}Trib'].isin(f_trib_val)]
    if f_ctf: query = query[query[f'{prefixo}CTF'].isin(f_ctf)]

    st.info(f"Filtros aplicados na **{direcao}** da **{empresa}** | {len(query)} resultados.")

    for _, row in query.iterrows():
        # Cor de destaque baseada na ST (020 ganha cor diferente para alertar redução)
        header_color = "orange" if row['ST'] == "020" else "blue"
        
        with st.expander(f"📍 {row['Origem']} para {row['Destino']} | Trib: {row['Trib']} | ST: {row['ST']}"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### 📥 ENTRADA")
                st.write(f"**% Trib:** {row['Ent_Trib']}% | **Isento:** {row['Ent_Isento']}%")
                st.write(f"**Alíquota:** {row['Ent_Aliq']}% | **CTF:** {row['Ent_CTF']}")
            with c2:
                st.markdown("### 📤 SAÍDA")
                st.write(f"**% Trib:** {row['Sai_Trib']}% | **Isento:** {row['Sai_Isento']}%")
                st.write(f"**Alíquota:** {row['Sai_Aliq']}% | **CTF:** {row['Sai_CTF']}")
else:
    st.error("Arquivo não encontrado.")
