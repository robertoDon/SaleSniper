import pandas as pd

from domain.servicos.dados_mercado import DadosMercado


def get_tamsamsom_data() -> dict:
    """Gera uma tabela de TAM/SAM/SOM usando dados de exemplo ou da Receita Federal."""
    try:
        dados_mercado = DadosMercado()
        # Carrega dados de exemplo (perfeito para demonstração sem grandes arquivos)
        df_mercado = dados_mercado._gerar_dados_exemplo()

        # Para fins de demonstração, consideramos os primeiros clientes como nossa base de clientes
        df_clientes = df_mercado.head(50).copy()

        matriz = dados_mercado.calcular_tam_sam_som_por_cnae(df_clientes, df_mercado)

        # Organizar para exibição (limitado aos primeiros 100 registros)
        matriz_display = matriz.copy().head(100)
        return {
            "summary": {
                "total_TAM": int(matriz['TAM'].sum()),
                "total_SAM": int(matriz['SAM'].sum()),
                "total_SOM": int(matriz['SOM'].sum()),
            },
            "table_columns": list(matriz_display.columns),
            "table_rows": matriz_display.to_dict(orient="records"),
        }
    except Exception as e:
        return {"error": f"Erro ao calcular TAM/SAM/SOM: {e}"}
