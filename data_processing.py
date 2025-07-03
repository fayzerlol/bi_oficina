import pandas as pd
import re
import streamlit as st

@st.cache_data
def load_and_process_data(uploaded_file, unique_key_cols):
    """
    Carrega dados do Excel, limpa, unifica e aplica a lógica de negócio
    para propagar o nome do cliente a partir dos orçamentos.
    """
    xls = pd.ExcelFile(uploaded_file)
    SHEETS = [
        ("orc_A", "Ampola", "Orçamento"), ("rec_A", "Ampola", "Recarga"), ("fin_A", "Ampola", "Finalização"), ("th_A", "Ampola", "Teste Hidrostático"),
        ("orc_T_P", "Tanque Pressurizado", "Orçamento"), ("rec_T_P", "Tanque Pressurizado", "Recarga"), ("fin_T_P", "Tanque Pressurizado", "Finalização"),
        ("orc_T_S", "Tanque Sem Pressão", "Orçamento"), ("rec_T_S", "Tanque Sem Pressão", "Recarga")
    ]
    COLMAP = {
        "nota_fiscal": ["Nota Fiscal", "Número da Nota Fiscal", "Nº Nota Fiscal"], "numero_serie": ["Número de Série", "Nº de Série"],
        "numero_lacre": ["Número do Lacre", "Nº do Lacre"], "cliente": ["Cliente"],
        "laudo_tecnico": ["Análise Técnica:", "Laudo.", "Laudo Técnico"],
        "data_th": ["Data do Teste Hidrostático", "Data Fabricação / Teste Hidrostático"], "data_inicio": ["Início:"]
    }

    def clean_key_text(text):
        if pd.isna(text): return ""
        s = str(text).replace('.0', '')
        s = re.sub(r'[^A-Z0-9]', '', s.upper()); return s
    def clean_text(text):
        if pd.isna(text): return ""
        return str(text).strip().upper()
    def clean_and_convert_date(column):
        dates = pd.to_datetime(column, errors='coerce')
        return dates.where(dates.dt.year != 1970, pd.NaT)

    all_data = []
    for sheet_name, tipo_item, etapa in SHEETS:
        if sheet_name in xls.sheet_names:
            df_raw = xls.parse(sheet_name)
            df_processed = pd.DataFrame()
            for target_col, source_options in COLMAP.items():
                found_col = next((col for col in source_options if col in df_raw.columns), None)
                if found_col:
                    if target_col in ["nota_fiscal", "numero_serie", "numero_lacre"]: df_processed[target_col] = df_raw[found_col].apply(clean_key_text)
                    elif target_col in ['cliente', 'laudo_tecnico']: df_processed[target_col] = df_raw[found_col].apply(clean_text)
                    elif "data" in target_col: df_processed[target_col] = clean_and_convert_date(df_raw[found_col])
                else: df_processed[target_col] = "" if "data" not in target_col else pd.NaT
            df_processed["tipo_item"], df_processed["etapa"] = tipo_item, etapa
            all_data.append(df_processed)

    if not all_data: return pd.DataFrame(), {}
    
    df_full = pd.concat(all_data, ignore_index=True)
    stats = {"rows_read": len(df_full)}
    
    df_full['chave'] = df_full['tipo_item'].astype(str) + "|" + df_full[unique_key_cols].agg("|".join, axis=1)
    df_full = df_full[df_full['chave'].str.replace('|', '').str.strip().astype(bool)]
    stats["rows_after_key_drop"] = len(df_full)

    df_com_cliente = df_full[df_full['cliente'].astype(str).str.strip() != ''].copy()
    mapa_mestre_clientes = df_com_cliente.drop_duplicates('chave', keep='first').set_index('chave')['cliente']
    df_full['cliente'] = df_full['chave'].map(mapa_mestre_clientes)
    
    df_com_laudo = df_full[df_full['laudo_tecnico'].astype(str).str.strip() != ''].copy()
    if not df_com_laudo.empty:
        mapa_mestre_laudos = df_com_laudo.drop_duplicates('chave', keep='first').set_index('chave')['laudo_tecnico']
        df_full['laudo_tecnico'] = df_full['chave'].map(mapa_mestre_laudos)
    
    df_full.dropna(subset=['cliente'], inplace=True)
    df_full['laudo_tecnico'].fillna('N/D', inplace=True)
    stats["rows_after_orphans_drop"] = len(df_full)
    
    return df_full.sort_values("data_inicio"), stats