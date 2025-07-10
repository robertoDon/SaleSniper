def calcular_funil(base_taxas: dict, ajuste: float) -> dict:
    return {etapa: round(valor * ajuste, 3) for etapa, valor in base_taxas.items()}


def calcular_projecao(etapas: list, taxas: dict, meta_final: float) -> dict:
    proj = {"Venda": meta_final}
    for etapa in reversed(etapas[:-1]):
        etapa_seguinte = etapas[etapas.index(etapa) + 1]
        taxa = taxas.get(etapa, 0.0)
        if taxa > 0:
            proj[etapa] = proj[etapa_seguinte] / taxa
        else:
            proj[etapa] = 0
    return proj
