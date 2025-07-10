import streamlit as st
import pandas as pd
from services.faixas_ticket import identificar_faixa, ajuste_por_faixa, base_taxas
from services.funil import calcular_funil, calcular_projecao
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import xlsxwriter
import locale
from datetime import datetime, timedelta
import calendar
import holidays
import numpy as np

# Configurar locale para português do Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Definir etapas do funil globalmente
etapas = ["Lead", "MQL", "SAL", "Agendamento", "Reunião Ocorrida", "Oportunidade (SQL)", "Venda"]

def formatar_numero_br(valor, casas_decimais=0):
    """Formata número para o padrão brasileiro."""
    if isinstance(valor, (int, float)):
        # Se for um número inteiro ou se o valor for muito próximo de um inteiro
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
    
    # Converter DataFrame para lista de listas
    data = [df.columns.tolist()] + df.values.tolist()
    
    # Criar tabela
    table = Table(data)
    
    # Estilizar tabela
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

def calcular_progressao_metas(meta_final, meses_restantes, n_vendedores_inicial):
    """Calcula a progressão de metas e número de vendedores ao longo dos meses."""
    n_meses = len(meses_restantes)
    
    # Criar progressão exponencial suave para as metas
    # Começa com 40% da meta final e termina com 100%
    progressao = np.linspace(0.4, 1.0, n_meses)
    metas_mensais = [meta_final * p for p in progressao]
    
    # Calcular número de vendedores necessários para cada mês
    vendedores_por_mes = []
    for i, meta in enumerate(metas_mensais):
        # Começa com o número inicial de vendedores
        if i == 0:
            vendedores_por_mes.append(n_vendedores_inicial)
        else:
            # Calcula quantos vendedores adicionais são necessários
            meta_anterior = metas_mensais[i-1]
            vendedores_anterior = vendedores_por_mes[i-1]
            
            # Se a meta aumentou mais de 20% em relação ao mês anterior, adiciona um vendedor
            if meta > meta_anterior * 1.2:
                vendedores_por_mes.append(vendedores_anterior + 1)
            else:
                vendedores_por_mes.append(vendedores_anterior)
    
    return metas_mensais, vendedores_por_mes

def ajustar_meta_por_vendedores(meta_mensal, n_vendedores, dias_uteis, etapa, taxas, max_reunioes_por_dia=4):
    """Ajusta a meta mensal baseada no número de vendedores e limite de reuniões por dia."""
    # Calcula o máximo de reuniões possíveis por mês
    max_reunioes_mes = n_vendedores * dias_uteis * max_reunioes_por_dia
    
    # Se for a etapa de reuniões, aplica o limite direto
    if etapa == "Reunião Ocorrida":
        return min(meta_mensal, max_reunioes_mes)
    
    # Para outras etapas, calcula quantas são necessárias para atingir a meta de reuniões
    # Encontra a taxa de conversão até reuniões
    taxa_ate_reunioes = 1.0
    for e in etapas:
        if e == "Reunião Ocorrida":
            break
        if e in taxas:
            taxa_ate_reunioes *= taxas[e]
    
    # Calcula quantas são necessárias na etapa atual para atingir a meta de reuniões
    meta_ajustada = meta_mensal / taxa_ate_reunioes
    
    return round(meta_ajustada)

def get_dias_uteis_mes(ano, mes):
    """Calcula os dias úteis do mês considerando:
    - Feriados nacionais
    - Dias antes e depois de feriados contam como meio dia
    """
    # Lista de feriados nacionais
    feriados = holidays.BR()
    
    # Obter o primeiro e último dia do mês
    primeiro_dia = datetime(ano, mes, 1)
    ultimo_dia = datetime(ano, mes, calendar.monthrange(ano, mes)[1])
    
    # Lista de todos os dias do mês
    dias = [primeiro_dia + timedelta(days=x) for x in range((ultimo_dia - primeiro_dia).days + 1)]
    
    # Calcular dias úteis
    dias_uteis = 0
    for dia in dias:
        # Se for fim de semana, pula
        if dia.weekday() >= 5:  # 5 = Sábado, 6 = Domingo
            continue
            
        # Se for feriado, pula
        if dia in feriados:
            continue
            
        # Se for dia antes ou depois de feriado, conta como meio dia
        dia_anterior = dia - timedelta(days=1)
        dia_posterior = dia + timedelta(days=1)
        if dia_anterior in feriados or dia_posterior in feriados:
            dias_uteis += 0.5
        else:
            dias_uteis += 1
    
    # Arredondar para baixo
    return int(dias_uteis)

def get_meses_restantes():
    """Retorna lista de meses restantes do ano atual a partir do próximo mês."""
    hoje = datetime.now()
    ano_atual = hoje.year
    mes_atual = hoje.month
    
    # Lista de meses em português
    meses_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    
    # Retorna meses restantes
    return [(meses_pt[i-1], i, ano_atual) for i in range(mes_atual + 1, 13)]

def ajustar_meta_por_dias_uteis(meta_mensal, dias_uteis_mes, dias_uteis_padrao=21):
    """Ajusta a meta mensal baseada na quantidade de dias úteis do mês."""
    return round(meta_mensal * (dias_uteis_mes / dias_uteis_padrao))

def exibir_calculadora():
    # Aplicar cor laranja ao título principal
    st.markdown("<h1 style='color: #FF8C00;'>Calculadora de Metas & Projeção de Funil</h1>", unsafe_allow_html=True)

    # Verificar se temos dados do ICP
    if "icp_data" not in st.session_state or st.session_state["icp_data"] is None:
        st.warning("Por favor, primeiro carregue os dados na aba 'Análise de ICP'")
        return

    meses_restantes = get_meses_restantes()

    # Carregar valores salvos da sessão ou usar padrões
    valores_salvos = st.session_state.get("metas_data", {
        "segmento": list(base_taxas.keys())[0],
        "tipo_obj": "Faturamento",
        "val_obj": 1_000_000.0,
        "n_vend": 5
    })

    segmento = st.selectbox("Segmento da Empresa", list(base_taxas.keys()), 
                           index=list(base_taxas.keys()).index(valores_salvos["segmento"]))
    tipo_obj = st.selectbox("Tipo de Objetivo Anual", ["Clientes", "MRR", "Faturamento"], 
                           index=["Clientes", "MRR", "Faturamento"].index(valores_salvos["tipo_obj"]))
    val_obj = st.number_input("Valor Anual de Objetivo", min_value=0.0, 
                             value=valores_salvos["val_obj"], step=10_000.0, format="%.2f")

    col1, col2 = st.columns(2)
    with col1:
        n_vend = st.number_input("Número Inicial de Vendedores", min_value=1, 
                                value=valores_salvos["n_vend"], step=1)
    with col2:
        # Usar a média simples da coluna ticket_medio
        df = st.session_state["icp_data"]["df"]
        ticket = df["ticket_medio"].mean()
        # Aplicar cor laranja ao valor do Ticket Médio
        st.markdown(f"<p style='color: #F0F0F0; font-size: 1.2em;'>Ticket Médio (R$)</p>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color: #FF8C00;'>{formatar_numero_br(ticket)}</h3>", unsafe_allow_html=True)

    # Salvar valores atuais na sessão
    st.session_state["metas_data"] = {
        "segmento": segmento,
        "tipo_obj": tipo_obj,
        "val_obj": val_obj,
        "n_vend": n_vend
    }

    # Botões para calcular/recalcular
    col1, col2 = st.columns([1, 3])
    with col1:
        calcular = st.button("Calcular Metas e Funil")
        if "metas_calculadas" in st.session_state:
            recalcular = st.button("Recalcular")
        else:
            recalcular = False

    # Mostrar resultados apenas se já foram calculados e não estamos recalculando
    if "metas_calculadas" in st.session_state and not recalcular and not calcular:
        dados = st.session_state["metas_calculadas"]
        
        # Aplicar cor laranja ao título da seção
        st.markdown("### <span style='color: #FF8C00;'>Taxas de Conversão Utilizadas:</span>", unsafe_allow_html=True)
        
        # Criar DataFrame para taxas editáveis
        taxas_editaveis = pd.DataFrame({
            "Etapa": dados["df_taxas"]["Etapa"],
            "Taxa Usada": dados["df_taxas"]["Taxa Usada"].astype(str).str.rstrip("%").astype(float)
        })
        
        # Configurar o editor de dados
        taxas_editadas = st.data_editor(
            taxas_editaveis,
            column_config={
                "Etapa": st.column_config.TextColumn(
                    "Etapa",
                    disabled=True
                ),
                "Taxa Usada": st.column_config.NumberColumn(
                    "Taxa Usada (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    format="%.0f"
                )
            },
            hide_index=True
        )
        
        # Botão para restaurar taxas padrão
        if st.button("Restaurar Taxas Padrão"):
            taxas_editadas = taxas_editaveis.copy()
            st.rerun()
        
        # Converter taxas editadas para o formato do funil (removendo o % e convertendo para float)
        taxas_atualizadas = {etapa: float(str(taxa).rstrip("%"))/100 for etapa, taxa in zip(taxas_editadas["Etapa"], taxas_editadas["Taxa Usada"])}
        
        # Recalcular projeção com as taxas atualizadas
        proj = calcular_projecao(etapas, taxas_atualizadas, dados["metas"].loc["Clientes/Mês", "Valor"])
        
        # Criar DataFrame com meses restantes e dias úteis
        df_proj = pd.DataFrame({
            "Mês": [mes for mes, _, _ in meses_restantes],
            "Dias Úteis": [get_dias_uteis_mes(ano, mes) for _, mes, ano in meses_restantes]
        })
        
        # Adicionar coluna de Vendedores e inicializar
        df_proj["Vendedores"] = 0 # Inicializar com zero

        # Calcular meta mensal de clientes/vendas base
        meta_clients_mensal_base = dados["metas"].loc["Clientes/Mês", "Valor"]

        # Calcular o total de clientes/vendas a serem atingidos nos meses restantes
        total_clients_restante = meta_clients_mensal_base * 12 # Usando a meta mensal base para calcular o total anual

        # Se o objetivo anual foi definido como MRR ou Faturamento, converter de volta para clientes usando o ticket médio
        if tipo_obj in ["MRR", "Faturamento"]:
            ticket_medio_atual = df["ticket_medio"].mean()
            if ticket_medio_atual > 0:
                # Ajustar para o total necessário no período restante (considerando meses restantes)
                total_clients_restante = val_obj / ticket_medio_atual
                if tipo_obj == "MRR": # MRR é anualizado na meta geral, então dividimos por 12 para obter o valor mensal
                    total_clients_restante = total_clients_restante / 12 * len(meses_restantes)
                else: # Faturamento Anual
                    total_clients_restante = total_clients_restante / 12 * len(meses_restantes)
            else:
                total_clients_restante = 0

        # Distribuir a meta total de clientes/vendas gradualmente ao longo dos meses restantes
        # Usando uma progressão linear simples do 1º ao último mês restante
        # A meta do primeiro mês será proporcionalmente menor e do último maior
        num_meses_restantes = len(meses_restantes)
        metas_clientes_mensais_graduais = np.linspace(
            total_clients_restante / num_meses_restantes * 0.7, # Começa com 70% da média para um crescimento suave
            total_clients_restante / num_meses_restantes * 1.3, # Termina com 130% da média
            num_meses_restantes
        )

        # Iterar sobre os meses restantes para calcular as metas por etapa
        for i, (mes_nome, mes_num, ano) in enumerate(meses_restantes):
            dias_uteis = df_proj.loc[i, "Dias Úteis"]
            
            # A meta de vendas para este mês é a meta gradual calculada
            meta_venda_mensal = metas_clientes_mensais_graduais[i]
            
            # 1. Calcular Reuniões Ocorridas Necessárias para atingir a meta de Clientes/Vendas
            reunioes_necessarias = 0
            # Trabalhando de trás para frente: Venda <- Oportunidade (SQL) <- Reunião Ocorrida
            taxa_oportunidade_venda = taxas_atualizadas.get("Oportunidade (SQL)", 0.0)
            taxa_reuniao_oportunidade = taxas_atualizadas.get("Reunião Ocorrida", 0.0)

            if taxa_oportunidade_venda > 0 and taxa_reuniao_oportunidade > 0:
                 reunioes_necessarias = meta_venda_mensal / taxa_oportunidade_venda / taxa_reuniao_oportunidade

            # Arredondar para cima, pois não se pode ter fração de reunião
            reunioes_necessarias = int(np.ceil(reunioes_necessarias))
            
            # 2. Calcular o número mínimo de vendedores necessários para realizar essas reuniões
            vendedores_necessarios_min = 0
            if dias_uteis > 0 and 4 > 0: # 4 reuniões por dia por vendedor
                vendedores_necessarios_min = reunioes_necessarias / (dias_uteis * 4)
            vendedores_necessarios_min = int(np.ceil(vendedores_necessarios_min)) # Arredonda para cima

            # 3. Ajustar o número de vendedores para o mês atual
            if i > 0:
                 vendedores_no_mes_anterior = df_proj.loc[i-1, "Vendedores"]
                 # O número de vendedores no mês atual é o maior entre o do mês anterior e o mínimo necessário
                 df_proj.loc[i, "Vendedores"] = max(vendedores_no_mes_anterior, vendedores_necessarios_min)
            else:
                 # Primeiro mês usa o maior entre o número inicial de vendedores e o mínimo necessário
                 df_proj.loc[i, "Vendedores"] = max(n_vend, vendedores_necessarios_min)
            
            # 4. Preencher a linha do DataFrame com as metas para o mês
            df_proj.loc[i, "Reunião Ocorrida Necessários"] = reunioes_necessarias

            # Calcular etapas anteriores (trabalhando de trás para frente a partir de Reunião Ocorrida)
            meta_atual = reunioes_necessarias
            # Itera sobre as etapas de trás para frente, excluindo a última ('Venda') e 'Reunião Ocorrida'
            for etapa in reversed(etapas[:etapas.index("Reunião Ocorrida")]):
                # A taxa de conversão usada é da etapa ATUAL para a PRÓXIMA etapa no funil
                if etapa in taxas_atualizadas and taxas_atualizadas[etapa] > 0:
                    meta_atual = meta_atual / taxas_atualizadas[etapa]
                    df_proj.loc[i, f"{etapa} Necessários"] = int(np.ceil(meta_atual))
                else:
                     df_proj.loc[i, f"{etapa} Necessários"] = 0 # Evita divisão por zero ou taxa inexistente

            # Calcular etapas posteriores (trabalhando de frente para trás a partir de Reunião Ocorrida)
            meta_atual = reunioes_necessarias
            # Itera sobre as etapas de frente para trás, começando após 'Reunião Ocorrida'
            for etapa in etapas[etapas.index("Reunião Ocorrida") + 1:]:
                 # A taxa de conversão usada é da etapa ANTERIOR para a etapa ATUAL
                 etapa_anterior = etapas[etapas.index(etapa) - 1]
                 if etapa_anterior in taxas_atualizadas:
                    meta_atual = meta_atual * taxas_atualizadas[etapa_anterior]
                    df_proj.loc[i, f"{etapa} Necessários"] = round(meta_atual)
                 else:
                    df_proj.loc[i, f"{etapa} Necessários"] = 0 # Taxa de conversão inexistente
            
        st.markdown("**Metas Gerais**")
        metas_formatadas = dados["metas"].copy()
        metas_formatadas["Valor"] = metas_formatadas["Valor"].apply(formatar_numero_br)
        # Aplicar estilos à tabela de Metas Gerais - cores e fontes são limitadas em tabelas padrão do Streamlit
        # Podemos tentar aplicar um fundo escuro e texto claro via CSS global se necessário
        st.table(metas_formatadas)

        # Aplicar cor laranja ao título da seção
        st.markdown("### <span style='color: #FF8C00;'>Projeção Mensal de Funil Necessário</span>", unsafe_allow_html=True)
        df_proj_formatado = formatar_dataframe_br(df_proj)
        # Aplicar estilos ao DataFrame de Projeção - cores e fontes são limitadas em dataframes padrão do Streamlit
        # Podemos tentar aplicar um fundo escuro e texto claro via CSS global se necessário
        st.dataframe(df_proj_formatado, hide_index=True)
        
        # Botões de exportação apenas para a projeção do funil
        exibir_botoes_exportacao(df_proj, "projecao_funil")

    # Calcular apenas quando solicitado
    elif calcular or recalcular:
        if tipo_obj == "Clientes":
            obj_clients = val_obj
            obj_revenue = val_obj * ticket
        elif tipo_obj == "MRR":
            obj_revenue = val_obj * 12
            obj_clients = obj_revenue / ticket if ticket else 0
        else:
            obj_revenue = val_obj
            obj_clients = obj_revenue / ticket if ticket else 0

        meta_clients_mes = obj_clients / 12
        meta_rev_mes     = obj_revenue / 12
        meta_rev_vend    = meta_rev_mes / n_vend

        faixa = identificar_faixa(segmento, ticket)
        ajuste = ajuste_por_faixa[faixa]
        taxas = calcular_funil(base_taxas[segmento], ajuste)

        df_taxas = pd.DataFrame([
            {"Etapa": etapa, "Taxa Usada": taxas[etapa]*100} for etapa in etapas[:-1]
        ])
        
        st.markdown("**Taxas de Conversão Utilizadas:**")
        taxas_editadas = st.data_editor(
            df_taxas,
            hide_index=True,
            column_config={
                "Etapa": st.column_config.TextColumn("Etapa", disabled=True),
                "Taxa Usada": st.column_config.NumberColumn(
                    "Taxa Usada (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=1.0,
                    format="%.0f"
                )
            }
        )
        
        # Botão para restaurar taxas padrão
        if st.button("Restaurar Taxas Padrão"):
            taxas = calcular_funil(base_taxas[segmento], ajuste)
            taxas_editadas = pd.DataFrame([
                {"Etapa": etapa, "Taxa Usada": taxas[etapa]*100} for etapa in etapas[:-1]
            ])
            st.rerun()
        
        # Converter taxas editadas para o formato do funil (removendo o % e convertendo para float)
        taxas_atualizadas = {etapa: float(str(taxa).rstrip("%"))/100 for etapa, taxa in zip(taxas_editadas["Etapa"], taxas_editadas["Taxa Usada"])}
        
        # Recalcular projeção com as taxas atualizadas
        proj = calcular_projecao(etapas, taxas_atualizadas, meta_clients_mes)

        # Criar DataFrame com meses restantes e dias úteis
        df_proj = pd.DataFrame({
            "Mês": [mes for mes, _, _ in meses_restantes],
            "Dias Úteis": [get_dias_uteis_mes(ano, mes) for _, mes, ano in meses_restantes]
        })
        
        # Adicionar coluna de Vendedores e inicializar
        df_proj["Vendedores"] = 0 # Inicializar com zero

        # Calcular meta mensal de clientes/vendas base
        meta_clients_mensal_base = meta_clients_mes

        # Calcular o total de clientes/vendas a serem atingidos nos meses restantes
        total_clients_restante = meta_clients_mensal_base * 12 # Usando a meta mensal base para calcular o total anual

        # Distribuir a meta total de clientes/vendas gradualmente ao longo dos meses restantes
        # Usando uma progressão linear simples do 1º ao último mês restante
        # A meta do primeiro mês será proporcionalmente menor e do último maior
        num_meses_restantes = len(meses_restantes)
        metas_clientes_mensais_graduais = np.linspace(
            total_clients_restante / num_meses_restantes * 0.7, # Começa com 70% da média para um crescimento suave
            total_clients_restante / num_meses_restantes * 1.3, # Termina com 130% da média
            num_meses_restantes
        )

        # Iterar sobre os meses restantes para calcular as metas por etapa
        for i, (mes_nome, mes_num, ano) in enumerate(meses_restantes):
            dias_uteis = df_proj.loc[i, "Dias Úteis"]
            
            # A meta de vendas para este mês é a meta gradual calculada
            meta_venda_mensal = metas_clientes_mensais_graduais[i]
            
            # 1. Calcular Reuniões Ocorridas Necessárias para atingir a meta de Clientes/Vendas
            reunioes_necessarias = 0
            # Trabalhando de trás para frente: Venda <- Oportunidade (SQL) <- Reunião Ocorrida
            taxa_oportunidade_venda = taxas_atualizadas.get("Oportunidade (SQL)", 0.0)
            taxa_reuniao_oportunidade = taxas_atualizadas.get("Reunião Ocorrida", 0.0)

            if taxa_oportunidade_venda > 0 and taxa_reuniao_oportunidade > 0:
                 reunioes_necessarias = meta_venda_mensal / taxa_oportunidade_venda / taxa_reuniao_oportunidade

            # Arredondar para cima, pois não se pode ter fração de reunião
            reunioes_necessarias = int(np.ceil(reunioes_necessarias))
            
            # 2. Calcular o número mínimo de vendedores necessários para realizar essas reuniões
            vendedores_necessarios_min = 0
            if dias_uteis > 0 and 4 > 0: # 4 reuniões por dia por vendedor
                vendedores_necessarios_min = reunioes_necessarias / (dias_uteis * 4)
            vendedores_necessarios_min = int(np.ceil(vendedores_necessarios_min)) # Arredonda para cima

            # 3. Ajustar o número de vendedores para o mês atual
            if i > 0:
                 vendedores_no_mes_anterior = df_proj.loc[i-1, "Vendedores"]
                 # O número de vendedores no mês atual é o maior entre o do mês anterior e o mínimo necessário
                 df_proj.loc[i, "Vendedores"] = max(vendedores_no_mes_anterior, vendedores_necessarios_min)
            else:
                 # Primeiro mês usa o maior entre o número inicial de vendedores e o mínimo necessário
                 df_proj.loc[i, "Vendedores"] = max(n_vend, vendedores_necessarios_min)
            
            # 4. Preencher a linha do DataFrame com as metas para o mês
            df_proj.loc[i, "Reunião Ocorrida Necessários"] = reunioes_necessarias

            # Calcular etapas anteriores (trabalhando de trás para frente a partir de Reunião Ocorrida)
            meta_atual = reunioes_necessarias
            # Itera sobre as etapas de trás para frente, excluindo a última ('Venda') e 'Reunião Ocorrida'
            for etapa in reversed(etapas[:etapas.index("Reunião Ocorrida")]):
                # A taxa de conversão usada é da etapa ATUAL para a PRÓXIMA etapa no funil
                if etapa in taxas_atualizadas and taxas_atualizadas[etapa] > 0:
                    meta_atual = meta_atual / taxas_atualizadas[etapa]
                    df_proj.loc[i, f"{etapa} Necessários"] = int(np.ceil(meta_atual))
                else:
                     df_proj.loc[i, f"{etapa} Necessários"] = 0 # Evita divisão por zero ou taxa inexistente

            # Calcular etapas posteriores (trabalhando de frente para trás a partir de Reunião Ocorrida)
            meta_atual = reunioes_necessarias
            # Itera sobre as etapas de frente para trás, começando após 'Reunião Ocorrida'
            for etapa in etapas[etapas.index("Reunião Ocorrida") + 1:]:
                 # A taxa de conversão usada é da etapa ANTERIOR para a etapa ATUAL
                 etapa_anterior = etapas[etapas.index(etapa) - 1]
                 if etapa_anterior in taxas_atualizadas:
                    meta_atual = meta_atual * taxas_atualizadas[etapa_anterior]
                    df_proj.loc[i, f"{etapa} Necessários"] = round(meta_atual)
                 else:
                    df_proj.loc[i, f"{etapa} Necessários"] = 0 # Taxa de conversão inexistente
            
        st.markdown("**Metas Gerais**")
        metas = pd.DataFrame([
            {"Descrição": "Clientes/Mês",     "Valor": round(meta_clients_mensal_base)},
            {"Descrição": "Receita/Mês (R$)", "Valor": round(meta_rev_mes)},
            {"Descrição": "Receita/Vendedor (R$)", "Valor": round(meta_rev_vend)},
        ]).set_index("Descrição")
        
        metas_formatadas = metas.copy()
        metas_formatadas["Valor"] = metas_formatadas["Valor"].apply(formatar_numero_br)
        # Aplicar estilos à tabela de Metas Gerais
        st.table(metas_formatadas)

        # Aplicar cor laranja ao título da seção
        st.markdown("### <span style='color: #FF8C00;'>Projeção Mensal de Funil Necessário</span>", unsafe_allow_html=True)
        df_proj_formatado = formatar_dataframe_br(df_proj)
        # Aplicar estilos ao DataFrame de Projeção
        st.dataframe(df_proj_formatado, hide_index=True)
        
        # Botões de exportação apenas para a projeção do funil
        exibir_botoes_exportacao(df_proj, "projecao_funil")

        # Salvar resultados na sessão
        st.session_state["metas_calculadas"] = {
            "faixa": faixa,
            "ajuste": ajuste,
            "df_taxas": taxas_editadas,
            "metas": metas,
            "df_proj": df_proj
        }
