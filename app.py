import streamlit as st
import pandas as pd
import re

# Configuração visual para parecer um sistema profissional
st.set_page_config(page_title="Consulta Fiscal - Golden/Nucleo", layout="wide")

def carregar_dados(caminho_arquivo):
    dados = []
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
    except FileNotFoundError:
        return None

    # Regex para identificar as linhas de dados (Ex: AC SP TSN 000...)
    # Filtra linhas que começam com a sigla de um estado
    linhas = re.findall(r'^\s+([A-Z]{2})\s+([A-Z]{2})\s+([A-Z0-9]{2,3})\s+(\d{3}).*', conteudo, re.MULTILINE)
    
    # Processamento manual para garantir precisão nas colunas do relatório
    todas_linhas = conteudo.split('\n')
    for i, linha in enumerate(todas_linhas):
        # Verifica se a linha tem o formato de dados (Origem e Destino)
        match = re.search(r'^\s+([A-Z]{2})\s+([A-Z]{2})\s+([A-Z0-9]{2,3})\s+(\d{3})', linha)
        if match:
            partes = linha.split()
            # O relatório tem larguras fixas, mas o split resolve a maioria dos casos
            # Se a linha for de dados completa:
            if len(partes) >= 15:
                item = {
                    "Origem": partes[0],
                    "Destino": partes[1],
                    "Trib": partes[2],
                    "ST": partes[3],
                    "Ent_Tributado": partes[7],
                    "Ent_Aliq": partes[10],
                    "Ent_CTF": partes[11],
                    "Sai_Tributado": partes[12],
                    "Sai_Aliq": partes[15],
                    "Sai_CTF": partes[16]
                }
                dados.append(item)
    
    return pd.DataFrame(dados)

# --- INTERFACE ---
st.title("📑 Sistema de Consulta de Tributações")
st.markdown("---")

# Seleção de Empresa na lateral
st.sidebar.header("Configurações")
empresa = st.sidebar.selectbox("Selecione a Empresa", ["GOLDEN", "NUCLEO"])

# Mapeamento dos nomes de arquivo conforme solicitado
arquivo_map = {
    "GOLDEN": "TRIBUTACOES_GOLDEN.txt",
    "NUCLEO": "TRIBUTACOES_NUCLEO.txt"
}

df = carregar_dados(arquivo_map[empresa])

if df is not None and not df.empty:
    # Filtros Dinâmicos
    st.sidebar.subheader("Filtros")
    f_origem = st.sidebar.multiselect("UF Origem", options=sorted(df['Origem'].unique()))
    f_destino = st.sidebar.multiselect("UF Destino", options=sorted(df['Destino'].unique()))
    f_trib = st.sidebar.multiselect("Código Trib.", options=sorted(df['Trib'].unique()))

    # Aplicação dos filtros
    query = df.copy()
    if f_origem: query = query[query['Origem'].isin(f_origem)]
    if f_destino: query = query[query['Destino'].isin(f_destino)]
    if f_trib: query = query[query['Trib'].isin(f_trib)]

    # Exibição
    st.info(f"Exibindo tributações para: **{empresa}** ({len(query)} registros encontrados)")

    for _, row in query.iterrows():
        # Card visual similar ao print do sistema
        with st.container():
            st.markdown(f"### 📍 {row['Origem']} para {row['Destino']} | Tipo: {row['Trib']}")
            c1, c2 = st.columns(2)
            
            with c1:
                st.markdown("**📥 ENTRADA**")
                st.code(f"Tributado: {row['Ent_Tributado']}%\nAlíquota:  {row['Ent_Aliq']}%\nCTF:       {row['Ent_CTF']}")
            
            with c2:
                st.markdown("**📤 SAÍDA**")
                st.code(f"Tributado: {row['Sai_Tributado']}%\nAlíquota:  {row['Sai_Aliq']}%\nCTF:       {row['Sai_CTF']}")
            st.markdown("---")
else:
    st.error(f"Arquivo **{arquivo_map[empresa]}** não encontrado ou está vazio.")
    st.info("Certifique-se de que o arquivo está na raiz do seu repositório no GitHub.")
