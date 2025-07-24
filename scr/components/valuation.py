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
    st.markdown("<h1 style='color: #FF8C00;'>SaleSniper - Valuation de Empresas</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    ### 📊 Calculadora de Valuation Empresarial
    
    Esta ferramenta utiliza os métodos mais estabelecidos do mercado para calcular o valuation de sua empresa:
    
    - **Múltiplos de Mercado**: Comparação com empresas similares
    - **DCF (Discounted Cash Flow)**: Valor presente dos fluxos futuros
    - **Método Berkus**: Para startups em estágio inicial
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
            "SaaS", "E-commerce", "Fintech", "Healthtech", "Edtech", "Consultoria", "Outros"
        ])
        tamanho_empresa = st.selectbox("Estágio da Empresa", [
            "seed", "startup", "scaleup", "estabelecida"
        ])
        receita_anual = st.number_input("Receita Anual (R$)", min_value=0.0, value=1000000.0, step=10000.0, 
                                       help="Ex: 1.000.000 para R$ 1 milhão")
        st.caption(f"Valor atual: R$ {formatar_numero_br(receita_anual)}")
        
        # Opção para detalhar despesas
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
    
    with col2:
        # Crescimento baseado no setor e estágio (estimativa automática)
        n_vendedores = st.number_input("Número de Vendedores", min_value=0, value=5, step=1)
        
        # Estimativa de crescimento baseada no setor e estágio
        if setor == "SaaS" and tamanho_empresa == "seed":
            crescimento_estimado = 80
        elif setor == "SaaS" and tamanho_empresa == "startup":
            crescimento_estimado = 50
        elif setor == "SaaS" and tamanho_empresa == "scaleup":
            crescimento_estimado = 30
        elif setor == "SaaS" and tamanho_empresa == "estabelecida":
            crescimento_estimado = 15
        elif setor == "Consultoria" and tamanho_empresa == "seed":
            crescimento_estimado = 60
        elif setor == "Consultoria" and tamanho_empresa == "startup":
            crescimento_estimado = 40
        elif setor == "Consultoria" and tamanho_empresa == "scaleup":
            crescimento_estimado = 25
        elif setor == "Consultoria" and tamanho_empresa == "estabelecida":
            crescimento_estimado = 10
        else:
            crescimento_estimado = 20
        
        st.markdown(f"**Crescimento Estimado: {crescimento_estimado}%** (baseado no setor e estágio)")
        crescimento_anual = crescimento_estimado / 100
        
        # Métricas qualitativas para Berkus e Scorecard
        produto_lancado = st.checkbox("Produto Lançado", value=True)
        parcerias_estrategicas = st.checkbox("Parcerias Estratégicas", value=False)
        vendas_organicas = st.checkbox("Vendas Orgânicas", value=True)
        investe_trafego_pago = st.checkbox("Já investe em tráfego pago?", value=True)
    
    # Fatores para Scorecard
    st.markdown("### 🎯 Fatores Qualitativos (Scorecard)")
    st.markdown("Selecione o nível de cada fator:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        equipe_score = st.selectbox("Força da Equipe", ["Baixo", "Médio", "Alto"], index=1)
        produto_score = st.selectbox("Qualidade do Produto", ["Baixo", "Médio", "Alto"], index=1)
        vendas_marketing = st.selectbox("Estratégia de Vendas/Marketing", ["Baixo", "Médio", "Alto"], index=1)
    
    with col2:
        financas = st.selectbox("Saúde Financeira", ["Baixo", "Médio", "Alto"], index=1)
        concorrencia = st.selectbox("Concorrência", ["Baixo", "Médio", "Alto"], index=1)
        inovacao = st.selectbox("Inovação", ["Baixo", "Médio", "Alto"], index=1)
    
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
        
        # Exibir resultados
        st.markdown("### 📊 Resultados do Valuation")
        
        # Métricas principais com tooltips explicativos
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Múltiplos", f"R$ {formatar_numero_br(resultados['multiplos']['receita']/1000000, 1)}M")
            with st.expander("❓ O que é valuation por múltiplos?", expanded=False):
                st.markdown("""
                **🔢 Método dos Múltiplos**
                
                **Como funciona:** Compara sua empresa com outras similares do mercado usando múltiplos de receita, EBITDA e lucro.
                
                **Fórmula:** Valor = Métrica Financeira × Múltiplo de Mercado
                
                **Por que este valor:** Baseado em múltiplos reais do mercado para empresas do setor {setor} em estágio {tamanho_empresa}.
                
                **Vantagens:** 
                - Baseado em dados reais do mercado
                - Fácil de entender e explicar
                - Reflete o que investidores pagam por empresas similares
                """)
        
        with col2:
            st.metric("DCF", f"R$ {formatar_numero_br(resultados['dcf']['valor_empresa']/1000000, 1)}M")
            with st.expander("❓ O que é valuation DCF?", expanded=False):
                st.markdown("""
                **💰 Método DCF (Discounted Cash Flow)**
                
                **Como funciona:** Calcula o valor presente dos fluxos de caixa futuros da empresa.
                
                **Fórmula:** Valor = Σ(Fluxo de Caixa Futuro / (1 + Taxa de Desconto)^ano) + Valor Terminal
                
                **Por que este valor:** Projeta crescimento de {crescimento_estimado}% ao ano com margem EBITDA de {margem_ebitda*100:.1f}%.
                
                **Vantagens:**
                - Considera crescimento futuro
                - Baseado em fundamentos da empresa
                - Mais preciso para empresas com projeções claras
                """)
        
        with col3:
            st.metric("Berkus", f"R$ {formatar_numero_br(resultados['berkus']['valor_total']/1000000, 1)}M")
            with st.expander("❓ O que é valuation Berkus?", expanded=False):
                st.markdown("""
                **🚀 Método Berkus**
                
                **Como funciona:** Avalia startups em estágio inicial baseado em marcos qualitativos.
                
                **Critérios avaliados:**
                - Produto lançado: R$ 500k
                - Vendas orgânicas: R$ 500k
                - Parcerias estratégicas: R$ 500k
                - Investimento em tráfego pago: R$ 500k
                
                **Por que este valor:** Ideal para empresas em estágio {tamanho_empresa} que já atingiram marcos importantes.
                
                **Vantagens:**
                - Ideal para startups em estágio inicial
                - Fácil de aplicar
                - Considera marcos importantes
                """)
        
        with col4:
            st.metric("Scorecard", f"R$ {formatar_numero_br(resultados['scorecard']['valor_total']/1000000, 1)}M")
            with st.expander("❓ O que é valuation Scorecard?", expanded=False):
                st.markdown("""
                **📊 Método Scorecard**
                
                **Como funciona:** Avalia qualitativamente diferentes aspectos da empresa e aplica multiplicadores.
                
                **Fatores avaliados:**
                - Força da equipe
                - Qualidade do produto
                - Estratégia de vendas/marketing
                - Saúde financeira
                - Concorrência
                - Inovação
                
                **Por que este valor:** Baseado na avaliação qualitativa dos 6 fatores principais da empresa.
                
                **Vantagens:**
                - Considera aspectos qualitativos
                - Flexível para diferentes tipos de empresa
                - Abrangente
                """)
        
        # Mostrar EBITDA e margem calculados
        st.markdown("### 📊 Métricas Financeiras Calculadas")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("EBITDA", f"R$ {formatar_numero_br(ebitda)}")
        with col2:
            st.metric("Margem EBITDA", f"{margem_ebitda*100:.1f}%")
        
        # Valuation médio ponderado com explicação
        col_val, col_info = st.columns([3, 1])
        
        with col_val:
            st.markdown(f"### 🎯 Valuation Médio Ponderado: **R$ {formatar_numero_br(relatorio['valuation_medio']/1000000, 1)}M**")
        
        with col_info:
            with st.expander("ℹ️ Como foi calculado", expanded=False):
                st.markdown(f"""
                **🎯 Valuation Médio Ponderado**
                
                **Como é calculado:** Combina os 4 métodos com pesos diferentes baseados no estágio da empresa.
                
                **Pesos utilizados:**
                - Múltiplos: {relatorio['pesos_utilizados'][0]*100:.1f}%
                - DCF: {relatorio['pesos_utilizados'][1]*100:.1f}%
                - Berkus: {relatorio['pesos_utilizados'][2]*100:.1f}%
                - Scorecard: {relatorio['pesos_utilizados'][3]*100:.1f}%
                
                **Por que estes pesos:** Empresas em estágio {tamanho_empresa} têm características específicas que tornam alguns métodos mais relevantes que outros.
                
                **Resultado:** Valor final que considera todos os aspectos da empresa de forma equilibrada.
                """)
        
        # Layout em duas colunas
        col_esquerda, col_direita = st.columns(2)
        
        # Removendo as seções de dicas para deixar a interface mais limpa
        
        # Detalhamento dos métodos
        st.markdown("### 📈 Detalhamento por Método")
        
        # Layout em duas colunas para detalhamentos
        col_det_esq, col_det_dir = st.columns(2)
        
        with col_det_esq:
            # Múltiplos
            st.markdown("#### 🔢 Valuation por Múltiplos")
            mult_df = pd.DataFrame({
                "Método": ["Receita", "EBITDA", "Lucro Líquido"],
                "Múltiplo": [
                    resultados['multiplos']['multiplos']['receita'],
                    resultados['multiplos']['multiplos']['ebitda'],
                    resultados['multiplos']['multiplos']['lucro']
                ],
                "Valor Base (R$)": [receita_anual, ebitda, lucro_liquido],
                "Valuation (R$)": [
                    resultados['multiplos']['receita'],
                    resultados['multiplos']['ebitda'],
                    resultados['multiplos']['lucro']
                ]
            })
            st.dataframe(formatar_dataframe_br(mult_df), hide_index=True)
            
            # Mostrar multiplicadores utilizados
            st.markdown("**Multiplicadores Utilizados:**")
            mult = resultados['multiplos']['multiplos']
            st.markdown(f"- **Receita**: {mult['receita']}x")
            st.markdown(f"- **EBITDA**: {mult['ebitda']}x")
            st.markdown(f"- **Lucro Líquido**: {mult['lucro']}x")
            st.markdown(f"- **Setor**: {setor}")
            st.markdown(f"- **Estágio**: {tamanho_empresa}")
            
            # DCF
            st.markdown("#### 💰 Valuation por DCF")
            dcf_df = pd.DataFrame({
                "Ano": range(1, len(resultados['dcf']['receitas_projetadas']) + 1),
                "Receita Projetada (R$)": resultados['dcf']['receitas_projetadas'],
                "EBITDA Projetado (R$)": resultados['dcf']['ebitda_projetado'],
                "FCF Projetado (R$)": resultados['dcf']['fcf_projetado'],
                "VP FCF (R$)": resultados['dcf']['vp_fcf']
            })
            st.dataframe(formatar_dataframe_br(dcf_df), hide_index=True)
            
            st.markdown(f"**Valor Terminal:** R$ {formatar_numero_br(resultados['dcf']['valor_terminal'])}")
            st.markdown(f"**VP Valor Terminal:** R$ {formatar_numero_br(resultados['dcf']['vp_terminal'])}")
        
        with col_det_dir:
            # Berkus
            st.markdown("#### 🚀 Valuation por Berkus")
            berkus_fatores = []
            for fator in resultados['berkus']['fatores']:
                berkus_fatores.append([fator['fator'], f"R$ {formatar_numero_br(fator['valor'])}"])
            
            berkus_df = pd.DataFrame(berkus_fatores, columns=["Fator", "Valor"])
            st.dataframe(berkus_df, hide_index=True)
            
            # Scorecard
            st.markdown("#### 📊 Valuation por Scorecard")
            scorecard_fatores = []
            for fator, valor in resultados['scorecard']['fatores'].items():
                # Converter valor numérico para texto
                if valor == 0.7:
                    valor_texto = "Baixo"
                elif valor == 1.0:
                    valor_texto = "Médio"
                else:
                    valor_texto = "Alto"
                scorecard_fatores.append([fator, valor_texto])
            
            scorecard_df = pd.DataFrame(scorecard_fatores, columns=["Fator", "Nível"])
            st.dataframe(scorecard_df, hide_index=True)
        
        # Análise e recomendação
        st.markdown("### 🤔 E aí, estou bem?")
        
        # Calcular métricas para análise
        valuation_medio = relatorio['valuation_medio']
        margem_ebitda = ebitda / receita_anual if receita_anual > 0 else 0
        
        # Determinar se está bem para o mercado
        if tamanho_empresa == "seed":
            if valuation_medio >= 2000000:  # R$ 2M
                status = "🟢 Muito bem posicionada!"
                analise = "Sua empresa está com um valuation excelente para o estágio seed. Isso indica que você tem uma base sólida e potencial de crescimento significativo."
            elif valuation_medio >= 1000000:  # R$ 1M
                status = "🟡 Bem posicionada"
                analise = "Sua empresa está bem posicionada no mercado. Há espaço para crescimento, mas a base está sólida."
            else:
                status = "🔴 Precisa de melhorias"
                analise = "Sua empresa precisa de melhorias para se destacar no mercado. Foque em validar o produto e gerar receita."
        elif tamanho_empresa == "startup":
            if valuation_medio >= 10000000:  # R$ 10M
                status = "🟢 Excelente posicionamento!"
                analise = "Sua startup está com um valuation muito forte. Você tem um produto validado e crescimento consistente."
            elif valuation_medio >= 5000000:  # R$ 5M
                status = "🟡 Bem posicionada"
                analise = "Sua startup está bem posicionada. Continue focando no crescimento e validação de mercado."
            else:
                status = "🔴 Precisa de melhorias"
                analise = "Sua startup precisa de melhorias para se destacar. Foque em crescimento de receita e validação."
        elif tamanho_empresa == "scaleup":
            if valuation_medio >= 50000000:  # R$ 50M
                status = "🟢 Posicionamento excepcional!"
                analise = "Sua scaleup está com um valuation excepcional. Você tem um modelo de negócio validado e crescimento acelerado."
            elif valuation_medio >= 25000000:  # R$ 25M
                status = "🟡 Bem posicionada"
                analise = "Sua scaleup está bem posicionada. Continue focando na expansão e otimização."
            else:
                status = "🔴 Precisa de melhorias"
                analise = "Sua scaleup precisa de melhorias para se destacar. Foque em crescimento acelerado e eficiência."
        else:  # estabelecida
            if valuation_medio >= 100000000:  # R$ 100M
                status = "🟢 Posicionamento sólido!"
                analise = "Sua empresa estabelecida está com um valuation muito sólido. Você tem um negócio maduro e lucrativo."
            elif valuation_medio >= 50000000:  # R$ 50M
                status = "🟡 Bem posicionada"
                analise = "Sua empresa está bem posicionada. Continue focando na otimização e expansão."
            else:
                status = "🔴 Precisa de melhorias"
                analise = "Sua empresa precisa de melhorias para se destacar. Foque em eficiência e crescimento sustentável."
        
        # Pontos de melhoria
        melhorias = []
        if margem_ebitda < 0.1:
            melhorias.append("**Margem EBITDA baixa**: Foque em otimizar custos e aumentar eficiência operacional")
        if receita_anual < 1000000:
            melhorias.append("**Receita baixa**: Trabalhe no crescimento de vendas e expansão de mercado")
        if tamanho_empresa in ["seed", "startup"] and not produto_lancado:
            melhorias.append("**Produto não lançado**: Priorize o lançamento do produto para validar o mercado")
        if tamanho_empresa in ["seed", "startup"] and not vendas_organicas:
            melhorias.append("**Sem vendas orgânicas**: Desenvolva estratégias de aquisição de clientes")
        
        if not melhorias:
            melhorias.append("**Continue assim!**: Sua empresa está no caminho certo")
        
        # Recomendação do programa
        if tamanho_empresa == "seed":
            programa = "**Don for Seed**"
            descricao_programa = "Programa especializado para empresas em estágio seed, focado em validação de produto e primeiras vendas."
        elif tamanho_empresa == "startup":
            programa = "**Don for Startup**"
            descricao_programa = "Programa para startups em crescimento, focado em escalabilidade e validação de mercado."
        elif tamanho_empresa == "scaleup":
            programa = "**Don for Scale-up**"
            descricao_programa = "Programa para scaleups, focado em crescimento acelerado e expansão de mercado."
        else:
            programa = "**Don for Enterprise**"
            descricao_programa = "Programa para empresas estabelecidas, focado em otimização e expansão estratégica."
        
        # Exibir análise
        st.markdown(f"**{status}**")
        st.markdown(analise)
        
        st.markdown("**📈 Pontos de Melhoria:**")
        for melhoria in melhorias:
            st.markdown(f"• {melhoria}")
        
        st.markdown("**💡 Recomendação:**")
        st.markdown(f"Baseado no estágio da sua empresa ({tamanho_empresa}), recomendamos o {programa}.")
        st.markdown(descricao_programa)
        
        # Salvar na sessão
        st.session_state["valuation_result"] = relatorio 