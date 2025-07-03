import streamlit as st
import pandas as pd
import plotly.express as px

def render_divergence_tab(data_df):
    st.markdown("<h2 class='section-header'>Análise de Divergências no Processo</h2>", unsafe_allow_html=True)
    st.info("Esta análise mostra itens que 'vazaram' do funil ou que pularam etapas, ajudando a identificar perdas de negócio ou falhas de processo.", icon="💡")

    orc_chaves = set(data_df[data_df['etapa'] == 'Orçamento']['chave'].unique())
    rec_chaves = set(data_df[data_df['etapa'] == 'Recarga']['chave'].unique())
    fin_chaves = set(data_df[data_df['etapa'] == 'Finalização']['chave'].unique())
    
    orc_sem_rec = orc_chaves - rec_chaves
    rec_sem_fin = rec_chaves - fin_chaves
    
    col1, col2 = st.columns(2)

    with col1:
        with st.expander(f"Orçados que não viraram Recarga ({len(orc_sem_rec)} itens)"):
            if orc_sem_rec:
                df_leak = data_df[data_df['chave'].isin(orc_sem_rec)].drop_duplicates('chave')
                st.dataframe(df_leak[['cliente', 'nota_fiscal', 'numero_serie', 'numero_lacre']])
                
                st.markdown("###### Clientes com mais orçamentos parados:")
                fig = px.bar(df_leak['cliente'].value_counts().nlargest(5))
                st.plotly_chart(fig, use_container_width=True)

    with col2:
        with st.expander(f"Em Recarga e não Finalizados ({len(rec_sem_fin)} itens)"):
            if rec_sem_fin:
                df_wip = data_df[data_df['chave'].isin(rec_sem_fin)].drop_duplicates('chave', keep='last')
                st.dataframe(df_wip[['cliente', 'nota_fiscal', 'numero_serie', 'numero_lacre', 'etapa']])
                
                st.markdown("###### Clientes com mais itens em andamento:")
                fig = px.bar(df_wip['cliente'].value_counts().nlargest(5))
                st.plotly_chart(fig, use_container_width=True)