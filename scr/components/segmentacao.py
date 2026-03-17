from components.utils import calcular_segmentacao, calcular_metricas_segmentacao
import pandas as pd
import numpy as np
import locale

# Configurar locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # Usa o padrão do sistema

def formatar_valor(valor):
    # Se não for um número ou string numérica, retorna o valor original
    if not isinstance(valor, (int, float)):
        try:
            # Tenta converter para float se for uma string numérica
            if isinstance(valor, str):
                valor = float(valor.replace('R$', '').replace('.', '').replace(',', '.').strip())
            else:
                return valor
        except ValueError:
            return valor
            
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_ltv(df):
    """Calcula o LTV (Life-Time Value) para cada cliente"""
    df = df.copy()  # Criar cópia para não modificar o original
    
    # Verifica se temos as colunas necessárias
    if 'ticket_medio' not in df.columns and 'valor_contrato' in df.columns:
        df['ticket_medio'] = df['valor_contrato']
        
    # Calcular meses_ativo se não existir
    if 'meses_ativo' not in df.columns and 'data_contratacao' in df.columns:
        # Calcular baseado na data de contratação
        df['data_contratacao'] = pd.to_datetime(df['data_contratacao'], errors='coerce')
        hoje = pd.Timestamp.now()
        df['meses_ativo'] = ((hoje - df['data_contratacao']).dt.days / 30).fillna(12).astype(int)
        
    # Calcula o LTV
    df['ltv'] = df['ticket_medio'] * df['meses_ativo']
    return df

def get_segmentacao_data():
    return {'message': 'Segmentacao data placeholder'} 