base_taxas = {
    "Software por Recorrência": {
        "Lead": 0.5, "MQL": 0.6, "SAL": 0.65,
        "Agendamento": 0.75, "Reunião Ocorrida": 0.65, "Oportunidade (SQL)": 0.4
    },
    "Software por Licença": {
        "Lead": 0.45, "MQL": 0.55, "SAL": 0.6,
        "Agendamento": 0.7, "Reunião Ocorrida": 0.6, "Oportunidade (SQL)": 0.35
    },
    "Serviço": {
        "Lead": 0.6, "MQL": 0.65, "SAL": 0.7,
        "Agendamento": 0.8, "Reunião Ocorrida": 0.7, "Oportunidade (SQL)": 0.5
    },
    "Hardware": {
        "Lead": 0.4, "MQL": 0.5, "SAL": 0.6,
        "Agendamento": 0.65, "Reunião Ocorrida": 0.55, "Oportunidade (SQL)": 0.3
    },
    "Indústria": {
        "Lead": 0.35, "MQL": 0.45, "SAL": 0.55,
        "Agendamento": 0.6, "Reunião Ocorrida": 0.5, "Oportunidade (SQL)": 0.25
    }
}

faixas_ticket = {
    "Software por Recorrência": {
        "baixa": (0, 200),
        "media": (201, 10000),
        "alta": (10001, float("inf"))
    },
    "Software por Licença": {
        "baixa": (0, 100),
        "media": (101, 1000000),
        "alta": (1000001, float("inf"))
    },
    "Serviço": {
        "baixa": (0, 200),
        "media": (201, 10000000),
        "alta": (10000001, float("inf"))
    },
    "Hardware": {
        "baixa": (0, 200),
        "media": (201, 500000),
        "alta": (500001, float("inf"))
    },
    "Indústria": {
        "baixa": (0, 500),
        "media": (501, 1000000),
        "alta": (1000001, float("inf"))
    }
}

ajuste_por_faixa = {
    "baixa": 1.0,
    "media": 0.8,
    "alta": 0.6
}

def identificar_faixa(segmento: str, ticket: float) -> str:
    if segmento not in faixas_ticket:
        return "media"
    for faixa, (min_val, max_val) in faixas_ticket[segmento].items():
        if min_val <= ticket <= max_val:
            return faixa
    return "media"
