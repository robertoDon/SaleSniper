import streamlit as st
import pandas as pd
from typing import Tuple, Dict, Any, List
import numpy as np
import locale
from core.sistema import Sistema

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

@st.cache_data(ttl=3600)  # Cache por 1 hora
def carregar_e_preprocessar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Função cacheada para preprocessamento de dados com otimizações de memória
    """
    # Criar cópia para não modificar o original
    df = df.copy()
    
    # Otimizar tipos de dados
    categorias = ['porte', 'segmento', 'localizacao', 'dores']
    for col in categorias:
        if col in df.columns:
            # Converter para string primeiro
            df[col] = df[col].astype(str)
            # Preencher valores nulos
            df[col] = df[col].replace('nan', 'NaN').fillna('NaN')
            # Converter para categoria incluindo NaN
            unique_values = df[col].unique()
            df[col] = pd.Categorical(df[col], categories=unique_values)
    
    # Converter colunas numéricas para tipos mais eficientes
    numericas = ['faturamento', 'ticket_medio', 'ltv', 'tempo_negociacao']
    for col in numericas:
        if col in df.columns:
            try:
                # Converter para numérico, preenchendo nulos com 0
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                # Otimizar tipo numérico baseado no range de valores
                if df[col].max() <= 32767 and df[col].min() >= -32768:
                    df[col] = df[col].astype('int16')
                elif df[col].max() <= 2147483647 and df[col].min() >= -2147483648:
                    df[col] = df[col].astype('int32')
                else:
                    df[col] = df[col].astype('float32')
            except Exception as e:
                print(f"Erro ao converter coluna {col}: {str(e)}")
                # Manter como float32 em caso de erro
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype('float32')
    
    # Tratar coluna de produtos
    if 'produtos' in df.columns:
        # Garantir que produtos seja string e tratar nulos
        df['produtos'] = df['produtos'].fillna('')
        # Normalizar separadores e limpar espaços
        df['produtos'] = (df['produtos']
                         .str.replace(',', ';')
                         .str.replace(';;', ';')
                         .str.strip()
                         .str.strip(';'))
        # Remover produtos vazios e duplicados
        df['produtos'] = df['produtos'].apply(
            lambda x: ';'.join(sorted(set(filter(None, map(str.strip, x.split(';'))))))
        )
    
    # Adicionar CNPJ se não existir
    if "cnpj" not in df.columns:
        df["cnpj"] = [f"{i:014d}" for i in range(len(df))]
    
    # Calcular meses_ativo se não existir
    if "meses_ativo" not in df.columns and "data_contratacao" in df.columns:
        # Calcular baseado na data de contratação
        df["data_contratacao"] = pd.to_datetime(df["data_contratacao"], errors='coerce')
        hoje = pd.Timestamp.now()
        df["meses_ativo"] = ((hoje - df["data_contratacao"]).dt.days / 30).fillna(12).astype(int)
    
    # Calcular LTV se não existir
    if "ltv" not in df.columns and "ticket_medio" in df.columns and "meses_ativo" in df.columns:
        df["ltv"] = df["ticket_medio"] * df["meses_ativo"]
    
    # Renomear colunas
    df = df.rename(columns={"nome_cliente": "nome"})
    
    # Remover duplicatas de colunas
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Remover colunas com muitos valores nulos
    cols_to_drop = [col for col in df.columns 
                   if col not in categorias + numericas + ['cnpj', 'nome', 'produtos'] 
                   and df[col].isna().sum() > 0.8 * len(df)]
    df = df.drop(columns=cols_to_drop)
    
    # Otimizar memória
    df = df.copy()  # Forçar realocação de memória otimizada
    
    return df

@st.cache_data(ttl=3600)
def calcular_analise_icp(df: pd.DataFrame, 
                        variaveis_categoricas: Tuple[str, ...],
                        variaveis_numericas: Tuple[str, ...]) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Função cacheada para cálculo de análise ICP
    """
    sistema = Sistema()
    sistema.carregar_dados(df)
    # return sistema.rodar_analise_icp(list(variaveis_categoricas), list(variaveis_numericas))

    # Chamar a análise ICP do sistema
    capitao, correlacoes_sistema = sistema.rodar_analise_icp(list(variaveis_categoricas), list(variaveis_numericas))

    # Construir o DataFrame 'todas' com a coluna 'variavel' explicitamente
    correlacoes_list = []

    # Processar correlações numéricas
    if 'numericas' in correlacoes_sistema and not correlacoes_sistema['numericas'].empty:
        matriz_corr = correlacoes_sistema['numericas']
        for var in matriz_corr.index:
             if var in variaveis_numericas: # Apenas variáveis de entrada, excluindo ltv/ticket_medio como variáveis
                correlacoes_list.append({
                    'variavel': var,
                    'correlacao_com_ltv': matriz_corr.loc[var, 'ltv'] if 'ltv' in matriz_corr.columns else None,
                    'correlacao_com_ticket': matriz_corr.loc[var, 'ticket_medio'] if 'ticket_medio' in matriz_corr.columns else None
                })

    # Processar correlações por categoria
    if 'categorias' in correlacoes_sistema:
        for cat, dados in correlacoes_sistema['categorias'].items():
            # Adicionar o valor específico da categoria, se disponível
            valor_ltv = dados['ltv'].get('melhor_categoria')
            valor_ticket = dados['ticket_medio'].get('melhor_categoria')
            
            correlacoes_list.append({
                'variavel': cat,
                'valor_ltv': valor_ltv, # Armazenar o valor_ltv
                'valor_ticket': valor_ticket, # Armazenar o valor_ticket
                'correlacao_com_ltv': dados['ltv'].get('diferenca_percentual', 0.0) / 100, # Usar get para evitar KeyError
                'correlacao_com_ticket': dados['ticket_medio'].get('diferenca_percentual', 0.0) / 100 # Usar get para evitar KeyError
            })

    # Criar o DataFrame 'todas'
    df_todas = pd.DataFrame(correlacoes_list)

    # Criar o dicionário de retorno
    correlacoes_retorno = {
        'todas': df_todas,
        'categorias': correlacoes_sistema.get('categorias', {}) # Incluir categorias originais se existirem
        # Adicionar outras chaves se a análise do sistema retornar mais coisas relevantes
    }

    return capitao, correlacoes_retorno

def calcular_segmentacao(df: pd.DataFrame, campo: str, tipo_segmentacao: str, percentuais=None) -> pd.DataFrame:
    """
    Calcula a segmentação dos clientes com base no campo e tipo de segmentação especificados.
    
    Args:
        df: DataFrame com os dados dos clientes
        campo: Campo base para segmentação (ltv ou ticket_medio)
        tipo_segmentacao: Tipo de segmentação ("80/20" ou "20/30/30/20")
        percentuais: Percentuais customizados para segmentação
            - Para 80/20: número único representando o percentual do grupo A
            - Para 20/30/30/20: lista com 4 percentuais [tier1, tier2, tier3, tier4]
    """
    # Garantir que o LTV existe se for o campo selecionado
    if campo == "ltv" and "ltv" not in df.columns:
        from .segmentacao import calcular_ltv
        df = calcular_ltv(df)
    
    sistema = Sistema()
    sistema.df = df
    
    if tipo_segmentacao == "80/20":
        # Se percentuais for fornecido, usa ele, senão usa 80
        percentual_a = percentuais if percentuais is not None else 80
        return sistema.rodar_segmentacao_por_valor(campo, percentual_a)
    else:
        # Se percentuais for fornecido, usa ele, senão usa [20, 30, 30, 20]
        percentuais = percentuais if percentuais is not None else [20, 30, 30, 20]
        return sistema.rodar_segmentacao_por_quantidade(campo, percentuais)

@st.cache_data(ttl=3600)
def get_variaveis_default() -> Tuple[Tuple[str, ...], Tuple[str, ...]]:
    """
    Retorna as variáveis padrão para análise ICP
    """
    return (
        ("porte", "dores", "localizacao", "segmento"),
        ("faturamento", "ticket_medio", "tempo_negociacao", "ltv")
    )

@st.cache_data(ttl=1800)  # Cache por 30 minutos
def calcular_correlacoes_batch(df: pd.DataFrame, 
                             variaveis_numericas: List[str],
                             variaveis_categoricas: List[str]) -> Dict[str, pd.DataFrame]:
    """
    Calcula todas as correlações de uma vez de forma otimizada
    """
    correlacoes = []
    
    # Correlações numéricas usando vetorização
    if variaveis_numericas:
        matriz_corr = df[variaveis_numericas + ['ltv', 'ticket_medio']].corr()
        for var in variaveis_numericas:
            correlacoes.append({
                'variavel': var,
                'correlacao_com_ltv': matriz_corr.loc[var, 'ltv'],
                'correlacao_com_ticket': matriz_corr.loc[var, 'ticket_medio']
            })
    
    # Correlações categóricas otimizadas
    for var in variaveis_categoricas:
        # Usar dummies para cálculo mais eficiente
        dummies = pd.get_dummies(df[var])
        corr_ltv = np.sqrt(
            ((dummies.T @ df['ltv']) ** 2).sum() / 
            (df['ltv'] ** 2).sum()
        )
        corr_ticket = np.sqrt(
            ((dummies.T @ df['ticket_medio']) ** 2).sum() / 
            (df['ticket_medio'] ** 2).sum()
        )
        correlacoes.append({
            'variavel': var,
            'correlacao_com_ltv': corr_ltv,
            'correlacao_com_ticket': corr_ticket
        })
    
    return pd.DataFrame(correlacoes)

@st.cache_data(ttl=3600)
def calcular_metricas_segmentacao(df: pd.DataFrame, 
                                campo: str,
                                tipo_segmentacao: str = "80/20") -> Tuple[pd.DataFrame, Dict]:
    """
    Calcula métricas de segmentação com cache otimizado
    """
    # Ordenar por valor
    df_sorted = df.sort_values(campo, ascending=False)
    
    if tipo_segmentacao == "80/20":
        # Cálculo Pareto
        df_sorted['valor_acumulado'] = df_sorted[campo].cumsum()
        df_sorted['percentual_acumulado'] = df_sorted['valor_acumulado'] / df_sorted[campo].sum()
        
        # Identificar ponto de corte 80%
        corte_80 = df_sorted[df_sorted['percentual_acumulado'] >= 0.8].index[0]
        df_sorted['tier'] = 'B'
        df_sorted.loc[:corte_80, 'tier'] = 'A'
    else:
        # Segmentação por quartis
        quartis = pd.qcut(df_sorted[campo], q=[0, 0.2, 0.5, 0.8, 1], labels=['D', 'C', 'B', 'A'])
        df_sorted['tier'] = quartis
    
    # Calcular métricas por tier
    metricas = df_sorted.groupby('tier').agg({
        campo: ['count', 'mean', 'sum', 'std']
    }).round(2)
    
    metricas.columns = ['Quantidade', 'Média', 'Total', 'Desvio Padrão']
    
    # Calcular estatísticas gerais
    stats = {
        'total_clientes': len(df),
        'valor_total': df[campo].sum(),
        'media_geral': df[campo].mean(),
        'mediana': df[campo].median(),
        'desvio_padrao': df[campo].std()
    }
    
    return metricas.reset_index(), stats

# Funções auxiliares otimizadas
def formatar_valor(valor: float) -> str:
    """Formata valor monetário de forma eficiente"""
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(valor)

def rankear_correlacao(valor: float) -> str:
    """Ranqueia correlação de forma eficiente"""
    abs_valor = abs(valor)
    if abs_valor >= 0.7: return "Muito Forte"
    if abs_valor >= 0.5: return "Forte"
    if abs_valor >= 0.3: return "Moderada"
    if abs_valor >= 0.1: return "Fraca"
    return "Muito Fraca" 