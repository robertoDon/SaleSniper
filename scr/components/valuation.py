import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import locale
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import xlsxwriter
from services.valuation_service import ValuationService

# Configurar locale para português do Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

def formatar_numero_br(valor, casas_decimais=0):
    """Formata número para o padrão brasileiro."""
    if isinstance(valor, (int, float)):
        if isinstance(valor, int) or (isinstance(valor, float) and (valor.is_integer() or abs(valor - round(valor)) < 0.001)):
            return f"{int(round(valor)):,}".replace(",", ".")
        return f"{valor:,.{casas_decimais}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor

def formatar_dataframe_br(df):
    """Formata todos os números de um DataFrame para o padrão brasileiro."""
    df_formatado = df.copy()
    for coluna in df_formatado.columns:
        if pd.api.types.is_numeric_dtype(df_formatado[coluna]):
            df_formatado[coluna] = df_formatado[coluna].apply(lambda x: formatar_numero_br(x))
    return df_formatado

def exportar_para_xlsx(df: pd.DataFrame, nome_arquivo: str):
    """Exporta um DataFrame para arquivo XLSX."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    return output.getvalue()

def exportar_para_pdf(df: pd.DataFrame, nome_arquivo: str):
    """Exporta um DataFrame para arquivo PDF."""
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    elements = []
    
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    
    elements.append(table)
    doc.build(elements)
    return output.getvalue()

def exibir_botoes_exportacao(df: pd.DataFrame, nome_arquivo: str):
    """Exibe botões para exportar DataFrame em diferentes formatos."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.download_button(
            label="📥 CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f"{nome_arquivo}.csv",
            mime='text/csv'
        )
    
    with col2:
        st.download_button(
            label="📥 XLSX",
            data=exportar_para_xlsx(df, nome_arquivo),
            file_name=f"{nome_arquivo}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    with col3:
        st.download_button(
            label="📥 PDF",
            data=exportar_para_pdf(df, nome_arquivo),
            file_name=f"{nome_arquivo}.pdf",
            mime='application/pdf'
        )

def exibir_valuation():
    # Verificar se é a primeira execução
    if "valuation_initialized" not in st.session_state:
        st.session_state["valuation_initialized"] = True
        st.session_state["valuation_result"] = None
    
    st.markdown("<h1 style='color: #FF8C00;'>SaleSniper - Valuation de Empresas</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    ### 📊 Calculadora de Valuation Empresarial
    
    Esta ferramenta utiliza os métodos mais estabelecidos do mercado para calcular o valuation de sua empresa:
    
    - **Múltiplos de Mercado**: Comparação com empresas similares
    - **DCF (Discounted Cash Flow)**: Valor presente dos fluxos futuros
    - **Método Berkus**: Para empresas em estágio inicial
    - **Scorecard**: Avaliação qualitativa e quantitativa
    """)
    
    # Inicializar serviço de valuation
    valuation_service = ValuationService()
    
    # Formulário de dados da empresa
    st.markdown("### 📋 Dados da Empresa")
    
    col1, col2 = st.columns(2)
    
    with col1:
        nome_empresa = st.text_input("Nome da Empresa", value="Minha Empresa")
        setor = st.selectbox("Setor", [
            "SaaS", "Tecnologia", "E-commerce", "Consultoria", "Varejo", "Serviços", "Outros"
        ])
        
        # Estágios da empresa com explicações
        estagios_info = {
            "ideacao": "Desenvolvendo ideia e conceito do produto/serviço",
            "validacao": "Validando mercado e primeiros clientes",
            "operacao": "Operação estável com receita recorrente",
            "tracao": "Crescimento acelerado e validação de mercado",
            "escala": "Expansão e otimização de operações"
        }
        
        tamanho_empresa = st.selectbox("Estágio da Empresa", list(estagios_info.keys()))
        
        # Exibir explicação do estágio
        st.caption(f"💡 {estagios_info[tamanho_empresa]}")
        
        receita_anual = st.number_input("Faturamento Anual (R$)", min_value=0.0, value=1000000.0, step=10000.0, 
                                       help="Ex: 1.000.000 para R$ 1 milhão - Valor total faturado no ano")
        st.caption(f"Valor atual: R$ {formatar_numero_br(receita_anual)}")
        
        n_vendedores = st.number_input("Número de Vendedores", min_value=0, value=5, step=1)
        
        # Métricas qualitativas para Berkus e Scorecard
        produto_lancado = st.checkbox("Produto Lançado", value=True)
        parcerias_estrategicas = st.checkbox("Parcerias Estratégicas", value=False)
        vendas_organicas = st.checkbox("Vendas Orgânicas", value=True)
        investe_trafego_pago = st.checkbox("Invisto em tráfego pago", value=True)
    
    with col2:
        # Estimativa de crescimento baseada no setor e estágio
        if setor == "SaaS" and tamanho_empresa == "ideacao":
            crescimento_estimado = 100
        elif setor == "SaaS" and tamanho_empresa == "validacao":
            crescimento_estimado = 80
        elif setor == "SaaS" and tamanho_empresa == "operacao":
            crescimento_estimado = 50
        elif setor == "SaaS" and tamanho_empresa == "tracao":
            crescimento_estimado = 30
        elif setor == "SaaS" and tamanho_empresa == "escala":
            crescimento_estimado = 15
        elif setor == "Consultoria" and tamanho_empresa == "ideacao":
            crescimento_estimado = 80
        elif setor == "Consultoria" and tamanho_empresa == "validacao":
            crescimento_estimado = 60
        elif setor == "Consultoria" and tamanho_empresa == "operacao":
            crescimento_estimado = 40
        elif setor == "Consultoria" and tamanho_empresa == "tracao":
            crescimento_estimado = 25
        elif setor == "Consultoria" and tamanho_empresa == "escala":
            crescimento_estimado = 10
        else:
            crescimento_estimado = 30
        
        st.markdown(f"**Crescimento Estimado: {crescimento_estimado}%** (baseado no setor e estágio)")
        crescimento_anual = crescimento_estimado / 100
        
        # Opção para detalhar despesas - MOVIDA PARA BAIXO
        detalhar_despesas = st.checkbox("🔍 Detalhar Despesas (Opcional)")
        
        if detalhar_despesas:
            st.markdown("**Detalhe suas despesas mensais por categoria:**")
            custos_vendas_mensal = st.number_input("Custos de Vendas (R$/mês)", min_value=0.0, value=25000.0, step=1000.0, 
                                                  help="Ex: 25.000")
            st.caption(f"Valor atual: R$ {formatar_numero_br(custos_vendas_mensal)}/mês")
            
            despesas_operacionais_mensal = st.number_input("Despesas Operacionais (R$/mês)", min_value=0.0, value=16667.0, step=1000.0, 
                                                          help="Ex: 16.667")
            st.caption(f"Valor atual: R$ {formatar_numero_br(despesas_operacionais_mensal)}/mês")
            
            despesas_adm_mensal = st.number_input("Despesas Administrativas (R$/mês)", min_value=0.0, value=12500.0, step=1000.0, 
                                                 help="Ex: 12.500")
            st.caption(f"Valor atual: R$ {formatar_numero_br(despesas_adm_mensal)}/mês")
            
            despesas_marketing_mensal = st.number_input("Despesas de Marketing (R$/mês)", min_value=0.0, value=8333.0, step=1000.0, 
                                                       help="Ex: 8.333")
            st.caption(f"Valor atual: R$ {formatar_numero_br(despesas_marketing_mensal)}/mês")
            
            outros_custos_mensal = st.number_input("Outros Custos (R$/mês)", min_value=0.0, value=4167.0, step=1000.0, 
                                                  help="Ex: 4.167")
            st.caption(f"Valor atual: R$ {formatar_numero_br(outros_custos_mensal)}/mês")
            
            # Calcular totais anuais
            custos_vendas = custos_vendas_mensal * 12
            despesas_operacionais = despesas_operacionais_mensal * 12
            despesas_adm = despesas_adm_mensal * 12
            despesas_marketing = despesas_marketing_mensal * 12
            outros_custos = outros_custos_mensal * 12
            
            # Calcular total das despesas detalhadas
            despesas_totais = custos_vendas + despesas_operacionais + despesas_adm + despesas_marketing + outros_custos
            despesas_totais_mensal = despesas_totais / 12
            st.markdown(f"**Total das Despesas: R$ {formatar_numero_br(despesas_totais_mensal)}/mês (R$ {formatar_numero_br(despesas_totais)}/ano)**")
        else:
            # Campo simples para despesas totais mensais (só aparece se não detalhar)
            despesas_totais_mensal = st.number_input("Despesas Totais (R$/mês)", min_value=0.0, value=66667.0, step=1000.0, 
                                                   help="Ex: 66.667 - Soma de todas as despesas mensais")
            st.caption(f"Valor atual: R$ {formatar_numero_br(despesas_totais_mensal)}/mês")
            
            # Calcular total anual
            despesas_totais = despesas_totais_mensal * 12
            
            # Se não detalhou, usar valores padrão proporcionais
            custos_vendas = despesas_totais * 0.375  # 37.5%
            despesas_operacionais = despesas_totais * 0.25   # 25%
            despesas_adm = despesas_totais * 0.1875  # 18.75%
            despesas_marketing = despesas_totais * 0.125  # 12.5%
            outros_custos = despesas_totais * 0.0625  # 6.25%
        
        ebitda = receita_anual - despesas_totais
        ebitda = max(ebitda, 0)  # Não pode ser negativo
        
        # Lucro líquido será estimado baseado no EBITDA (assumindo 70% do EBITDA)
        lucro_liquido = ebitda * 0.7 if ebitda > 0 else 0
        st.markdown(f"**Lucro Líquido Estimado: R$ {formatar_numero_br(lucro_liquido)}** (70% do EBITDA)")
    
    # Fatores para Scorecard - 3 COLUNAS
    st.markdown("### 🎯 Fatores Qualitativos (Scorecard)")
    st.markdown("Selecione o nível de cada fator:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption("**Força da Equipe**: Baixo = Equipe pequena/iniciante | Médio = Equipe experiente | Alto = Equipe especializada/executiva")
        equipe_score = st.selectbox("Força da Equipe", ["Baixo", "Médio", "Alto"], index=1)
        
        st.caption("**Qualidade do Produto**: Baixo = MVP básico | Médio = Produto funcional | Alto = Produto diferenciado/premium")
        produto_score = st.selectbox("Qualidade do Produto", ["Baixo", "Médio", "Alto"], index=1)
        
        st.caption("**Estratégia de Vendas/Marketing**: Baixo = Sem estratégia definida | Médio = Estratégia básica | Alto = Estratégia sofisticada")
        vendas_marketing = st.selectbox("Estratégia de Vendas/Marketing", ["Baixo", "Médio", "Alto"], index=1)
    
    with col2:
        st.caption("**Saúde Financeira**: Baixo = Prejuízo/endividado | Médio = Equilibrado | Alto = Lucrativo/capital próprio")
        financas = st.selectbox("Saúde Financeira", ["Baixo", "Médio", "Alto"], index=1)
        
        st.caption("**Concorrência**: Baixo = Muitos concorrentes | Médio = Concorrência moderada | Alto = Poucos concorrentes")
        concorrencia = st.selectbox("Concorrência", ["Baixo", "Médio", "Alto"], index=1)
        
        st.caption("**Inovação**: Baixo = Produto comum | Médio = Alguma diferenciação | Alto = Tecnologia única/patente")
        inovacao = st.selectbox("Inovação", ["Baixo", "Médio", "Alto"], index=1)
    
    # Verificar se já temos resultados calculados
    if "valuation_result" in st.session_state and st.session_state["valuation_result"] is not None:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success("✅ Valuation já calculado! Os resultados estão sendo exibidos abaixo.")
        with col2:
            if st.button("🔄 Novo Cálculo", type="secondary"):
                st.session_state["valuation_result"] = None
                st.rerun()
        
        # Usar resultados salvos
        relatorio = st.session_state["valuation_result"]
        resultados = relatorio["resultados"]
        
        # Recuperar dados do formulário da sessão
        dados_empresa = relatorio["dados_empresa"]
        nome_empresa = dados_empresa["nome_empresa"]
        setor = dados_empresa["setor"]
        tamanho_empresa = dados_empresa["tamanho_empresa"]
        receita_anual = dados_empresa["receita_anual"]
        ebitda = dados_empresa["ebitda"]
        lucro_liquido = dados_empresa["lucro_liquido"]
        margem_ebitda = dados_empresa["margem_ebitda"]
        crescimento_anual = dados_empresa["crescimento_anual"]
        n_vendedores = dados_empresa["n_vendedores"]
        produto_lancado = dados_empresa["produto_lancado"]
        parcerias_estrategicas = dados_empresa["parcerias_estrategicas"]
        vendas_organicas = dados_empresa["vendas_organicas"]
        investe_trafego_pago = dados_empresa["investe_trafego_pago"]
        
        # Recuperar scores
        def converter_score_reverso(valor):
            if valor == 0.7: return "Baixo"
            elif valor == 1.0: return "Médio"
            else: return "Alto"  # 1.3
        
        equipe_score = converter_score_reverso(dados_empresa["equipe"])
        produto_score = converter_score_reverso(dados_empresa["produto"])
        vendas_marketing = converter_score_reverso(dados_empresa["vendas_marketing"])
        financas = converter_score_reverso(dados_empresa["financas"])
        concorrencia = converter_score_reverso(dados_empresa["concorrencia"])
        inovacao = converter_score_reverso(dados_empresa["inovacao"])
        
        # Calcular crescimento estimado para exibição
        if setor == "SaaS" and tamanho_empresa == "ideacao":
            crescimento_estimado = 100
        elif setor == "SaaS" and tamanho_empresa == "validacao":
            crescimento_estimado = 80
        elif setor == "SaaS" and tamanho_empresa == "operacao":
            crescimento_estimado = 50
        elif setor == "SaaS" and tamanho_empresa == "tracao":
            crescimento_estimado = 30
        elif setor == "SaaS" and tamanho_empresa == "escala":
            crescimento_estimado = 15
        elif setor == "Consultoria" and tamanho_empresa == "ideacao":
            crescimento_estimado = 80
        elif setor == "Consultoria" and tamanho_empresa == "validacao":
            crescimento_estimado = 60
        elif setor == "Consultoria" and tamanho_empresa == "operacao":
            crescimento_estimado = 40
        elif setor == "Consultoria" and tamanho_empresa == "tracao":
            crescimento_estimado = 25
        elif setor == "Consultoria" and tamanho_empresa == "escala":
            crescimento_estimado = 10
        else:
            crescimento_estimado = 30
    
    # Botão para calcular
    if st.button("💰 Calcular Valuation", type="primary"):
        
        # Converter valores do scorecard para números
        def converter_score(valor):
            if valor == "Baixo": return 0.7
            elif valor == "Médio": return 1.0
            else: return 1.3  # Alto
        
        # Calcular margem EBITDA
        margem_ebitda = ebitda / receita_anual if receita_anual > 0 else 0
        
        # Preparar dados da empresa
        dados_empresa = {
            "nome_empresa": nome_empresa,
            "setor": setor,
            "tamanho_empresa": tamanho_empresa,
            "receita_anual": receita_anual,
            "ebitda": ebitda,
            "lucro_liquido": lucro_liquido,
            "margem_ebitda": margem_ebitda,
            "crescimento_anual": crescimento_anual,
            "n_vendedores": n_vendedores,
            "produto_lancado": produto_lancado,
            "parcerias_estrategicas": parcerias_estrategicas,
            "vendas_organicas": vendas_organicas,
            "investe_trafego_pago": investe_trafego_pago,
            "equipe": converter_score(equipe_score),
            "produto": converter_score(produto_score),
            "vendas_marketing": converter_score(vendas_marketing),
            "financas": converter_score(financas),
            "concorrencia": converter_score(concorrencia),
            "inovacao": converter_score(inovacao)
        }
        
        # Gerar relatório completo
        relatorio = valuation_service.gerar_relatorio_completo(dados_empresa)
        resultados = relatorio["resultados"]
        
        # Salvar na sessão
        st.session_state["valuation_result"] = relatorio
        st.success("✅ Valuation calculado com sucesso!")
        
        # Exibir resultados após o cálculo
        st.markdown("### 📊 Resultados do Valuation")
        
        # APENAS MÚLTIPLOS - Simplificado
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Múltiplos", f"R$ {formatar_numero_br(resultados['multiplos']['receita']/1000000, 1)}M")
            with st.expander("❓ O que é valuation por múltiplos?", expanded=False):
                st.markdown("""
                **🔢 Método dos Múltiplos**
                
                **Como funciona:** Compara sua empresa com outras similares do mercado usando múltiplos de faturamento, EBITDA e lucro.
                
                **Fórmula:** Valor = Métrica Financeira × Múltiplo de Mercado
                
                **Por que este valor:** Baseado em múltiplos reais do mercado para empresas do setor {setor} em estágio {tamanho_empresa}.
                
                **Vantagens:** 
                - Baseado em dados reais do mercado
                - Fácil de entender e explicar
                - Reflete o que investidores pagam por empresas similares
                """)
        
        with col2:
            st.metric("DCF", f"R$ {formatar_numero_br(resultados['dcf']['valor_empresa']/1000000, 1)}M")
            st.caption("Ver relatório completo")
        
        with col3:
            st.metric("Berkus", f"R$ {formatar_numero_br(resultados['berkus']['valor_total']/1000000, 1)}M")
            st.caption("Ver relatório completo")
        
        with col4:
            st.metric("Scorecard", f"R$ {formatar_numero_br(resultados['scorecard']['valor_total']/1000000, 1)}M")
            st.caption("Ver relatório completo")
        
        # Métricas Financeiras - MANTER COMO ESTÁ
        st.markdown("### 📊 Métricas Financeiras Calculadas")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("EBITDA", f"R$ {formatar_numero_br(ebitda)}")
        with col2:
            st.metric("Margem EBITDA", f"{margem_ebitda*100:.1f}%")
        
        # Multiplicadores Utilizados - MANTER COMO ESTÁ
        st.markdown("### 📈 Multiplicadores Utilizados")
        mult = resultados['multiplos']['multiplos']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Faturamento", f"{mult['receita']}x")
        with col2:
            st.metric("EBITDA", f"{mult['ebitda']}x")
        with col3:
            st.metric("Lucro Líquido", f"{mult['lucro']}x")
        
        st.caption(f"Baseado em empresas do setor {setor} em estágio {tamanho_empresa}")
        
        # Análise e recomendação - SEM EMOJIS
        st.markdown("### E aí, estou bem?")
        
        # Calcular métricas para análise
        valuation_medio = relatorio['valuation_medio']
        margem_ebitda = ebitda / receita_anual if receita_anual > 0 else 0
        
        # Determinar se está bem para o mercado
        if tamanho_empresa == "ideacao":
            if valuation_medio >= 2000000:  # R$ 2M
                status = "Muito bem posicionada!"
                analise = "Sua empresa está com um valuation excelente para o estágio de ideação. Isso indica que você tem uma base sólida e potencial de crescimento significativo."
            elif valuation_medio >= 1000000:  # R$ 1M
                status = "Bem posicionada"
                analise = "Sua empresa está bem posicionada no mercado. Há espaço para crescimento, mas a base está sólida."
            else:
                status = "Precisa de melhorias"
                analise = "Sua empresa precisa de melhorias para se destacar no mercado. Foque em validar o produto e gerar receita."
        elif tamanho_empresa == "validacao":
            if valuation_medio >= 5000000:  # R$ 5M
                status = "Excelente posicionamento!"
                analise = "Sua empresa está com um valuation muito forte para o estágio de validação. Você tem um produto validado e crescimento consistente."
            elif valuation_medio >= 2500000:  # R$ 2.5M
                status = "Bem posicionada"
                analise = "Sua empresa está bem posicionada. Continue focando na validação de mercado."
            else:
                status = "Precisa de melhorias"
                analise = "Sua empresa precisa de melhorias para se destacar. Foque em validação de mercado e primeiros clientes."
        elif tamanho_empresa == "operacao":
            if valuation_medio >= 15000000:  # R$ 15M
                status = "Posicionamento excepcional!"
                analise = "Sua empresa está com um valuation excepcional para o estágio de operação. Você tem um modelo de negócio validado e operação estável."
            elif valuation_medio >= 7500000:  # R$ 7.5M
                status = "Bem posicionada"
                analise = "Sua empresa está bem posicionada. Continue focando na otimização da operação."
            else:
                status = "Precisa de melhorias"
                analise = "Sua empresa precisa de melhorias para se destacar. Foque em estabilizar a operação e aumentar receita."
        elif tamanho_empresa == "tracao":
            if valuation_medio >= 50000000:  # R$ 50M
                status = "Posicionamento excepcional!"
                analise = "Sua empresa está com um valuation excepcional para o estágio de tração. Você tem crescimento acelerado e validação de mercado."
            elif valuation_medio >= 25000000:  # R$ 25M
                status = "Bem posicionada"
                analise = "Sua empresa está bem posicionada. Continue focando no crescimento acelerado."
            else:
                status = "Precisa de melhorias"
                analise = "Sua empresa precisa de melhorias para se destacar. Foque em crescimento acelerado e validação."
        else:  # escala
            if valuation_medio >= 100000000:  # R$ 100M
                status = "Posicionamento sólido!"
                analise = "Sua empresa em escala está com um valuation muito sólido. Você tem um negócio maduro e lucrativo."
            elif valuation_medio >= 50000000:  # R$ 50M
                status = "Bem posicionada"
                analise = "Sua empresa está bem posicionada. Continue focando na otimização e expansão."
            else:
                status = "Precisa de melhorias"
                analise = "Sua empresa precisa de melhorias para se destacar. Foque em eficiência e crescimento sustentável."
        
        # Análise específica baseada nos dados do formulário
        pontos_positivos = []
        pontos_alerta = []
        pontos_negativos = []
        
        # Pontos positivos baseados nos dados
        if produto_lancado:
            pontos_positivos.append("**Produto já lançado**: Você tem um produto validado no mercado")
        if vendas_organicas:
            pontos_positivos.append("**Vendas orgânicas**: Você consegue gerar vendas sem investimento pesado")
        if parcerias_estrategicas:
            pontos_positivos.append("**Parcerias estratégicas**: Você tem alianças importantes no mercado")
        if investe_trafego_pago:
            pontos_positivos.append("**Investe em tráfego pago**: Você tem estratégia de aquisição ativa")
        if margem_ebitda > 0.2:
            pontos_positivos.append("**Margem EBITDA alta**: Sua operação é eficiente")
        if receita_anual > 5000000:
            pontos_positivos.append("**Faturamento sólido**: Você tem uma base financeira forte")
        if n_vendedores > 3:
            pontos_positivos.append("**Equipe de vendas**: Você tem capacidade de expansão")
        
        # Pontos de alerta (meio termo)
        if margem_ebitda >= 0.1 and margem_ebitda <= 0.2:
            pontos_alerta.append("**Margem EBITDA moderada**: Há espaço para otimização de custos")
        if receita_anual >= 1000000 and receita_anual <= 5000000:
            pontos_alerta.append("**Faturamento em crescimento**: Continue focando na expansão")
        if n_vendedores >= 2 and n_vendedores <= 3:
            pontos_alerta.append("**Equipe de vendas pequena**: Considere expandir para acelerar crescimento")
        
        # Pontos negativos específicos
        if not produto_lancado and tamanho_empresa in ["ideacao", "validacao"]:
            pontos_negativos.append("**Produto não lançado**: Priorize o lançamento para validar o mercado e aumentar o valuation")
        if not vendas_organicas and tamanho_empresa in ["ideacao", "validacao"]:
            pontos_negativos.append("**Sem vendas orgânicas**: Desenvolva estratégias de aquisição natural de clientes")
        if not parcerias_estrategicas:
            pontos_negativos.append("**Sem parcerias estratégicas**: Busque alianças que possam acelerar seu crescimento")
        if not investe_trafego_pago:
            pontos_negativos.append("**Não investe em tráfego pago**: Considere estratégias de marketing digital para crescimento")
        if margem_ebitda < 0.1:
            pontos_negativos.append(f"**Margem EBITDA baixa ({margem_ebitda*100:.1f}%)**: Otimize custos operacionais para aumentar lucratividade")
        if receita_anual < 1000000:
            pontos_negativos.append(f"**Faturamento baixo (R$ {formatar_numero_br(receita_anual)})**: Foque em crescimento de vendas e expansão de mercado")
        if n_vendedores < 2:
            pontos_negativos.append("**Equipe de vendas pequena**: Considere expandir a equipe para acelerar crescimento")
        
        # Garantir sempre pelo menos 1 de cada
        if not pontos_positivos:
            pontos_positivos.append("**Potencial de crescimento**: Sua empresa tem espaço para evolução significativa")
        if not pontos_alerta:
            pontos_alerta.append("**Continue otimizando**: Mantenha o foco na melhoria contínua")
        if not pontos_negativos:
            pontos_negativos.append("**Atenção aos detalhes**: Foque na otimização de processos e eficiência")
        
        # Exibir análise
        st.markdown(f"**{status}**")
        st.markdown(analise)
        
        st.markdown("**Ponto Positivo:**")
        st.markdown(f"• {pontos_positivos[0]}")
        
        st.markdown("**Ponto Alerta:**")
        st.markdown(f"• {pontos_alerta[0]}")
        
        st.markdown("**Ponto Negativo:**")
        st.markdown(f"• {pontos_negativos[0]}")
        
        # Recomendação de produto Don
        st.markdown("**Recomendação de produto Don:**")
        
        if tamanho_empresa == "ideacao":
            programa = "**Don for Ideação**"
            descricao_programa = "Programa especializado para empresas em estágio de ideação, focado em desenvolvimento de conceito e validação inicial."
            dica_negocio = "Foque em validar sua ideia com o mercado antes de investir pesado em desenvolvimento."
        elif tamanho_empresa == "validacao":
            programa = "**Don for Validação**"
            descricao_programa = "Programa para empresas em validação, focado em primeiros clientes e validação de mercado."
            dica_negocio = "Priorize encontrar seus primeiros clientes e validar o produto-market fit."
        elif tamanho_empresa == "operacao":
            programa = "**Don for Operação**"
            descricao_programa = "Programa para empresas em operação estável, focado em otimização e crescimento sustentável."
            dica_negocio = "Foque em estabilizar processos e aumentar a eficiência operacional."
        elif tamanho_empresa == "tracao":
            programa = "**Don for Tração**"
            descricao_programa = "Programa para empresas em tração, focado em crescimento acelerado e expansão de mercado."
            dica_negocio = "Acelere o crescimento focando em estratégias de aquisição e expansão."
        else:  # escala
            programa = "**Don for Escala**"
            descricao_programa = "Programa para empresas em escala, focado em otimização e expansão estratégica."
            dica_negocio = "Otimize processos e busque expansão estratégica para maximizar resultados."
        
        st.markdown(f"Baseado no estágio da sua empresa ({tamanho_empresa}), recomendamos o {programa}.")
        st.markdown(descricao_programa)
        st.markdown(f"**Dica de negócio:** {dica_negocio}")
        
        # Botão de contato
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.link_button(
                "Entre em contato conosco",
                "https://api.whatsapp.com/send/?phone=554892254155&text&type=phone_number&app_absent=0",
                type="primary"
            )