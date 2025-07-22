import streamlit as st
import pandas as pd
import plotly.express as px

def exibir_tamsamsom():
    st.title("Análise de TAM / SAM / SOM por CNAE (3 dígitos)")
    
    if "icp_data" not in st.session_state or st.session_state["icp_data"] is None:
        st.warning("Por favor, primeiro carregue os dados na aba 'Análise de ICP'")
        return
        
    sistema = st.session_state["icp_data"]["sistema"]
    df_clientes = sistema.df.copy()
    
    # Carregar dados de mercado
    sistema.configurar_api_mercado("mock")
    sistema.carregar_dados_mercado({})
    sistema.cruzar_com_clientes()
    sistema.aplicar_segmentacao_mercado("faturamento")
    df_mercado = sistema.df_mercado.copy()
    dados_mercado = sistema.dados_mercado

    # TAM/SAM/SOM por CNAE (3 dígitos) e região
    df_mercado['cnae3'] = df_mercado['cnae'].astype(str).str[:3]
    matriz = df_mercado.groupby(['cnae3', 'regiao']).agg(
        TAM=('cnpj', 'count'),
        SAM=('é_cliente', lambda x: (~x).sum()),
        SOM=('é_cliente', 'sum'),
        faturamento_medio=('faturamento', 'mean')
    ).reset_index()
    st.markdown("### Matriz TAM / SAM / SOM por CNAE (3 dígitos) e Região")
    st.dataframe(matriz)

    # Gráfico TAM/SAM/SOM por CNAE (3 dígitos)
    st.markdown("### Gráfico TAM/SAM/SOM por CNAE (3 dígitos)")
    matriz_cnae = matriz.groupby('cnae3').agg({'TAM':'sum','SAM':'sum','SOM':'sum'}).reset_index()
    fig = px.bar(matriz_cnae, x='cnae3', y=['TAM','SAM','SOM'], barmode='group', title='TAM/SAM/SOM por CNAE (3 dígitos)')
    st.plotly_chart(fig, use_container_width=True)

    # Oportunidades: CNAEs semelhantes (não atendidos)
    st.markdown("### Oportunidades: CNAEs semelhantes (não atendidos)")
    oportunidades = dados_mercado.sugerir_cnaes_semelhantes(df_clientes, df_mercado)
    st.dataframe(oportunidades)
    fig2 = px.bar(oportunidades, x='cnae3', y='qtd_empresas', color='regiao', title='Oportunidades de Expansão por CNAE (3 dígitos)')
    st.plotly_chart(fig2, use_container_width=True) 