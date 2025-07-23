import streamlit as st
from components.utils import calcular_segmentacao, calcular_metricas_segmentacao
import pandas as pd
import numpy as np
import locale

# Configurar locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # Usa o padrão do sistema

def formatar_valor(valor):
    # Se não for um número ou string numérica, retorna o valor original
    if not isinstance(valor, (int, float)):
        try:
            # Tenta converter para float se for uma string numérica
            if isinstance(valor, str):
                valor = float(valor.replace('R$', '').replace('.', '').replace(',', '.').strip())
            else:
                return valor
        except ValueError:
            return valor
            
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_ltv(df):
    """Calcula o LTV (Life-Time Value) para cada cliente"""
    # Verifica se temos as colunas necessárias
    if 'ticket_medio' not in df.columns:
        if 'valor_contrato' in df.columns:
            df['ticket_medio'] = df['valor_contrato']
        else:
            st.error("Não foi possível calcular o LTV: coluna 'ticket_medio' ou 'valor_contrato' não encontrada")
            return df
            
    # Calcular meses_ativo se não existir
    if 'meses_ativo' not in df.columns:
        if 'data_contratacao' in df.columns:
            # Calcular baseado na data de contratação
            df['data_contratacao'] = pd.to_datetime(df['data_contratacao'], errors='coerce')
            hoje = pd.Timestamp.now()
            df['meses_ativo'] = ((hoje - df['data_contratacao']).dt.days / 30).fillna(12).astype(int)
        else:
            # Valor padrão de 12 meses
            df['meses_ativo'] = 12
        
    # Calcula o LTV
    df['ltv'] = df['ticket_medio'] * df['meses_ativo']
    return df

def exibir_segmentacao():
    st.title("SaleSniper - Segmentação de Clientes")
    
    if "icp_data" not in st.session_state or st.session_state["icp_data"] is None:
        st.warning("Por favor, primeiro carregue os dados na aba 'Análise de ICP'")
        return
        
    # Botão para recarregar dados
    if st.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        del st.session_state["icp_data"]
        st.rerun()
        
    sistema = st.session_state["icp_data"]["sistema"]
    df = sistema.df
    
    # Garantindo que temos uma coluna 'nome'
    if 'nome' not in df.columns:
        df['nome'] = df.index.astype(str)
    
    # Calculando LTV se não existir
    if 'ltv' not in df.columns:
        df = calcular_ltv(df)
    
    # Garantindo que temos ticket_medio
    if 'ticket_medio' not in df.columns and 'valor_contrato' in df.columns:
        df['ticket_medio'] = df['valor_contrato']
    
    # Opções para o top 5
    opcoes_top5 = {
        "Meses como Cliente": {
            "coluna": "meses_ativo",
            "formato": lambda x: f"{x:.0f} meses",
            "ordenacao": False
        },
        "Ticket Médio": {
            "coluna": "ticket_medio",
            "formato": formatar_valor,
            "ordenacao": False
        },
        "LTV": {
            "coluna": "ltv",
            "formato": formatar_valor,
            "ordenacao": False
        },
        "Faturamento": {
            "coluna": "faturamento",
            "formato": formatar_valor,
            "ordenacao": False
        }
    }
    
    # Filtrar opções disponíveis baseado nas colunas existentes
    opcoes_disponiveis = {
        nome: dados for nome, dados in opcoes_top5.items() 
        if dados["coluna"] in df.columns
    }
    
    if opcoes_disponiveis:
        st.markdown("### 🏆 Top 5 Clientes")
        
        # Dropdown para selecionar a métrica
        metrica_selecionada = st.selectbox(
            "Selecione a métrica para o Top 5",
            list(opcoes_disponiveis.keys())
        )
        
        # Obter dados da métrica selecionada
        dados_metricas = opcoes_disponiveis[metrica_selecionada]
        coluna = dados_metricas["coluna"]
        formato = dados_metricas["formato"]
        ordenacao = dados_metricas["ordenacao"]
        
        # Criar DataFrame com top 5
        top5 = df.sort_values(coluna, ascending=ordenacao).head(5)[['nome', coluna]]
        top5 = top5.rename(columns={
            'nome': 'Cliente',
            coluna: metrica_selecionada
        })
        
        # Aplicar formatação
        top5[metrica_selecionada] = top5[metrica_selecionada].apply(formato)
        
        # Exibir tabela
        st.dataframe(top5, hide_index=True)
    
    st.markdown("---")
    
    # Mapeamento de descrições para os campos
    descricoes_campos = {
        "ltv": "Valor total do cliente (Ticket médio × Meses ativos)",
        "ticket_medio": "Valor mensal do contrato"
    }
    
    # Adicionando opção de segmentação por CNAE se existir na base
    if 'cnae' in df.columns:
        descricoes_campos['cnae'] = 'CNAE (3 dígitos) do cliente'
    
    # Criando lista de opções com descrições
    opcoes_campos = list(descricoes_campos.values())
    
    col1, col2 = st.columns(2)
    with col1:
        campo_selecionado = st.selectbox(
            "Campo base para segmentar",
            opcoes_campos
        )
        # Convertendo a descrição de volta para o nome do campo
        campo = next(c for c in descricoes_campos.keys() if descricoes_campos[c] == campo_selecionado)
        
    with col2:
        tipo_segmentacao = st.selectbox(
            "Tipo de Segmentação",
            ["Customizada por valor acumulado", "Customizada por quantidade"],
            index=0
        )

    # Adicionando campos para customização dos percentuais
    if tipo_segmentacao == "Customizada por valor acumulado":
        col1, col2 = st.columns(2)
        with col1:
            percentual_a = st.number_input(
                "Percentual para Grupo A (%)",
                min_value=1,
                max_value=99,
                value=20,
                help="Percentual do valor total que o Grupo A deve representar"
            )
        with col2:
            st.info(f"""💡 A segmentação customizada por valor acumulado:
            - Grupo A: Clientes que somam {percentual_a}% do valor total ({campo})
            - Grupo B: Demais clientes""")
    else:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            percentual_tier1 = st.number_input(
                "Tier 1 (%)",
                min_value=1,
                max_value=100,
                value=20,
                help="Percentual de clientes no Tier 1"
            )
        with col2:
            percentual_tier2 = st.number_input(
                "Tier 2 (%)",
                min_value=1,
                max_value=100,
                value=30,
                help="Percentual de clientes no Tier 2"
            )
        with col3:
            percentual_tier3 = st.number_input(
                "Tier 3 (%)",
                min_value=1,
                max_value=100,
                value=30,
                help="Percentual de clientes no Tier 3"
            )
        with col4:
            percentual_tier4 = st.number_input(
                "Tier 4 (%)",
                min_value=1,
                max_value=100,
                value=20,
                help="Percentual de clientes no Tier 4"
            )
            
        # Validar se a soma dos percentuais é 100%
        soma_percentuais = percentual_tier1 + percentual_tier2 + percentual_tier3 + percentual_tier4
        if soma_percentuais != 100:
            st.error(f"A soma dos percentuais deve ser 100%. Atual: {soma_percentuais}%")
            st.stop()
            
        st.info(f"""💡 A segmentação customizada por quantidade:
        - Tier 1: {percentual_tier1}% dos clientes
        - Tier 2: {percentual_tier2}% dos clientes
        - Tier 3: {percentual_tier3}% dos clientes
        - Tier 4: {percentual_tier4}% dos clientes""")

    # Adicionando explicação sobre o campo selecionado
    if campo == "ltv":
        st.info("""💡 O LTV (Life-Time Value) representa o valor total que o cliente gerou para sua empresa:
        - Ticket médio × Número de meses desde a contratação""")

    if campo:
        # Usando função cacheada para segmentação
        if tipo_segmentacao == "Customizada por valor acumulado":
            seg = calcular_segmentacao(df, campo, "80/20", percentual_a)
        else:
            seg = calcular_segmentacao(df, campo, "20/30/30/20", 
                                     [percentual_tier1, percentual_tier2, percentual_tier3, percentual_tier4])
        
        # Removendo colunas duplicadas
        seg = seg.loc[:, ~seg.columns.duplicated()]
        
        # Garantindo que temos as colunas necessárias
        colunas_necessarias = ["nome", campo, "tier"]
        for col in colunas_necessarias:
            if col not in seg.columns:
                if col == "nome":
                    seg["nome"] = seg.index.astype(str)
                elif col == "tier":
                    st.error("Erro na segmentação: coluna 'tier' não encontrada")
                    return
        
        resultado = seg[colunas_necessarias].reset_index(drop=True)
        
        # Formatando valores monetários apenas para exibição
        resultado[campo] = resultado[campo].apply(formatar_valor)
        
        # Análise da segmentação
        st.markdown("### Resultados da Segmentação")
        st.dataframe(resultado, hide_index=True) 