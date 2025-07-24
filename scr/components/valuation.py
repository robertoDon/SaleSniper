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
            "SaaS", "E-commerce", "Fintech", "Healthtech", "Edtech", "Outros"
        ])
        tamanho_empresa = st.selectbox("Estágio da Empresa", [
            "startup", "scaleup", "estabelecida"
        ])
        receita_anual = st.number_input("Receita Anual (R$)", min_value=0.0, value=1000000.0, step=10000.0)
        ebitda = st.number_input("EBITDA (R$)", min_value=0.0, value=200000.0, step=10000.0)
        lucro_liquido = st.number_input("Lucro Líquido (R$)", min_value=0.0, value=150000.0, step=10000.0)
    
    with col2:
        margem_ebitda = st.slider("Margem EBITDA (%)", min_value=0.0, max_value=50.0, value=20.0, step=1.0) / 100
        crescimento_anual = st.slider("Crescimento Anual Esperado (%)", min_value=0.0, max_value=100.0, value=30.0, step=5.0) / 100
        usuarios_ativos = st.number_input("Usuários Ativos", min_value=0, value=5000, step=100)
        
        # Métricas qualitativas para Berkus e Scorecard
        produto_lancado = st.checkbox("Produto Lançado", value=True)
        parcerias_estrategicas = st.checkbox("Parcerias Estratégicas", value=False)
        vendas_organicas = st.checkbox("Vendas Orgânicas", value=True)
        equipe_qualificada = st.checkbox("Equipe Qualificada", value=True)
    
    # Fatores para Scorecard
    st.markdown("### 🎯 Fatores Qualitativos (Scorecard)")
    st.markdown("Avalie cada fator de 0.5 (muito baixo) a 1.5 (muito alto), onde 1.0 é neutro.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        equipe_score = st.slider("Força da Equipe", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
        tamanho_mercado = st.slider("Tamanho da Oportunidade", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
        produto_score = st.slider("Qualidade do Produto", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
    
    with col2:
        vendas_marketing = st.slider("Estratégia de Vendas/Marketing", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
        financas = st.slider("Saúde Financeira", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
        competicao = st.slider("Competição", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
    
    with col3:
        timing = st.slider("Timing de Mercado", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
        inovacao = st.slider("Inovação", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
        channels = st.slider("Canais de Distribuição", min_value=0.5, max_value=1.5, value=1.0, step=0.1)
    
    # Botão para calcular
    if st.button("💰 Calcular Valuation", type="primary"):
        
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
            "usuarios_ativos": usuarios_ativos,
            "produto_lancado": produto_lancado,
            "parcerias_estrategicas": parcerias_estrategicas,
            "vendas_organicas": vendas_organicas,
            "equipe_qualificada": equipe_qualificada,
            "equipe": equipe_score,
            "tamanho_mercado": tamanho_mercado,
            "produto": produto_score,
            "vendas_marketing": vendas_marketing,
            "financas": financas,
            "competicao": competicao,
            "timing": timing,
            "inovacao": inovacao,
            "channels": channels
        }
        
        # Gerar relatório completo
        relatorio = valuation_service.gerar_relatorio_completo(dados_empresa)
        resultados = relatorio["resultados"]
        
        # Exibir resultados
        st.markdown("### 📊 Resultados do Valuation")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Múltiplos", f"R$ {formatar_numero_br(resultados['multiplos']['receita']/1000000, 1)}M")
        with col2:
            st.metric("DCF", f"R$ {formatar_numero_br(resultados['dcf']['valor_empresa']/1000000, 1)}M")
        with col3:
            st.metric("Berkus", f"R$ {formatar_numero_br(resultados['berkus']['valor_total']/1000000, 1)}M")
        with col4:
            st.metric("Scorecard", f"R$ {formatar_numero_br(resultados['scorecard']['valor_total']/1000000, 1)}M")
        
        st.markdown(f"### 🎯 Valuation Médio Ponderado: **R$ {formatar_numero_br(relatorio['valuation_medio']/1000000, 1)}M**")
        
        # Detalhamento dos métodos
        st.markdown("### 📈 Detalhamento por Método")
        
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
            scorecard_fatores.append([fator, valor])
        
        scorecard_df = pd.DataFrame(scorecard_fatores, columns=["Fator", "Multiplicador"])
        st.dataframe(scorecard_df, hide_index=True)
        
        # Resumo final
        st.markdown("### 📋 Resumo Executivo")
        
        resumo_df = valuation_service.exportar_para_dataframe(relatorio)
        resumo_df = resumo_df[["Método", "Valuation (R$ M)", "Peso"]]
        
        st.dataframe(formatar_dataframe_br(resumo_df), hide_index=True)
        
        # Botões de exportação
        st.markdown("### 📤 Exportar Resultados")
        exibir_botoes_exportacao(resumo_df, f"valuation_{nome_empresa.replace(' ', '_')}")
        
        # Salvar na sessão
        st.session_state["valuation_result"] = relatorio 