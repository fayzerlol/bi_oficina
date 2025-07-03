import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import timedelta
import io
import base64
import re

def display_logo(path="logo.png", height=80):
    try:
        with open(path, "rb") as f:
            img = f.read()
        b64 = base64.b64encode(img).decode()
        st.markdown(f"<div style='text-align:center;'><img src='data:image/png;base64,{b64}' height='{height}'></div>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def to_excel(df_to_export):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df_to_export.to_excel(writer, index=False, sheet_name="Dados")
    return buf.getvalue()

def generate_detailed_report(df, chart_data_dict):
    report_sheets = chart_data_dict.copy()
    
    orc_chaves = set(df[df['etapa'] == 'Orçamento']['chave'].unique())
    rec_chaves = set(df[df['etapa'] == 'Recarga']['chave'].unique())
    fin_chaves = set(df[df['etapa'] == 'Finalização']['chave'].unique())

    if orc_sem_rec_chaves := orc_chaves - rec_chaves:
        report_sheets["Orcamento_sem_Recarga"] = df[df['chave'].isin(orc_sem_rec_chaves)].drop_duplicates('chave', keep='first')
    if rec_sem_fin_chaves := rec_chaves - fin_chaves:
        report_sheets["Recarga_sem_Finalizacao"] = df[df['chave'].isin(rec_sem_fin_chaves)].drop_duplicates('chave', keep='last')
    if fin_sem_orc_chaves := fin_chaves - orc_chaves:
        report_sheets["Finalizado_sem_Orcamento"] = df[df['chave'].isin(fin_sem_orc_chaves)].drop_duplicates('chave', keep='first')

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet_name, data in report_sheets.items():
            if not data.empty:
                data.to_excel(writer, index=False, sheet_name=sheet_name)
    return buf.getvalue()

def highlight_critical(val):
    if pd.isna(val): return ''
    if val > 365*10: return 'background-color: #ff4d4d; color: white;'
    if val > 365*8.5: return 'background-color: #ffa500; color: white;'
    return ''

def agrupar_outros(df_column, top_n=5):
    if df_column.empty: return df_column
    top_cats = df_column.value_counts().nlargest(top_n).index
    return df_column.where(df_column.isin(top_cats), "Outros")

def identify_critical_items(df):
    if df.empty: return pd.DataFrame()
    latest_status = df.sort_values("data_inicio", ascending=False).drop_duplicates(subset=['chave'], keep='first')
    crit_list = []; today = pd.Timestamp.now().normalize()
    ten_years, eight_half = timedelta(days=365.25 * 10), timedelta(days=365.25 * 8.5)
    df_com_th = latest_status.dropna(subset=['data_th'])
    for _, row in df_com_th.iterrows():
        delta = today - row['data_th']
        if delta > ten_years: crit_list.append({**row.to_dict(), "crit_tipo": "TH vencido", "dias_vencido": delta.days})
        elif delta > eight_half: crit_list.append({**row.to_dict(), "crit_tipo": "TH quase vencido", "dias_vencido": delta.days})
    return pd.DataFrame(crit_list)

def calculate_lead_times(df):
    if df.empty: return pd.DataFrame()
    df_sorted = df.sort_values('data_inicio')
    df_pivot = df_sorted.pivot_table(index='chave', columns='etapa', values='data_inicio', aggfunc='first')
    if 'Orçamento' in df_pivot and 'Recarga' in df_pivot: df_pivot['Orçamento ➔ Recarga'] = (df_pivot['Recarga'] - df_pivot['Orçamento']).dt.days
    if 'Recarga' in df_pivot and 'Finalização' in df_pivot: df_pivot['Recarga ➔ Finalização'] = (df_pivot['Finalização'] - df_pivot['Recarga']).dt.days
    return df_pivot.reset_index()

def create_sankey_chart(df):
    if len(df) < 2: return None
    paths = df.groupby('chave')['etapa'].apply(list).reset_index()
    links = paths['etapa'].apply(lambda x: list(zip(x, x[1:]))).explode().dropna()
    if links.empty: return None
    df_links = links.value_counts().reset_index(); df_links.columns = ['path', 'value']
    df_links[['source', 'target']] = pd.DataFrame(df_links['path'].tolist(), index=df_links.index)
    labels = pd.unique(df_links[['source', 'target']].values.ravel('K'))
    label_map = {label: i for i, label in enumerate(labels)}
    fig = go.Figure(go.Sankey(
        node=dict(pad=25, thickness=20, label=labels, color="#f4a100"),
        link=dict(source=df_links['source'].map(label_map), target=df_links['target'].map(label_map), value=df_links['value'])
    ))
    fig.update_layout(title_text="Fluxo de Itens Entre Etapas", font_size=12, margin=dict(l=0, r=0, t=40, b=5))
    return fig

def clean_key_text(text):
    """Função exportada para ser usada também no app.py"""
    if pd.isna(text): return ""
    s = str(text).replace('.0', '')
    return re.sub(r'[^A-Z0-9]', '', s.upper())