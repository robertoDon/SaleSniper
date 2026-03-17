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

def get_segmentacao_data(arquivo, campo: str = 'ltv', tipo_segmentacao: str = '80/20', percentuais=None) -> dict:
    """Processa segmentação baseada em arquivo Excel de clientes.

    Args:
        arquivo: arquivo enviado pelo formulário (werkzeug FileStorage)
        campo: campo base para segmentação (ex: 'ltv', 'ticket_medio')
        tipo_segmentacao: '80/20' ou '20/30/30/20'
        percentuais: inteiro (para 80/20) ou lista de 4 inteiros (para 20/30/30/20)
    """
    try:
        # Carregar dados e garantir colunas do segmento
        df_original = pd.read_excel(arquivo)
        df = df_original.copy()
        if 'ticket_medio' not in df.columns and 'valor_contrato' in df.columns:
            df['ticket_medio'] = df['valor_contrato']
        # Se ainda não existir, calcula LTV se possível
        if 'ltv' not in df.columns:
            df = calcular_ltv(df)

        # Executa a segmentação
        df_seg = calcular_segmentacao(df, campo, tipo_segmentacao, percentuais)

        # Métricas auxiliares para exibição
        metricas = None
        try:
            df_metricas, meta_info = calcular_metricas_segmentacao(df, campo, tipo_segmentacao)
            metricas = {
                'n_segmentos': len(df_seg),
                'maior_valor': df_seg[campo].max() if campo in df_seg.columns else None,
                'menor_valor': df_seg[campo].min() if campo in df_seg.columns else None,
                'meta_info': meta_info
            }
        except Exception:
            metricas = None

        return {
            'segmentacao': df_seg.to_dict(orient='records'),
            'metricas': metricas,
            'campo': campo,
            'tipo': tipo_segmentacao,
            'num_clientes': len(df),
            'colunas': list(df.columns)
        }
    except Exception as e:
        return {'error': f'Erro ao processar segmentação: {e}'}
