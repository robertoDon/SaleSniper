import os
import pandas as pd
import requests

class DadosMercado:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.econodata.com.br/v1/empresas"  # Exemplo real

    def carregar_dados_econodata(self, params: dict) -> pd.DataFrame:
        import os
        caminho_mock = os.path.join(os.path.dirname(__file__), "mock_mercado.csv")
        df = pd.read_csv(caminho_mock)

        # Padroniza todos os nomes de coluna
        df.columns = df.columns.str.strip().str.lower()

        if "cnpj" not in df.columns:
            raise ValueError("Arquivo de mercado não possui coluna 'cnpj' após normalização.")

        return df

    def cruzar_dados_mercado(self, df_mercado: pd.DataFrame, df_clientes: pd.DataFrame) -> pd.DataFrame:
        df_mercado["é_cliente"] = df_mercado["cnpj"].isin(df_clientes["cnpj"])
        return df_mercado

    def aplicar_segmentacao_20_30_30_20(self, df: pd.DataFrame, campo: str) -> pd.DataFrame:
        df = df.sort_values(by=campo, ascending=False).copy()
        total = len(df)
        limites = [
            int(0.2 * total),
            int(0.5 * total),
            int(0.8 * total),
            total
        ]
        tiers = []
        for i, idx in enumerate(df.index):
            if i < limites[0]:
                tiers.append("Tier 1")
            elif i < limites[1]:
                tiers.append("Tier 2")
            elif i < limites[2]:
                tiers.append("Tier 3")
            else:
                tiers.append("Tier 4")
        df["tier"] = tiers
        return df

    def gerar_matriz_tam_sam_som(self, df: pd.DataFrame, agrupadores=["regiao", "cnae"]) -> pd.DataFrame:
        matriz = df.groupby(agrupadores).agg(
            TAM=("cnpj", "count"),
            SAM=("é_cliente", lambda x: (~x).sum()),
            SOM=("é_cliente", "sum"),
            Tier_1=("tier", lambda x: (x == "Tier 1").sum()),
            Tier_2=("tier", lambda x: (x == "Tier 2").sum()),
            Tier_3=("tier", lambda x: (x == "Tier 3").sum()),
            Tier_4=("tier", lambda x: (x == "Tier 4").sum())
        ).reset_index()
        return matriz
    
    def gerar_resumo_tam_sam_som(self, df: pd.DataFrame) -> pd.DataFrame:
        if "tier" not in df.columns or "é_cliente" not in df.columns:
            raise ValueError("DataFrame precisa conter colunas 'tier' e 'é_cliente'.")

        df["é_potencial"] = ~df["é_cliente"]

        resultado = {
            "TAM": df.groupby("tier")["cnpj"].count(),
            "SAM": df[df["é_potencial"]].groupby("tier")["cnpj"].count(),
            "SOM": df[df["é_cliente"]].groupby("tier")["cnpj"].count(),
        }

        matriz = pd.DataFrame(resultado).T.fillna(0).astype(int)
        return matriz

    def sugerir_cnaes_semelhantes(self, df_clientes: pd.DataFrame, df_mercado: pd.DataFrame) -> pd.DataFrame:
        """
        Sugere CNAEs semelhantes (3 dígitos) presentes no mercado, mas não na base de clientes.
        Retorna DataFrame com CNAE, quantidade de empresas e região.
        """
        # Extrai os 3 primeiros dígitos dos CNAEs dos clientes
        cnaes_clientes = df_clientes['cnae'].astype(str).str[:3].unique()
        # Extrai os 3 primeiros dígitos dos CNAEs do mercado
        df_mercado['cnae3'] = df_mercado['cnae'].astype(str).str[:3]
        # Filtra CNAEs do mercado que não estão nos clientes
        df_novos = df_mercado[~df_mercado['cnae3'].isin(cnaes_clientes)]
        # Agrupa por CNAE3 e região
        oportunidades = df_novos.groupby(['cnae3', 'regiao']).agg(qtd_empresas=('cnpj', 'count')).reset_index()
        oportunidades = oportunidades.sort_values('qtd_empresas', ascending=False)
        return oportunidades

