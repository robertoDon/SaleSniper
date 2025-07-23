import pandas as pd
import numpy as np

def carregar_clientes_do_excel(arquivo):
    df = pd.read_excel(arquivo)
    # Lista de colunas esperadas e valores default
    colunas_default = {
        'produtos': '',
        'data_contratacao': pd.NaT,
        'data_entrada': pd.NaT,
        'data_churn': pd.NaT,
        'tempo_negociacao': 0,
        'perfil': '',
        'canal_aquisicao': '',
        'regiao': '',
        'idade': 0,
        'tempo_casa': 0,
        'score_engajamento': 0.0
    }
    for col, default in colunas_default.items():
        if col not in df.columns:
            df[col] = default
    # Tratamento padrão para colunas específicas
    df['produtos'] = df['produtos'].fillna('').astype(str)
    df['data_contratacao'] = pd.to_datetime(df['data_contratacao'], errors='coerce')
    df['data_entrada'] = pd.to_datetime(df['data_entrada'], errors='coerce')
    df['data_churn'] = pd.to_datetime(df['data_churn'], errors='coerce')
    df['tempo_negociacao'] = pd.to_numeric(df['tempo_negociacao'], errors='coerce').fillna(0).astype(int)
    df['idade'] = pd.to_numeric(df['idade'], errors='coerce').fillna(0).astype(int)
    df['tempo_casa'] = pd.to_numeric(df['tempo_casa'], errors='coerce').fillna(0).astype(int)
    df['score_engajamento'] = pd.to_numeric(df['score_engajamento'], errors='coerce').fillna(0.0).astype(float)
    return df