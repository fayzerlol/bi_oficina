import streamlit as st
import pandas as pd
from data_processing import load_and_process_data
from utils import (
    display_logo, to_excel, generate_detailed_report, clean_key_text
)
from tabs.overview_tab import render_overview_tab
from tabs.lead_time_tab import render_lead_time_tab
from tabs.risk_tab import render_risk_tab
from tabs.divergence_tab import render_divergence_tab
from tabs.explorer_tab import render_explorer_tab

# === Configuração da página e CSS ===
st.set_page_config(page_title="BI Ampolas & Tanques", page_icon="🚀", layout="wide")
st.markdown("""
<style>
body { background-color: #F8F9FA; font-family: 'Inter', sans-serif; }
.main-header { font-size:2.4rem; font-weight:900; text-align:center;
  background:linear-gradient(90deg,#ffd600,#ffe066,#fff5cc);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent;
  margin:1.5rem 0; }
.section-header { font-size:1.5rem; font-weight:700; color:#f4a100; margin:1.5rem 0; }
.metric-container { background:#fffbe7; border-radius:12px;
  box-shadow:0 4px 20px rgba(0,0,0,0.05); padding:1.2rem; text-align:center;
  margin-bottom:1rem; }
.metric-title { font-size:1.1rem; color:#3366CC; margin-bottom:0.5rem; }
.metric-value { font-size:2rem; font-weight:700; color:#f4a100; }
.footer { text-align:center; color:#9e8b36; margin:2rem 0 1rem 0; }
</style>
""", unsafe_allow_html=True)

# === UI e Lógica Principal ===
display_logo()
st.markdown('<h1 class="main-header">BI Ampolas & Tanques - Grupo Franzen</h1>', unsafe_allow_html=True)

# --- Upload e Carregamento dos Dados ---
upload = st.sidebar.file_uploader("Upload do arquivo Excel (.xlsx)", type=["xlsx"])
if not upload:
    st.info("Por favor, faça o upload de um arquivo Excel para começar.")
    st.stop()

# --- Filtros da Sidebar ---
st.sidebar.header("Filtros Dinâmicos")
keys = st.sidebar.multiselect("Campos para chave única:", ["nota_fiscal", "numero_serie", "numero_lacre"], default=["nota_fiscal", "numero_serie", "numero_lacre"])
if not keys:
    st.sidebar.error("Selecione ao menos um campo para a chave única.")
    st.stop()

df_main, stats = load_and_process_data(upload, keys)
if df_main.empty:
    st.error("Nenhum dado válido encontrado.")
    st.stop()

painel = st.sidebar.radio("Painel:", ["Todos", "Ampola", "Tanque Pressurizado", "Tanque Sem Pressão"])
data_df = df_main.copy()
if painel != "Todos":
    data_df = data_df[data_df["tipo_item"] == painel]

clientes_disponiveis = ["Todos"] + sorted(data_df["cliente"].unique())
sel_cli = st.sidebar.selectbox("Cliente:", clientes_disponiveis)
if sel_cli != "Todos":
    data_df = data_df[data_df["cliente"] == sel_cli]

# ### NOVO: Filtro por Nota Fiscal Específica ###
nf_search = st.sidebar.text_input("Buscar por Nota Fiscal Específica:")
if nf_search:
    # Usa a mesma função de limpeza dos dados para garantir a comparação correta
    cleaned_nf_search = clean_key_text(nf_search)
    data_df = data_df[data_df['nota_fiscal'] == cleaned_nf_search]


# --- Resumo Dinâmico ---
total_unicos_filtrado = data_df['chave'].nunique()
st.markdown(f"Exibindo **{total_unicos_filtrado}** itens únicos para o painel **{painel}** e cliente **{sel_cli}**.")
st.markdown("---")

# --- Coleta de dados para o relatório ---
report_data = {}

# --- Abas do Dashboard ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Visão Geral",
    "⏱️ Análise de Tempo",
    "⚠️ Análise de Divergências",
    "🔥 Análise de Riscos (TH)",
    "🔎 Explorador de Itens"
])

with tab1:
    render_overview_tab(data_df, sel_cli, report_data)

with tab2:
    render_lead_time_tab(data_df)

with tab3:
    render_divergence_tab(data_df)

with tab4:
    render_risk_tab(data_df, keys)

with tab5:
    render_explorer_tab(df_main)


# --- Sidebar: Ferramentas de Exportação e Info ---
st.sidebar.markdown("---")
st.sidebar.header("Ferramentas e Exportação")

with st.sidebar.expander("ℹ️ Qualidade da Importação"):
    st.write(f"Linhas lidas do Excel: **{stats.get('rows_read', 0)}**")
    st.write(f"Linhas c/ chave vazia (descartadas): **{stats.get('rows_read', 0) - stats.get('rows_after_key_drop', 0)}**")
    st.write(f"Itens órfãos (sem cliente): **{stats.get('rows_after_orphans_drop', 0)}**")
    st.write(f"Total de registros válidos: **{stats.get('rows_after_orphans_drop', 0)}**")

st.sidebar.download_button(
    label="📥 Baixar Dados da Visão Atual",
    data=to_excel(data_df),
    file_name=f"dados_filtrados_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.ms-excel"
)

st.sidebar.download_button(
    label="📄 Baixar Relatório Detalhado",
    data=generate_detailed_report(data_df, report_data),
    file_name=f"relatorio_detalhado_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.ms-excel"
)

st.markdown('<div class="footer">BI Ampolas & Tanques • Powered by Rennan Miranda</div>', unsafe_allow_html=True)