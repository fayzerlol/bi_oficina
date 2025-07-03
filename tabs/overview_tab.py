import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import create_sankey_chart

def render_overview_tab(data_df, sel_cli, report_data):
    st.markdown("<h2 class='section-header'>Métricas Principais e Fluxo</h2>", unsafe_allow_html=True)
    if data_df.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
        return

    orcados = data_df[data_df['etapa']=='Orçamento']['chave'].nunique()
    finalizados = data_df[data_df['etapa']=='Finalização']['chave'].nunique()
    taxa_conversao = (finalizados / orcados * 100) if orcados > 0 else 0
    df_finalizados = data_df[data_df['etapa']=='Finalização'].copy()
    if not df_finalizados.empty and pd.api.types.is_datetime64_any_dtype(df_finalizados['data_inicio']):
        df_finalizados['semana'] = df_finalizados['data_inicio'].dt.to_period('W')
        throughput_semanal = df_finalizados.groupby('semana')['chave'].nunique().mean()
    else:
        throughput_semanal = 0
    
    c1,c2,c3 = st.columns(3)
    c1.markdown(f"<div class='metric-container'><div class='metric-title'>Itens Únicos na Visão</div><div class='metric-value'>{data_df['chave'].nunique()}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric-container'><div class='metric-title'>Taxa de Conversão</div><div class='metric-value'>{taxa_conversao:.1f}%</div><div style='font-size:.8rem'>(Orçados → Finalizados)</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric-container'><div class='metric-title'>Vazão Semanal Média</div><div class='metric-value'>{throughput_semanal:.1f}</div><div style='font-size:.8rem'>(Itens Finalizados/Semana)</div></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("<h3 class='section-header'>Análise de Fluxo e Volume</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Fluxo do Processo (Sankey)")
        fig_sankey = create_sankey_chart(data_df)
        if fig_sankey:
            st.plotly_chart(fig_sankey, use_container_width=True)
        else:
            st.info("Não há dados de fluxo suficientes para exibir.")
    with col2:
        if sel_cli == "Todos":
            st.markdown("##### Top 10 Clientes (por Itens Únicos)")
            top_cli_data = data_df.drop_duplicates(subset=['chave']).cliente.value_counts().nlargest(10).reset_index()
            top_cli_data.columns=["Cliente","Quantidade de Itens Únicos"]
            report_data["Top_10_Clientes"] = top_cli_data
            fig_cli = px.bar(top_cli_data,x="Quantidade de Itens Únicos",y="Cliente",orientation="h",text="Quantidade de Itens Únicos")
            fig_cli.update_layout(yaxis={'categoryorder':'total ascending'},margin=dict(l=0,r=0,t=20,b=20))
            st.plotly_chart(fig_cli,use_container_width=True)
        else:
            st.markdown(f"##### Etapas para {sel_cli}")
            etapas_cli = data_df['etapa'].value_counts().reset_index(); etapas_cli.columns=['Etapa','Quantidade de Registros']
            report_data[f"Etapas_{sel_cli.replace(' ','_')}"] = etapas_cli
            fig_etapas = px.bar(etapas_cli,x='Etapa',y='Quantidade de Registros',text='Quantidade de Registros',color='Etapa')
            fig_etapas.update_layout(margin=dict(l=0,r=0,t=20,b=20)); st.plotly_chart(fig_etapas,use_container_width=True)