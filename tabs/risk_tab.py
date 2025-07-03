import streamlit as st
from utils import identify_critical_items, highlight_critical

def render_risk_tab(data_df, keys):
    st.markdown("<h2 class='section-header'>Monitoramento de Riscos e Prazos de TH</h2>", unsafe_allow_html=True)
    df_crit = identify_critical_items(data_df)
    
    if df_crit.empty:
        st.success("Nenhum item com risco de vencimento de teste hidrostático encontrado.", icon="✅")
    else:
        crit_tipos = df_crit.crit_tipo.unique()
        cols_to_show = ['cliente'] + keys + ['data_th', 'dias_vencido']
        
        if "TH quase vencido" in crit_tipos:
            st.markdown("##### ⚠️ Quase Vencido")
            df_q = df_crit[df_crit.crit_tipo == "TH quase vencido"]
            st.dataframe(df_q[cols_to_show].style.map(highlight_critical, subset=['dias_vencido']))
            
        if "TH vencido" in crit_tipos:
            st.markdown("##### 🔥 Vencido")
            df_v = df_crit[df_crit.crit_tipo == "TH vencido"]
            st.dataframe(df_v[cols_to_show].style.map(highlight_critical, subset=['dias_vencido']))