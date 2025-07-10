import pandas as pd
import numpy as np

def carregar_clientes_do_excel(caminho):
    df = pd.read_excel(caminho)
    df.columns = [c.lower().strip() for c in df.columns]
    
    # Garantindo que produtos seja sempre uma string, removendo colchetes e espaços extras
    df['produtos'] = df['produtos'].fillna('')
    df['produtos'] = df['produtos'].astype(str)
    df['produtos'] = df['produtos'].apply(lambda x: x.strip('[]').replace(' ', ''))
    
    df['data_contratacao'] = pd.to_datetime(df['data_contratacao'], errors='coerce')
    df['ticket_medio'] = pd.to_numeric(df['ticket_medio'], errors='coerce')
    df['tempo_negociacao'] = pd.to_numeric(df['tempo_negociacao'], errors='coerce')
    
    hoje = pd.Timestamp.today()
    # Calculando a diferença em meses entre a data de contratação e hoje
    df['meses_ativo'] = ((hoje.year - df['data_contratacao'].dt.year) * 12 + 
                        (hoje.month - df['data_contratacao'].dt.month)).astype(int)
    
    # Garantindo que o ticket médio seja um número inteiro para evitar problemas de precisão
    df['ticket_medio'] = df['ticket_medio'].round(2)
    
    # Calculando o LTV como ticket médio multiplicado pelo número de meses
    df['ltv'] = (df['ticket_medio'] * df['meses_ativo']).round(2)
    
    df.rename(columns={'nome_cliente': 'nome'}, inplace=True)
    return df