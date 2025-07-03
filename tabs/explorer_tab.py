import streamlit as st
import re
import pandas as pd

def render_explorer_tab(df_main):
    st.markdown("<h2 class='section-header'>Explorador de Itens</h2>", unsafe_allow_html=True)
    st.info("Digite qualquer parte de uma Nota Fiscal, Nº de Série ou Lacre para ver o histórico completo do item.", icon="🔎")
    
    def clean_key_text(text):
        if pd.isna(text): return ""
        s = str(text).replace('.0', '')
        return re.sub(r'[^A-Z0-9]', '', s.upper())

    search_term = st.text_input("Buscar item específico:", placeholder="Ex: 17849 ou ABC01...")
    
    if search_term:
        term = clean_key_text(search_term)
        mask = df_main.apply(lambda row: term in row['nota_fiscal'] or term in row['numero_serie'] or term in row['numero_lacre'], axis=1)
        result_df = df_main[mask]
        
        if result_df.empty:
            st.warning("Nenhum item encontrado.")
        else:
            chaves_encontradas = result_df['chave'].unique()
            st.write(f"Encontrado(s) {len(chaves_encontradas)} item(ns) único(s).")
            final_result_df = df_main[df_main['chave'].isin(chaves_encontradas)].sort_values(["chave", "data_inicio"])
            st.dataframe(final_result_df)