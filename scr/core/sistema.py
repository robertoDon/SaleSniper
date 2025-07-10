import pandas as pd
from domain.servicos.analise_icp import AnaliseICP
from domain.servicos.segmentacao import Segmentacao
from domain.servicos.dados_mercado import DadosMercado

class Sistema:
    def __init__(self):
        self.df = None
        self.df_mercado = None
        self.analise_icp = AnaliseICP()
        self.segmentador = Segmentacao()
        self.dados_mercado = None

    def carregar_dados(self, df: pd.DataFrame):
        self.df = df

    def rodar_analise_icp(self, qualitativos, quantitativos):
        return self.analise_icp.calcular_capitao_america(self.df, qualitativos), \
               self.analise_icp.calcular_correlacoes(self.df, qualitativos, quantitativos)

    def rodar_segmentacao_por_valor(self, campo: str, percentual_a: float = 20) -> pd.DataFrame:
        """
        Roda a segmentação por valor acumulado.
        
        Args:
            campo: Campo base para segmentação (ltv ou ticket_medio)
            percentual_a: Percentual do valor total que o Grupo A deve representar (default: 20)
        """
        return self.segmentador.aplicar_segmentacao_8020(self.df, campo, percentual_a)
        
    def rodar_segmentacao_por_quantidade(self, campo: str, percentuais: list = [20, 30, 30, 20]) -> pd.DataFrame:
        """
        Roda a segmentação por quantidade de clientes.
        
        Args:
            campo: Campo base para segmentação (ltv ou ticket_medio)
            percentuais: Lista com 4 percentuais [tier1, tier2, tier3, tier4] (default: [20, 30, 30, 20])
        """
        return self.segmentador.aplicar_segmentacao_20_30_30_20(self.df, campo, percentuais)

    def configurar_api_mercado(self, api_key: str):
        self.dados_mercado = DadosMercado(api_key)

    def carregar_dados_mercado(self, filtros: dict):
        self.df_mercado = self.dados_mercado.carregar_dados_econodata(filtros)

    def cruzar_com_clientes(self):
        self.df_mercado = self.dados_mercado.cruzar_dados_mercado(self.df_mercado, self.df)

    def aplicar_segmentacao_mercado(self, campo: str):
        self.df_mercado = self.dados_mercado.aplicar_segmentacao_20_30_30_20(self.df_mercado, campo)

    def gerar_matriz_tam_sam_som(self) -> pd.DataFrame:
        return self.dados_mercado.gerar_matriz_tam_sam_som(self.df_mercado)

    def gerar_resumo_tam_sam_som(self) -> pd.DataFrame:
        return self.dados_mercado.gerar_resumo_tam_sam_som(self.df_mercado)
