import streamlit as st
import pandas as pd
import re

# Configuração da Página
st.set_page_config(page_title="Consulta de Tributações", layout="wide")

def carregar_dados(caminho_arquivo):
    dados = []
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
        
    # Regex para capturar os blocos de tributação ignorando cabeçalhos de página
    # Padrão: Orig Dest Trib ST Marg...
    padrao = r"(\s+[A-Z]{2}\s+[A-Z]{2}\s+[A-Z0-9]{3}\s+\d{3}.*?)(?=-{50,}|$)"
    blocos = re.findall(padrao, conteudo, re.DOTALL)

    for bloco in blocos:
        linhas = [l.strip() for l in bloco.strip().split('\n') if l.strip()]
        if not linhas: continue
        
        # Primeira linha contém os valores principais
        partes = re.split(r'\s+', linhas[0])
        
        # Mapeamento conforme o layout do arquivo TXT [cite: 4, 22, 181]
        try:
            item = {
                "Origem": partes[0],
                "Destino": partes[1],
                "Tributação": partes[2],
                "ST": partes[3],
                "Entrada_%Trib": partes[7],
                "Entrada_Aliq": partes[10],
                "Entrada_CTF": partes[11],
                "Saída_%Trib": partes[12],
                "Saída_Aliq": partes[15],
                "Saída_CTF": partes[16]
            }
            dados.append(item)
        except IndexError:
            continue
            
    return pd.DataFrame(dados)

# --- INTERFACE ---
st.title("📑 Consulta de Tributações por UF")

# Seleção de Empresa
empresa = st.sidebar.selectbox("Selecione a Empresa", ["GOLDEN", "NUCLEO"])
arquivo_map = {
    "GOLDEN": "TRIBUTACOES_GOLDEN.txt",
    "NUCLEO": "TRIBUTACOES_NUCLEO.txt"
}

try:
    df = carregar_dados(arquivo_map[empresa])

    # Filtros na Barra Lateral
    st.sidebar.header("Filtros de Busca")
    origem = st.sidebar.multiselect("UF Origem", options=sorted(df['Origem'].unique()))
    destino = st.sidebar.multiselect("UF Destino", options=sorted(df['Destino'].unique()))
    trib = st.sidebar.multiselect("Cód. Tributação", options=sorted(df['Tributação'].unique()))

    # Aplicar Filtros
    df_filtrado = df.copy()
    if origem: df_filtrado = df_filtrado[df_filtrado['Origem'].isin(origem)]
    if destino: df_filtrado = df_filtrado[df_filtrado['Destino'].isin(destino)]
    if trib: df_filtrado = df_filtrado[df_filtrado['Tributação'].isin(trib)]

    # Exibição dos Cards (Simulando o Print do Sistema)
    st.subheader(f"Resultados para {empresa}")
    
    if df_filtrado.empty:
        st.warning("Nenhuma tributação encontrada com esses filtros.")
    else:
        for index, row in df_filtrado.iterrows():
            with st.expander(f"📍 {row['Origem']} ➡️ {row['Destino']} | Tributação: {row['Tributação']}", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**⬇️ ENTRADA**")
                    st.info(f"**% Tributado:** {row['Entrada_%Trib']}%\n\n**Alíquota ICMS:** {row['Entrada_Aliq']}%\n\n**CTF:** {row['Entrada_CTF']}")
                
                with col2:
                    st.markdown("**⬆️ SAÍDA**")
                    st.success(f"**% Tributado:** {row['Saída_%Trib']}%\n\n**Alíquota ICMS:** {row['Saída_Aliq']}%\n\n**CTF:** {row['Saída_CTF']}")

except FileNotFoundError:
    st.error(f"Arquivo {arquivo_map[empresa]} não encontrado no repositório.")
