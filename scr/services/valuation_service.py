import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class ValuationService:
    """Serviço para cálculos de valuation empresarial."""
    
    def __init__(self):
        # Múltiplos de mercado por setor e estágio (baseados em dados de mercado)
        self.multiplos_mercado = {
            "SaaS": {
                "seed": {"receita": 12.0, "ebitda": 20.0, "lucro": 35.0},
                "startup": {"receita": 8.0, "ebitda": 15.0, "lucro": 25.0},
                "scaleup": {"receita": 6.0, "ebitda": 12.0, "lucro": 20.0},
                "estabelecida": {"receita": 4.0, "ebitda": 8.0, "lucro": 15.0}
            },
            "E-commerce": {
                "seed": {"receita": 4.0, "ebitda": 15.0, "lucro": 25.0},
                "startup": {"receita": 2.5, "ebitda": 12.0, "lucro": 18.0},
                "scaleup": {"receita": 2.0, "ebitda": 10.0, "lucro": 15.0},
                "estabelecida": {"receita": 1.5, "ebitda": 8.0, "lucro": 12.0}
            },
            "Fintech": {
                "seed": {"receita": 10.0, "ebitda": 25.0, "lucro": 40.0},
                "startup": {"receita": 6.0, "ebitda": 18.0, "lucro": 30.0},
                "scaleup": {"receita": 5.0, "ebitda": 15.0, "lucro": 25.0},
                "estabelecida": {"receita": 3.5, "ebitda": 12.0, "lucro": 20.0}
            },
            "Healthtech": {
                "seed": {"receita": 12.0, "ebitda": 30.0, "lucro": 50.0},
                "startup": {"receita": 7.0, "ebitda": 20.0, "lucro": 35.0},
                "scaleup": {"receita": 6.0, "ebitda": 18.0, "lucro": 30.0},
                "estabelecida": {"receita": 4.5, "ebitda": 15.0, "lucro": 25.0}
            },
            "Edtech": {
                "seed": {"receita": 8.0, "ebitda": 20.0, "lucro": 35.0},
                "startup": {"receita": 5.0, "ebitda": 15.0, "lucro": 25.0},
                "scaleup": {"receita": 4.0, "ebitda": 12.0, "lucro": 20.0},
                "estabelecida": {"receita": 3.0, "ebitda": 10.0, "lucro": 16.0}
            },
            "Consultoria": {
                "seed": {"receita": 5.0, "ebitda": 15.0, "lucro": 25.0},
                "startup": {"receita": 3.0, "ebitda": 10.0, "lucro": 15.0},
                "scaleup": {"receita": 2.5, "ebitda": 8.0, "lucro": 12.0},
                "estabelecida": {"receita": 2.0, "ebitda": 6.0, "lucro": 10.0}
            },
            "Outros": {
                "seed": {"receita": 6.0, "ebitda": 18.0, "lucro": 30.0},
                "startup": {"receita": 4.0, "ebitda": 12.0, "lucro": 20.0},
                "scaleup": {"receita": 3.0, "ebitda": 10.0, "lucro": 16.0},
                "estabelecida": {"receita": 2.5, "ebitda": 8.0, "lucro": 12.0}
            }
        }
        
        # Pesos para valuation médio ponderado por estágio
        self.pesos_estagio = {
            "seed": [0.1, 0.2, 0.5, 0.2],         # Berkus mais relevante
            "startup": [0.2, 0.3, 0.3, 0.2],      # Berkus e DCF mais relevantes
            "scaleup": [0.4, 0.4, 0.1, 0.1],      # Múltiplos e DCF mais relevantes
            "estabelecida": [0.5, 0.4, 0.05, 0.05] # Múltiplos mais relevantes
        }
    
    def calcular_ebitda(self, receita_anual: float, despesas_totais_anuais: float) -> float:
        """Calcula o EBITDA baseado na receita anual e despesas totais anuais."""
        ebitda = receita_anual - despesas_totais_anuais
        return max(ebitda, 0)  # EBITDA não pode ser negativo
    
    def calcular_ebitda_detalhado(self, receita_anual: float, custos_vendas_mensal: float, 
                                 despesas_operacionais_mensal: float, despesas_adm_mensal: float,
                                 despesas_marketing_mensal: float, outros_custos_mensal: float = 0) -> float:
        """Calcula o EBITDA baseado nos componentes mensais."""
        # Converter para anuais
        custos_vendas_anual = custos_vendas_mensal * 12
        despesas_operacionais_anual = despesas_operacionais_mensal * 12
        despesas_adm_anual = despesas_adm_mensal * 12
        despesas_marketing_anual = despesas_marketing_mensal * 12
        outros_custos_anual = outros_custos_mensal * 12
        
        despesas_totais = custos_vendas_anual + despesas_operacionais_anual + despesas_adm_anual + despesas_marketing_anual + outros_custos_anual
        ebitda = receita_anual - despesas_totais
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
            fatores_berkus.append({"fator": "Faturamento (2x)", "valor": valor_receita})
        
        return {
            "valor_total": valor_base,
            "fatores": fatores_berkus
        }
    
    def calcular_scorecard(self, receita_anual: float, setor: str,
                          equipe: float, produto: float, vendas_marketing: float,
                          financas: float, concorrencia: float, inovacao: float) -> Dict:
        """Calcula valuation usando o método Scorecard."""
        
        # Valor médio de startups similares (ajustado para mercado brasileiro)
        valor_medio = 2000000  # R$ 2M
        
        # Fatores de ajuste
        fatores = {
            "Força da Equipe": equipe,
            "Qualidade do Produto": produto,
            "Estratégia de Vendas/Marketing": vendas_marketing,
            "Saúde Financeira": financas,
            "Concorrência": concorrencia,
            "Inovação": inovacao
        }
        
        # Calcular valor
        valor = valor_medio
        for fator, peso in fatores.items():
            valor *= peso
        
        # Ajuste por faturamento
        valor_receita = 0
        if receita_anual > 0:
            valor_receita = receita_anual * 3  # 3x faturamento
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
            dados_empresa["equipe"],
            dados_empresa["produto"],
            dados_empresa["vendas_marketing"],
            dados_empresa["financas"],
            dados_empresa["concorrencia"],
            dados_empresa["inovacao"]
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
    
    def exportar_relatorio_completo(self, relatorio: Dict) -> pd.DataFrame:
        """Exporta relatório completo com todos os dados."""
        
        dados_empresa = relatorio["dados_empresa"]
        resultados = relatorio["resultados"]
        
        # Criar lista de dados para o DataFrame
        dados_completos = []
        
        # Informações da empresa
        dados_completos.append(["INFORMAÇÕES DA EMPRESA", "", ""])
        dados_completos.append(["Nome da Empresa", dados_empresa["nome_empresa"], ""])
        dados_completos.append(["Setor", dados_empresa["setor"], ""])
        dados_completos.append(["Estágio", dados_empresa["tamanho_empresa"], ""])
        dados_completos.append(["", "", ""])
        
        # Dados financeiros
        dados_completos.append(["DADOS FINANCEIROS", "", ""])
        dados_completos.append(["Faturamento Anual (R$)", f"R$ {dados_empresa['receita_anual']:,.0f}", ""])
        dados_completos.append(["EBITDA (R$)", f"R$ {dados_empresa['ebitda']:,.0f}", ""])
        dados_completos.append(["Margem EBITDA (%)", f"{dados_empresa['margem_ebitda']*100:.1f}%", ""])
        dados_completos.append(["Lucro Líquido (R$)", f"R$ {dados_empresa['lucro_liquido']:,.0f}", ""])
        dados_completos.append(["Crescimento Estimado (%)", f"{dados_empresa['crescimento_anual']*100:.1f}%", ""])
        dados_completos.append(["Número de Vendedores", dados_empresa["n_vendedores"], ""])
        dados_completos.append(["", "", ""])
        
        # Fatores qualitativos
        dados_completos.append(["FATORES QUALITATIVOS", "", ""])
        dados_completos.append(["Produto Lançado", "Sim" if dados_empresa["produto_lancado"] else "Não", ""])
        dados_completos.append(["Parcerias Estratégicas", "Sim" if dados_empresa["parcerias_estrategicas"] else "Não", ""])
        dados_completos.append(["Vendas Orgânicas", "Sim" if dados_empresa["vendas_organicas"] else "Não", ""])
        dados_completos.append(["Investe em Tráfego Pago", "Sim" if dados_empresa["investe_trafego_pago"] else "Não", ""])
        dados_completos.append(["", "", ""])
        
        # Scorecard
        dados_completos.append(["SCORECARD", "", ""])
        scorecard_fatores = {
            "Força da Equipe": dados_empresa["equipe"],
            "Tamanho da Oportunidade": dados_empresa["tamanho_mercado"],
            "Qualidade do Produto": dados_empresa["produto"],
            "Estratégia de Vendas/Marketing": dados_empresa["vendas_marketing"],
            "Saúde Financeira": dados_empresa["financas"],
            "Competição": dados_empresa["competicao"],
            "Timing de Mercado": dados_empresa["timing"],
            "Inovação": dados_empresa.get("inovacao", 1.0),
            "Canais de Distribuição": dados_empresa.get("channels", 1.0)
        }
        
        for fator, valor in scorecard_fatores.items():
            if valor == 0.7:
                nivel = "Baixo"
            elif valor == 1.0:
                nivel = "Médio"
            else:
                nivel = "Alto"
            dados_completos.append([fator, nivel, ""])
        
        dados_completos.append(["", "", ""])
        
        # Resultados por método
        dados_completos.append(["RESULTADOS POR MÉTODO", "", ""])
        dados_completos.append(["Múltiplos - Faturamento", f"R$ {resultados['multiplos']['receita']:,.0f}", f"{resultados['multiplos']['multiplos']['receita']}x"])
        dados_completos.append(["Múltiplos - EBITDA", f"R$ {resultados['multiplos']['ebitda']:,.0f}", f"{resultados['multiplos']['multiplos']['ebitda']}x"])
        dados_completos.append(["Múltiplos - Lucro", f"R$ {resultados['multiplos']['lucro']:,.0f}", f"{resultados['multiplos']['multiplos']['lucro']}x"])
        dados_completos.append(["DCF", f"R$ {resultados['dcf']['valor_empresa']:,.0f}", ""])
        dados_completos.append(["Berkus", f"R$ {resultados['berkus']['valor_total']:,.0f}", ""])
        dados_completos.append(["Scorecard", f"R$ {resultados['scorecard']['valor_total']:,.0f}", ""])
        dados_completos.append(["", "", ""])
        
        # Valuation final
        dados_completos.append(["VALUATION FINAL", "", ""])
        dados_completos.append(["Valuation Médio Ponderado", f"R$ {relatorio['valuation_medio']:,.0f}", ""])
        dados_completos.append(["Valuation Médio Ponderado (M)", f"R$ {relatorio['valuation_medio']/1000000:.1f}M", ""])
        dados_completos.append(["", "", ""])
        
        # Pesos utilizados
        dados_completos.append(["PESOS UTILIZADOS", "", ""])
        dados_completos.append(["Múltiplos", f"{relatorio['pesos_utilizados'][0]*100:.1f}%", ""])
        dados_completos.append(["DCF", f"{relatorio['pesos_utilizados'][1]*100:.1f}%", ""])
        dados_completos.append(["Berkus", f"{relatorio['pesos_utilizados'][2]*100:.1f}%", ""])
        dados_completos.append(["Scorecard", f"{relatorio['pesos_utilizados'][3]*100:.1f}%", ""])
        dados_completos.append(["", "", ""])
        
        # Data do cálculo
        dados_completos.append(["DATA DO CÁLCULO", relatorio["data_calculo"].strftime("%d/%m/%Y %H:%M"), ""])
        
        return pd.DataFrame(dados_completos, columns=["Item", "Valor", "Detalhe"]) 