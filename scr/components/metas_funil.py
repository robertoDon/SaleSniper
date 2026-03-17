"""Módulo de Metas & Funil.

Baseado na lógica original, here we compute how many leads / meetings / etc.
are needed to reach a revenue or client goal, using the base taxas by segmento.
"""

from services.faixas_ticket import base_taxas, identificar_faixa, ajuste_por_faixa
from services.funil import calcular_funil, calcular_projecao


def get_metas_funil_data(segmento: str,
                         tipo_obj: str,
                         valor_obj: float,
                         ticket_medio: float,
                         n_vendedores: int) -> dict:
    """Retorna dados de metas e funil para a UI.

    Args:
        segmento: segmento selecionado (base_taxas)
        tipo_obj: 'Clientes', 'MRR' ou 'Faturamento'
        valor_obj: valor alvo (clientes ou receita)
        ticket_medio: ticket médio por cliente
        n_vendedores: número de vendedores (usado como orientação)
    """
    try:
        if ticket_medio <= 0:
            return {'error': 'Informe um Ticket Médio maior que zero.'}

        # Ajustar meta de clientes baseado no tipo de objetivo
        if tipo_obj == 'Clientes':
            meta_clientes = valor_obj
        elif tipo_obj == 'MRR':
            meta_clientes = valor_obj / ticket_medio
        else:  # Faturamento anual
            meta_clientes = (valor_obj / 12) / ticket_medio

        meta_clientes = max(meta_clientes, 0)

        # Ajustar taxas conforme segmento + faixa de ticket
        taxas_base = base_taxas.get(segmento, base_taxas.get('Software por Recorrência'))
        faixa = identificar_faixa(segmento, ticket_medio)
        ajuste = ajuste_por_faixa.get(faixa, 1.0)

        taxas_ajustadas = calcular_funil(taxas_base, ajuste)

        etapas = list(taxas_ajustadas.keys()) + ['Venda']
        proj = calcular_projecao(etapas, taxas_ajustadas, meta_clientes)

        # Para exibir com formatação básica
        proj_formatada = {k: (round(v, 2) if isinstance(v, (int, float)) else v) for k, v in proj.items()}

        return {
            'segmento': segmento,
            'tipo_obj': tipo_obj,
            'valor_obj': valor_obj,
            'ticket_medio': ticket_medio,
            'n_vendedores': n_vendedores,
            'faixa': faixa,
            'ajuste': ajuste,
            'taxas_ajustadas': taxas_ajustadas,
            'projecao': proj_formatada,
            'meta_clientes': round(meta_clientes, 2)
        }

    except Exception as e:
        return {'error': f'Erro ao calcular metas e funil: {e}'}
