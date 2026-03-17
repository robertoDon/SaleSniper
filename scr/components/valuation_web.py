import pandas as pd
from typing import Dict

from services.valuation_service import ValuationService


def get_valuation_data(form) -> Dict:
    """Gera os dados de valuation a partir do formulário recebido."""

    try:
        def _parse_float(key, default=0.0):
            val = form.get(key, "")
            if val is None:
                return default
            if isinstance(val, (int, float)):
                return float(val)
            val = str(val).replace(",", ".").strip()
            if val == "":
                return default
            try:
                return float(val)
            except ValueError:
                return default

        def _parse_bool(key):
            return form.get(key) in ("on", "true", "True", "1")

        def _parse_score(key):
            v = _parse_float(key, 1.0)
            return v if v > 0 else 1.0

        nome_empresa = form.get("nome_empresa", "").strip() or "Minha Empresa"
        setor = form.get("setor", "Outros")
        tamanho_empresa = form.get("tamanho_empresa", "operacao")

        receita_anual = _parse_float("receita_anual", 0.0)
        ebitda = _parse_float("ebitda", 0.0)
        lucro_liquido = _parse_float("lucro_liquido", 0.0)
        margem_ebitda = _parse_float("margem_ebitda", 0.0) / 100.0
        crescimento_anual = _parse_float("crescimento_anual", 0.0) / 100.0

        dados_empresa = {
            "nome_empresa": nome_empresa,
            "setor": setor,
            "tamanho_empresa": tamanho_empresa,
            "receita_anual": receita_anual,
            "ebitda": ebitda,
            "lucro_liquido": lucro_liquido,
            "margem_ebitda": margem_ebitda,
            "crescimento_anual": crescimento_anual,
            "produto_lancado": _parse_bool("produto_lancado"),
            "parcerias_estrategicas": _parse_bool("parcerias_estrategicas"),
            "vendas_organicas": _parse_bool("vendas_organicas"),
            "investe_trafego_pago": _parse_bool("investe_trafego_pago"),
            "equipe": _parse_score("equipe"),
            "produto": _parse_score("produto"),
            "vendas_marketing": _parse_score("vendas_marketing"),
            "financas": _parse_score("financas"),
            "concorrencia": _parse_score("concorrencia"),
            "inovacao": _parse_score("inovacao"),
        }

        service = ValuationService()
        relatorio = service.gerar_relatorio_completo(dados_empresa)
        df = service.exportar_para_dataframe(relatorio)

        return {
            "empresa": nome_empresa,
            "valuation_medio": relatorio.get("valuation_medio"),
            "table_columns": list(df.columns),
            "table_rows": df.to_dict(orient="records"),
            "relatorio": relatorio,
        }
    except Exception as e:
        return {"error": f"Erro ao calcular valuation: {e}"}
