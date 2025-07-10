import pandas as pd

class Segmentacao:
    def aplicar_segmentacao_8020(self, df: pd.DataFrame, campo: str, percentual_a: float = 20) -> pd.DataFrame:
        """
        Segmenta os clientes com base na contribuição acumulada do campo (ex: ltv).
        Clientes que somam o percentual especificado do valor total entram no grupo A, os demais no grupo B.
        
        Args:
            df: DataFrame com os dados dos clientes
            campo: Campo base para segmentação (ltv ou ticket_medio)
            percentual_a: Percentual do valor total que o Grupo A deve representar (default: 20)
        """
        df = df.copy()
        df = df.sort_values(by=campo, ascending=False).reset_index(drop=True)
        total = df[campo].sum()
        acumulado = df[campo].cumsum()
        df["acumulado_pct"] = acumulado / total

        df["tier"] = df["acumulado_pct"].apply(lambda x: "A" if x <= percentual_a/100 else "B")
        return df.drop(columns=["acumulado_pct"])

    def aplicar_segmentacao_20_30_30_20(self, df: pd.DataFrame, campo: str, percentuais: list = [20, 30, 30, 20]) -> pd.DataFrame:
        """
        Segmenta os clientes em Tier 1, Tier 2, Tier 3 e Tier 4 com base na ordem decrescente do campo
        e nos percentuais especificados.
        
        Args:
            df: DataFrame com os dados dos clientes
            campo: Campo base para segmentação (ltv ou ticket_medio)
            percentuais: Lista com 4 percentuais [tier1, tier2, tier3, tier4] (default: [20, 30, 30, 20])
        """
        df = df.copy()
        df = df.sort_values(by=campo, ascending=False).reset_index(drop=True)
        total = len(df)
        
        # Calcula os limites baseado nos percentuais
        limites = [
            int(percentuais[0]/100 * total),
            int((percentuais[0] + percentuais[1])/100 * total),
            int((percentuais[0] + percentuais[1] + percentuais[2])/100 * total),
            total
        ]
        
        tiers = []
        for i in range(total):
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
