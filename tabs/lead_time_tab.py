import streamlit as st
import plotly.express as px
from utils import calculate_lead_times

def render_lead_time_tab(data_df):
    st.markdown("<h2 class='section-header'>Análise de Performance do Processo (Lead Time)</h2>", unsafe_allow_html=True)
    st.info("Lead Time (ou Tempo de Ciclo) é o tempo em dias que um item leva para passar de uma etapa para outra. Use isso para encontrar gargalos e medir a eficiência.", icon="💡")
    
    df_lead = calculate_lead_times(data_df)
    
    if df_lead.empty or df_lead.drop(columns=['chave']).isnull().all().all():
        st.info("Não há dados suficientes para calcular o tempo entre etapas com os filtros atuais.")
        return

    st.markdown("##### Tempo Médio Entre Etapas (dias)")
    c1, c2 = st.columns(2)
    lead_cols_options = {col:col for col in df_lead.columns if "➔" in col}
    
    mean_orc_rec = df_lead['Orçamento ➔ Recarga'].mean() if 'Orçamento ➔ Recarga' in df_lead else 0
    mean_rec_fin = df_lead['Recarga ➔ Finalização'].mean() if 'Recarga ➔ Finalização' in df_lead else 0
    c1.metric("Orçamento ➔ Recarga", f"{mean_orc_rec:.1f} dias")
    c2.metric("Recarga ➔ Finalização", f"{mean_rec_fin:.1f} dias")
    
    st.markdown("##### Distribuição do Tempo de Ciclo")
    if lead_cols_options:
        sel_lead_label = st.selectbox("Ver distribuição de tempo para:", lead_cols_options.values())
        
        fig_hist = px.histogram(df_lead, x=sel_lead_label, nbins=20, title=f"Distribuição: {sel_lead_label}")
        mean_val = df_lead[sel_lead_label].mean()
        fig_hist.add_vline(x=mean_val, line_dash="dash", line_color="red", annotation_text=f"Média: {mean_val:.1f} dias")
        st.plotly_chart(fig_hist, use_container_width=True)