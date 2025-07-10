# domain/servicos/tam_sam_som.py
import pandas as pd

def cruzar_dados_mercado(df_clientes: pd.DataFrame, df_mercado: pd.DataFrame) -> pd.DataFrame:
    df_mercado['é_cliente'] = df_mercado['cnpj'].isin(df_clientes['cnpj'])
    return df_mercado

def aplicar_segmentacao_20_30_30_20(df: pd.DataFrame, campo: str) -> pd.DataFrame:
    df = df.sort_values(by=campo, ascending=False)
    df['acumulado'] = df[campo].cumsum()
    total = df[campo].sum()
    df['percentual'] = df['acumulado'] / total

    def classificar(p):
        if p <= 0.2:
            return 'Tier 1'
        elif p <= 0.5:
            return 'Tier 2'
        elif p <= 0.8:
            return 'Tier 3'
        else:
            return 'Tier 4'

    df['Tier'] = df['percentual'].apply(classificar)
    return df

def gerar_matriz_tam_sam_som(df: pd.DataFrame, grupo_por: list) -> pd.DataFrame:
    matriz = df.groupby(grupo_por).agg(
        TAM=('cnpj', 'count'),
        SAM=('é_cliente', lambda x: x.count()),
        SOM=('é_cliente', lambda x: x.sum()),
        Tier1=('Tier', lambda x: (x == 'Tier 1').sum()),
        Tier2=('Tier', lambda x: (x == 'Tier 2').sum()),
        Tier3=('Tier', lambda x: (x == 'Tier 3').sum()),
        Tier4=('Tier', lambda x: (x == 'Tier 4').sum()),
    ).reset_index()
    return matriz
