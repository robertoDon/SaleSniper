import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import locale
import io
from typing import Dict
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

def gerar_relatorio_completo_pdf(relatorio: Dict, dados_empresa: Dict):
    """Gera relatório completo em PDF com todos os detalhes."""
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=letter)
    elements = []
    
    resultados = relatorio["resultados"]
    
    # Título
    from reportlab.platypus import Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center
    )
    
    elements.append(Paragraph(f"Relatório de Valuation - {dados_empresa['nome_empresa']}", title_style))
    elements.append(Spacer(1, 20))
    
    # Informações da empresa
    elements.append(Paragraph("Informações da Empresa", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    info_empresa = [
        ["Setor", dados_empresa['setor']],
        ["Estágio", dados_empresa['tamanho_empresa']],
        ["Receita Anual", f"R$ {formatar_numero_br(dados_empresa['receita_anual'])}"],
        ["EBITDA", f"R$ {formatar_numero_br(dados_empresa['ebitda'])}"],
        ["Margem EBITDA", f"{dados_empresa['margem_ebitda']*100:.1f}%"],
        ["Crescimento Estimado", f"{dados_empresa['crescimento_anual']*100:.0f}%"]
    ]
    
    info_table = Table(info_empresa, colWidths=[150, 200])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 20))
    
    # Resultados de Valuation
    elements.append(Paragraph("Resultados de Valuation", styles['Heading2']))
    elements.append(Spacer(1, 12))
    
    # Tabela principal de resultados
    dados_principais = [
        ["Método", "Valuation (R$)", "Valuation (R$ M)"],
        ["Múltiplos (Receita)", f"R$ {formatar_numero_br(resultados['multiplos']['receita'])}", f"R$ {formatar_numero_br(resultados['multiplos']['receita']/1000000, 1)}M"],
        ["Múltiplos (EBITDA)", f"R$ {formatar_numero_br(resultados['multiplos']['ebitda'])}", f"R$ {formatar_numero_br(resultados['multiplos']['ebitda']/1000000, 1)}M"],
        ["Múltiplos (Lucro)", f"R$ {formatar_numero_br(resultados['multiplos']['lucro'])}", f"R$ {formatar_numero_br(resultados['multiplos']['lucro']/1000000, 1)}M"],
        ["DCF", f"R$ {formatar_numero_br(resultados['dcf']['valor_empresa'])}", f"R$ {formatar_numero_br(resultados['dcf']['valor_empresa']/1000000, 1)}M"],
        ["Berkus", f"R$ {formatar_numero_br(resultados['berkus']['valor_total'])}", f"R$ {formatar_numero_br(resultados['berkus']['valor_total']/1000000, 1)}M"],
        ["Scorecard", f"R$ {formatar_numero_br(resultados['scorecard']['valor_total'])}", f"R$ {formatar_numero_br(resultados['scorecard']['valor_total']/1000000, 1)}M"],
        ["Médio Ponderado", f"R$ {formatar_numero_br(relatorio['valuation_medio'])}", f"R$ {formatar_numero_br(relatorio['valuation_medio']/1000000, 1)}M"]
    ]
    
    main_table = Table(dados_principais, colWidths=[200, 150, 150])
    main_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(main_table)
    elements.append(Spacer(1, 20))
    
    # Multiplicadores utilizados
    elements.append(Paragraph("Multiplicadores Utilizados", styles['Heading3']))
    elements.append(Spacer(1, 12))
    
    mult = resultados['multiplos']['multiplos']
    mult_data = [
        ["Métrica", "Multiplicador"],
        ["Faturamento", f"{mult['receita']}x"],
        ["EBITDA", f"{mult['ebitda']}x"],
        ["Lucro Líquido", f"{mult['lucro']}x"]
    ]
    
    mult_table = Table(mult_data, colWidths=[200, 150])
    mult_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(mult_table)
    elements.append(Spacer(1, 20))
    
    # Análise DCF
    elements.append(Paragraph("Análise DCF (Discounted Cash Flow)", styles['Heading3']))
    elements.append(Spacer(1, 12))
    
    dcf_data = [
        ["Ano", "Receita Projetada (R$)", "EBITDA Projetado (R$)", "FCF Projetado (R$)", "VP FCF (R$)"]
    ]
    
    for i in range(len(resultados['dcf']['receitas_projetadas'])):
        dcf_data.append([
            str(i + 1),
            f"R$ {formatar_numero_br(resultados['dcf']['receitas_projetadas'][i])}",
            f"R$ {formatar_numero_br(resultados['dcf']['ebitda_projetado'][i])}",
            f"R$ {formatar_numero_br(resultados['dcf']['fcf_projetado'][i])}",
            f"R$ {formatar_numero_br(resultados['dcf']['vp_fcf'][i])}"
        ])
    
    dcf_table = Table(dcf_data, colWidths=[50, 120, 120, 120, 120])
    dcf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(dcf_table)
    elements.append(Spacer(1, 20))
    
    # Análise Berkus
    elements.append(Paragraph("Análise Berkus", styles['Heading3']))
    elements.append(Spacer(1, 12))
    
    berkus_data = [["Fator", "Valor (R$)"]]
    for fator in resultados['berkus']['fatores']:
        berkus_data.append([fator['fator'], f"R$ {formatar_numero_br(fator['valor'])}"])
    
    berkus_table = Table(berkus_data, colWidths=[300, 150])
    berkus_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(berkus_table)
    elements.append(Spacer(1, 20))
    
    # Análise Scorecard
    elements.append(Paragraph("Análise Scorecard", styles['Heading3']))
    elements.append(Spacer(1, 12))
    
    scorecard_data = [["Fator", "Nível"]]
    for fator, valor in resultados['scorecard']['fatores'].items():
        if valor == 0.7:
            nivel = "Baixo"
        elif valor == 1.0:
            nivel = "Médio"
        else:
            nivel = "Alto"
        scorecard_data.append([fator, nivel])
    
    scorecard_table = Table(scorecard_data, colWidths=[300, 150])
    scorecard_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(scorecard_table)
    
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

def get_valuation_data():
    return {'message': 'Valuation data placeholder'}
    
    st.markdown("""
    <h3>Calculadora de Valuation Empresarial</h3>
    
    <p>Calcule o valor da sua empresa usando múltiplos de mercado baseados em empresas similares do seu setor.</p>
    """, unsafe_allow_html=True)
    
    # Inicializar serviço de valuation
    valuation_service = ValuationService()
    
    # Formulário de dados da empresa
    st.markdown("<h3 style='text-align: center;'>Dados da Empresa</h3>", unsafe_allow_html=True)
    
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
        
        # Campo simples para despesas totais mensais
        despesas_totais_mensal = st.number_input("Despesas Totais (R$/mês)", min_value=0.0, value=66667.0, step=1000.0, 
                                               help="Ex: 66.667 - Soma de todas as despesas mensais")
        st.caption(f"Valor atual: R$ {formatar_numero_br(despesas_totais_mensal)}/mês")
        
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
            # Calcular total anual
            despesas_totais = despesas_totais_mensal * 12
            
            # Se não detalhou, usar valores padrão proporcionais
            custos_vendas = despesas_totais * 0.375  # 37.5%
            despesas_operacionais = despesas_totais * 0.25   # 25%
            despesas_adm = despesas_totais * 0.1875  # 18.75%
            despesas_marketing = despesas_totais * 0.125  # 12.5%
            outros_custos = despesas_totais * 0.0625  # 6.25%
    
    with col2:
        n_vendedores = st.number_input("Número de Vendedores", min_value=0, value=5, step=1)
        
        # Métricas qualitativas para Berkus e Scorecard
        produto_lancado = st.checkbox("Produto Lançado", value=True)
        parcerias_estrategicas = st.checkbox("Parcerias Estratégicas", value=False)
        vendas_organicas = st.checkbox("Vendas Orgânicas", value=True)
        investe_trafego_pago = st.checkbox("Invisto em tráfego pago", value=True)
        
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
        
        ebitda = receita_anual - despesas_totais
        ebitda = max(ebitda, 0)  # Não pode ser negativo
        
        # Lucro líquido será estimado baseado no EBITDA (assumindo 70% do EBITDA)
        lucro_liquido = ebitda * 0.7 if ebitda > 0 else 0
        st.markdown(f"**Lucro Líquido Estimado: R$ {formatar_numero_br(lucro_liquido)}** (70% do EBITDA)")
    
    # Fatores para Scorecard - 3 COLUNAS COM 2 FATORES CADA
    st.markdown("<h3 style='text-align: center;'>Fatores Qualitativos (Scorecard)</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Selecione o nível de cada fator:</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        equipe_score = st.selectbox("Força da Equipe", ["Baixo", "Médio", "Alto"], index=1)
        st.caption("Baixo = Equipe pequena/iniciante | Médio = Equipe experiente | Alto = Equipe especializada/executiva")
        
        produto_score = st.selectbox("Qualidade do Produto", ["Baixo", "Médio", "Alto"], index=1)
        st.caption("Baixo = MVP básico | Médio = Produto funcional | Alto = Produto diferenciado/premium")
    
    with col2:
        vendas_marketing = st.selectbox("Estratégia de Vendas/Marketing", ["Baixo", "Médio", "Alto"], index=1)
        st.caption("Baixo = Sem estratégia definida | Médio = Estratégia básica | Alto = Estratégia sofisticada")
        
        financas = st.selectbox("Saúde Financeira", ["Baixo", "Médio", "Alto"], index=1)
        st.caption("Baixo = Prejuízo/endividado | Médio = Equilibrado | Alto = Lucrativo/capital próprio")
    
    with col3:
        concorrencia = st.selectbox("Concorrência", ["Baixo", "Médio", "Alto"], index=1)
        st.caption("Baixo = Muitos concorrentes | Médio = Concorrência moderada | Alto = Poucos concorrentes")
        
        inovacao = st.selectbox("Inovação", ["Baixo", "Médio", "Alto"], index=1)
        st.caption("Baixo = Produto comum | Médio = Alguma diferenciação | Alto = Tecnologia única/patente")
    
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
            # APENAS MÚLTIPLOS
            st.markdown("### Resultado do Valuation")
            
            st.metric("Valuation por Múltiplos", f"R$ {formatar_numero_br(resultados['multiplos']['receita']/1000000, 1)}M")
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
            
            # Métricas Financeiras - MANTER COMO ESTÁ
            st.markdown("### Métricas Financeiras Calculadas")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("EBITDA", f"R$ {formatar_numero_br(ebitda)}")
            with col2:
                st.metric("Margem EBITDA", f"{margem_ebitda*100:.1f}%")
            
            # Multiplicadores Utilizados - MANTER COMO ESTÁ
            st.markdown("### Multiplicadores Utilizados")
            mult = resultados['multiplos']['multiplos']
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Faturamento", f"{mult['receita']}x")
            with col2:
                st.metric("EBITDA", f"{mult['ebitda']}x")
            with col3:
                st.metric("Lucro Líquido", f"{mult['lucro']}x")
            
            st.caption(f"Baseado em empresas do setor {setor} em estágio {tamanho_empresa}")
            
            # Botão para baixar relatório completo
            st.markdown("---")
            st.markdown("### Relatório Completo")
            
            st.markdown("Baixe o relatório completo com todos os métodos de valuation e análises detalhadas:")
            
            st.download_button(
                label="Baixar Relatório Completo (PDF)",
                data=gerar_relatorio_completo_pdf(relatorio, dados_empresa),
                file_name=f"valuation_{nome_empresa}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime='application/pdf',
                type="primary"
            )
            
            st.caption("O relatório inclui: todos os métodos de valuation, projeções DCF, análise Berkus, scorecard detalhado e recomendações estratégicas.")
            
            st.markdown("---")
            
            # Análise "E aí, estou bem?"
            st.markdown("### E aí, estou bem?")
            
            # Determinar status baseado no valuation
            valor_multiplos = resultados['multiplos']['receita']
            
            if valor_multiplos >= 10000000:  # 10M+
                status = "Muito bem posicionada!"
                analise = f"Sua empresa está com um valuation excelente para o estágio de {tamanho_empresa}. Isso indica que você tem uma base sólida e potencial de crescimento significativo."
            elif valor_multiplos >= 5000000:  # 5M-10M
                status = "Bem posicionada!"
                analise = f"Sua empresa está com um valuation muito bom para o estágio de {tamanho_empresa}. Continue focando no crescimento e otimização."
            elif valor_multiplos >= 2000000:  # 2M-5M
                status = "Posicionamento moderado"
                analise = f"Sua empresa está com um valuation adequado para o estágio de {tamanho_empresa}. Há oportunidades de melhoria e crescimento."
            else:  # < 2M
                status = "Atenção necessária"
                analise = f"Sua empresa está com um valuation baixo para o estágio de {tamanho_empresa}. Recomendamos focar em melhorias estratégicas."
            
            # Pontos positivos, alerta e negativos
            pontos_positivos = []
            pontos_alerta = []
            pontos_negativos = []
            
            if produto_lancado:
                pontos_positivos.append("**Produto já lançado**: Você tem um produto validado no mercado")
            else:
                pontos_negativos.append("**Produto não lançado**: Priorize o lançamento do produto")
            
            if margem_ebitda >= 0.25:
                pontos_positivos.append("**Margem EBITDA alta**: Excelente eficiência operacional")
            elif margem_ebitda >= 0.15:
                pontos_alerta.append("**Margem EBITDA moderada**: Há espaço para otimização de custos")
            else:
                pontos_negativos.append("**Margem EBITDA baixa**: Foque na otimização de custos")
            
            if parcerias_estrategicas:
                pontos_positivos.append("**Parcerias estratégicas**: Você tem alianças que aceleram o crescimento")
            else:
                pontos_negativos.append("**Sem parcerias estratégicas**: Busque alianças que possam acelerar seu crescimento")
            
            if vendas_organicas:
                pontos_positivos.append("**Vendas orgânicas**: Você tem um modelo de aquisição sustentável")
            else:
                pontos_alerta.append("**Dependência de tráfego pago**: Considere diversificar canais de aquisição")
            
            if investe_trafego_pago:
                pontos_positivos.append("**Investimento em marketing**: Você está investindo em crescimento")
            else:
                pontos_alerta.append("**Sem investimento em marketing**: Considere investir em aquisição de clientes")
            
            # Garantir pelo menos um ponto de cada tipo
            if not pontos_positivos:
                pontos_positivos.append("**Potencial de crescimento**: Seu setor tem boas oportunidades")
            if not pontos_alerta:
                pontos_alerta.append("**Atenção aos detalhes**: Foque na otimização de processos e eficiência")
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
            st.markdown(dica_negocio)
            
            # Botão de contato
            st.markdown("---")
            st.markdown("""
            <style>
            .stButton > button {
                background-color: #FF8C00;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            .stButton > button:hover {
                background-color: #E67E00;
                color: white;
            }
            </style>
            """, unsafe_allow_html=True)
            st.link_button(
                "Entre em contato conosco",
                "https://api.whatsapp.com/send/?phone=554892254155&text&type=phone_number&app_absent=0",
                type="primary"
            )