import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class ValuationService:
    """Serviço para cálculos de valuation empresarial."""
    
    def __init__(self):
        # Múltiplos de mercado por setor e estágio
        self.multiplos_mercado = {
            "SaaS": {
                "startup": {"receita": 8.0, "ebitda": 15.0, "lucro": 25.0},
                "scaleup": {"receita": 6.0, "ebitda": 12.0, "lucro": 20.0},
                "estabelecida": {"receita": 4.0, "ebitda": 8.0, "lucro": 15.0}
            },
            "E-commerce": {
                "startup": {"receita": 2.5, "ebitda": 12.0, "lucro": 18.0},
                "scaleup": {"receita": 2.0, "ebitda": 10.0, "lucro": 15.0},
                "estabelecida": {"receita": 1.5, "ebitda": 8.0, "lucro": 12.0}
            },
            "Fintech": {
                "startup": {"receita": 6.0, "ebitda": 18.0, "lucro": 30.0},
                "scaleup": {"receita": 5.0, "ebitda": 15.0, "lucro": 25.0},
                "estabelecida": {"receita": 3.5, "ebitda": 12.0, "lucro": 20.0}
            },
            "Healthtech": {
                "startup": {"receita": 7.0, "ebitda": 20.0, "lucro": 35.0},
                "scaleup": {"receita": 6.0, "ebitda": 18.0, "lucro": 30.0},
                "estabelecida": {"receita": 4.5, "ebitda": 15.0, "lucro": 25.0}
            },
            "Edtech": {
                "startup": {"receita": 5.0, "ebitda": 15.0, "lucro": 25.0},
                "scaleup": {"receita": 4.0, "ebitda": 12.0, "lucro": 20.0},
                "estabelecida": {"receita": 3.0, "ebitda": 10.0, "lucro": 16.0}
            },
            "Consultoria": {
                "startup": {"receita": 3.0, "ebitda": 10.0, "lucro": 15.0},
                "scaleup": {"receita": 2.5, "ebitda": 8.0, "lucro": 12.0},
                "estabelecida": {"receita": 2.0, "ebitda": 6.0, "lucro": 10.0}
            },
            "Outros": {
                "startup": {"receita": 4.0, "ebitda": 12.0, "lucro": 20.0},
                "scaleup": {"receita": 3.0, "ebitda": 10.0, "lucro": 16.0},
                "estabelecida": {"receita": 2.5, "ebitda": 8.0, "lucro": 12.0}
            }
        }
        
        # Pesos para valuation médio ponderado por estágio
        self.pesos_estagio = {
            "startup": [0.2, 0.3, 0.3, 0.2],      # Berkus e DCF mais relevantes
            "scaleup": [0.4, 0.4, 0.1, 0.1],      # Múltiplos e DCF mais relevantes
            "estabelecida": [0.5, 0.4, 0.05, 0.05] # Múltiplos mais relevantes
        }
    
    def calcular_ebitda(self, receita_anual: float, custos_vendas: float, despesas_operacionais: float, 
                       despesas_adm: float, despesas_marketing: float, outros_custos: float = 0) -> float:
        """Calcula o EBITDA baseado nos componentes."""
        ebitda = receita_anual - custos_vendas - despesas_operacionais - despesas_adm - despesas_marketing - outros_custos
        return max(ebitda, 0)  # EBITDA não pode ser negativo
    
    def calcular_multiplos(self, receita_anual: float, ebitda: float, lucro_liquido: float, 
                          setor: str, tamanho_empresa: str) -> Dict:
        """Calcula valuation usando múltiplos de mercado."""
        
        # Obter múltiplos para o setor e tamanho
        multiplos = self.multiplos_mercado.get(setor, self.multiplos_mercado["Outros"])
        mult = multiplos.get(tamanho_empresa, multiplos["startup"])
        
        # Calcular valuations
        valuation_receita = receita_anual * mult["receita"]
        valuation_ebitda = ebitda * mult["ebitda"] if ebitda > 0 else 0
        valuation_lucro = lucro_liquido * mult["lucro"] if lucro_liquido > 0 else 0
        
        return {
            "receita": valuation_receita,
            "ebitda": valuation_ebitda,
            "lucro": valuation_lucro,
            "multiplos": mult,
            "detalhamento": {
                "receita_anual": receita_anual,
                "ebitda": ebitda,
                "lucro_liquido": lucro_liquido
            }
        }
    
    def calcular_dcf(self, receita_anual: float, margem_ebitda: float, crescimento_anual: float,
                    anos_projecao: int = 5, taxa_desconto: float = 0.15) -> Dict:
        """Calcula valuation usando Discounted Cash Flow (DCF)."""
        
        # Projeção de receita com crescimento decrescente
        receitas_projetadas = []
        for ano in range(anos_projecao):
            if ano == 0:
                receitas_projetadas.append(receita_anual)
            else:
                crescimento_ano = crescimento_anual * (0.9 ** ano)
                receitas_projetadas.append(receitas_projetadas[-1] * (1 + crescimento_ano))
        
        # Projeção de EBITDA
        ebitda_projetado = [receita * margem_ebitda for receita in receitas_projetadas]
        
        # Fluxo de caixa livre (assumindo 30% de reinvestimento)
        fcf_projetado = [ebitda * 0.7 for ebitda in ebitda_projetado]
        
        # Valor presente dos fluxos
        vp_fcf = []
        for i, fcf in enumerate(fcf_projetado):
            vp = fcf / ((1 + taxa_desconto) ** (i + 1))
            vp_fcf.append(vp)
        
        # Valor terminal (perpetuidade)
        crescimento_terminal = 0.03  # 3% ao ano
        fcf_terminal = fcf_projetado[-1] * (1 + crescimento_terminal)
        valor_terminal = fcf_terminal / (taxa_desconto - crescimento_terminal)
        vp_terminal = valor_terminal / ((1 + taxa_desconto) ** anos_projecao)
        
        # Valor total da empresa
        valor_empresa = sum(vp_fcf) + vp_terminal
        
        return {
            "valor_empresa": valor_empresa,
            "receitas_projetadas": receitas_projetadas,
            "ebitda_projetado": ebitda_projetado,
            "fcf_projetado": fcf_projetado,
            "vp_fcf": vp_fcf,
            "valor_terminal": valor_terminal,
            "vp_terminal": vp_terminal,
            "taxa_desconto": taxa_desconto,
            "anos_projecao": anos_projecao
        }
    
    def calcular_berkus(self, receita_anual: float, produto_lancado: bool,
                       parcerias_estrategicas: bool, vendas_organicas: bool, 
                       investe_trafego_pago: bool) -> Dict:
        """Calcula valuation usando o método Berkus (para startups)."""
        
        valor_base = 0
        fatores_berkus = []
        
        # Critérios Berkus (cada um vale $500k)
        if produto_lancado:
            valor_base += 500000
            fatores_berkus.append({"fator": "Produto Lançado", "valor": 500000})
        
        if vendas_organicas:
            valor_base += 500000
            fatores_berkus.append({"fator": "Vendas Orgânicas", "valor": 500000})
        
        if parcerias_estrategicas:
            valor_base += 500000
            fatores_berkus.append({"fator": "Parcerias Estratégicas", "valor": 500000})
        
        if investe_trafego_pago:
            valor_base += 500000
            fatores_berkus.append({"fator": "Investe em Tráfego Pago", "valor": 500000})
        
        # Ajuste por receita (máximo de $2M)
        if receita_anual > 0:
            valor_receita = min(receita_anual * 2, 2000000)
            valor_base += valor_receita
            fatores_berkus.append({"fator": "Receita (2x)", "valor": valor_receita})
        
        return {
            "valor_total": valor_base,
            "fatores": fatores_berkus
        }
    
    def calcular_scorecard(self, receita_anual: float, setor: str, tamanho_mercado: float,
                          equipe: float, produto: float, vendas_marketing: float,
                          financas: float, competicao: float, timing: float,
                          inovacao: float = 1.0, channels: float = 1.0) -> Dict:
        """Calcula valuation usando o método Scorecard."""
        
        # Valor médio de startups similares (ajustado para mercado brasileiro)
        valor_medio = 2000000  # R$ 2M
        
        # Fatores de ajuste
        fatores = {
            "Força da Equipe": equipe,
            "Tamanho da Oportunidade": tamanho_mercado,
            "Qualidade do Produto": produto,
            "Estratégia de Vendas/Marketing": vendas_marketing,
            "Saúde Financeira": financas,
            "Competição": competicao,
            "Timing de Mercado": timing,
            "Inovação": inovacao,
            "Canais de Distribuição": channels
        }
        
        # Calcular valor
        valor = valor_medio
        for fator, peso in fatores.items():
            valor *= peso
        
        # Ajuste por receita
        valor_receita = 0
        if receita_anual > 0:
            valor_receita = receita_anual * 3  # 3x receita
            valor = max(valor, valor_receita)
        
        return {
            "valor_total": valor,
            "valor_medio_base": valor_medio,
            "fatores": fatores,
            "valor_receita": valor_receita,
            "receita_anual": receita_anual
        }
    
    def calcular_valuation_medio(self, resultados: Dict, tamanho_empresa: str) -> float:
        """Calcula o valuation médio ponderado baseado no estágio da empresa."""
        
        valuations = [
            resultados["multiplos"]["receita"],
            resultados["dcf"]["valor_empresa"],
            resultados["berkus"]["valor_total"],
            resultados["scorecard"]["valor_total"]
        ]
        
        pesos = self.pesos_estagio.get(tamanho_empresa, self.pesos_estagio["startup"])
        valuation_medio = sum(v * p for v, p in zip(valuations, pesos))
        
        return valuation_medio
    
    def gerar_relatorio_completo(self, dados_empresa: Dict) -> Dict:
        """Gera relatório completo de valuation."""
        
        # Calcular todos os métodos
        mult_result = self.calcular_multiplos(
            dados_empresa["receita_anual"],
            dados_empresa["ebitda"],
            dados_empresa["lucro_liquido"],
            dados_empresa["setor"],
            dados_empresa["tamanho_empresa"]
        )
        
        dcf_result = self.calcular_dcf(
            dados_empresa["receita_anual"],
            dados_empresa["margem_ebitda"],
            dados_empresa["crescimento_anual"]
        )
        
        berkus_result = self.calcular_berkus(
            dados_empresa["receita_anual"],
            dados_empresa["produto_lancado"],
            dados_empresa["parcerias_estrategicas"],
            dados_empresa["vendas_organicas"],
            dados_empresa["investe_trafego_pago"]
        )
        
        scorecard_result = self.calcular_scorecard(
            dados_empresa["receita_anual"],
            dados_empresa["setor"],
            dados_empresa["tamanho_mercado"],
            dados_empresa["equipe"],
            dados_empresa["produto"],
            dados_empresa["vendas_marketing"],
            dados_empresa["financas"],
            dados_empresa["competicao"],
            dados_empresa["timing"],
            dados_empresa.get("inovacao", 1.0),
            dados_empresa.get("channels", 1.0)
        )
        
        # Calcular valuation médio
        resultados = {
            "multiplos": mult_result,
            "dcf": dcf_result,
            "berkus": berkus_result,
            "scorecard": scorecard_result
        }
        
        valuation_medio = self.calcular_valuation_medio(resultados, dados_empresa["tamanho_empresa"])
        
        return {
            "empresa": dados_empresa["nome_empresa"],
            "data_calculo": pd.Timestamp.now(),
            "dados_empresa": dados_empresa,
            "resultados": resultados,
            "valuation_medio": valuation_medio,
            "pesos_utilizados": self.pesos_estagio[dados_empresa["tamanho_empresa"]]
        }
    
    def exportar_para_dataframe(self, relatorio: Dict) -> pd.DataFrame:
        """Converte relatório para DataFrame para exportação."""
        
        resultados = relatorio["resultados"]
        
        df = pd.DataFrame({
            "Método": ["Múltiplos", "DCF", "Berkus", "Scorecard", "Médio Ponderado"],
            "Valuation (R$)": [
                resultados["multiplos"]["receita"],
                resultados["dcf"]["valor_empresa"],
                resultados["berkus"]["valor_total"],
                resultados["scorecard"]["valor_total"],
                relatorio["valuation_medio"]
            ],
            "Peso": relatorio["pesos_utilizados"] + [1.0]
        })
        
        df["Valuation (R$ M)"] = df["Valuation (R$)"] / 1000000
        
        return df 