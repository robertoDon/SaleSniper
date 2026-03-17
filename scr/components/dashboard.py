import pandas as pd
from adapters.importador import carregar_clientes_do_excel
from core.sistema import Sistema
from components.utils import (
    carregar_e_preprocessar_dados, 
    calcular_analise_icp,
    get_variaveis_default,
    formatar_valor
)
from services.ai_insights import gerar_insights_ia, gerar_insights_e_acoes_por_categoria, gerar_acao_sugerida_para_insight
import locale
from typing import Dict, List

# Configurar locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # Usa o padrão do sistema

def formatar_numero_br(valor, casas_decimais=2):
    """Formata número para o padrão brasileiro."""
    if isinstance(valor, (int, float)):
        return f"{valor:,.{casas_decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor

def _formatar_perfil_capitao(perfil: dict) -> dict:
    """Formata os valores do perfil Capitão América de forma otimizada."""
    perfil_formatado = {}
    
    for campo, valor in perfil.items():
        if isinstance(valor, dict):
            if 'media' in valor:
                # Formatação para métricas numéricas
                if campo in ['ticket_medio', 'ltv']:
                    # Valores monetários
                    perfil_formatado[campo] = {
                        'media': f"R$ {formatar_numero_br(valor['media'])}",
                        'mediana': f"R$ {formatar_numero_br(valor['mediana'])}",
                        'min': f"R$ {formatar_numero_br(valor['min'])}",
                        'max': f"R$ {formatar_numero_br(valor['max'])}"
                    }
                else:
                    # Valores numéricos não monetários
                    perfil_formatado[campo] = {
                        'media': formatar_numero_br(valor['media'], 1),
                        'mediana': formatar_numero_br(valor['mediana'], 1),
                        'min': formatar_numero_br(valor['min'], 1),
                        'max': formatar_numero_br(valor['max'], 1)
                    }
            elif 'moda' in valor:
                # Formatação para métricas categóricas
                distribuicao_formatada = {
                    k: f"{formatar_numero_br(v, 1)}%" for k, v in valor['distribuicao'].items()
                }
                perfil_formatado[campo] = {
                    'moda': valor['moda'],
                    'distribuicao': distribuicao_formatada
                }
        else:
            perfil_formatado[campo] = valor
            
    return perfil_formatado

def _exibir_metricas_financeiras(perfil: dict):
    """Exibe as métricas financeiras em colunas."""
    col1, col2 = st.columns(2)
    with col1:
        ticket_medio = perfil.get('ticket_medio', {})
        if isinstance(ticket_medio, dict) and 'media' in ticket_medio:
            st.metric("Ticket Médio", ticket_medio['media'])
        else:
            st.metric("Ticket Médio", "N/A")
    with col2:
        ltv = perfil.get('ltv', {})
        if isinstance(ltv, dict) and 'media' in ltv:
            st.metric("LTV", ltv['media'])
        else:
            st.metric("LTV", "N/A")

def _processar_correlacoes(correlacoes: dict) -> tuple:
    """Processa correlações para exibição otimizada."""
    insights = []
    
    # Processando correlações por categoria
    for categoria, dados in correlacoes['categorias'].items():
        # Análise de Ticket Médio
        ticket = dados['ticket_medio']
        insights.append({
            'tipo': 'ticket_medio',
            'variavel': categoria,
            'insight': f"**{categoria.title()}**: {ticket['melhor_categoria']} tem ticket médio {ticket['diferenca_percentual']:.1f}% maior que {ticket['pior_categoria']}"
        })
        
        # Análise de LTV
        ltv = dados['ltv']
        insights.append({
            'tipo': 'ltv',
            'variavel': categoria,
            'insight': f"**{categoria.title()}**: {ltv['melhor_categoria']} tem LTV {ltv['diferenca_percentual']:.1f}% maior que {ltv['pior_categoria']}"
        })
    
    return insights

def get_dashboard_data():
    return {'message': 'Dashboard data placeholder'}
