import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def get_tamsamsom_data():
    return {'message': 'TAM/SAM/SOM data placeholder'}
    
    # Limpar cache se necessário
    if st.button("🔄 Limpar Cache"):
        st.cache_data.clear()
        st.rerun()
    
    # Explicação sobre TAM/SAM/SOM
    with st.expander("ℹ️ O que são TAM, SAM e SOM?"):
        st.markdown("""
        **TAM (Total Addressable Market):** Total de empresas no mercado que poderiam usar seu produto/serviço.
        
        **SAM (Serviceable Available Market):** Subconjunto do TAM que sua empresa pode realisticamente alcançar.
        
        **SOM (Serviceable Obtainable Market):** Quantidade de clientes que você já possui (market share atual).
        
        **Por que SOM pode ser 0?** 
        - Se os CNPJs dos seus clientes não estiverem na base da Receita Federal
        - Se houver diferença no formato dos CNPJs entre as bases
        - Se os clientes não tiverem CNPJ válido
        """)
    
    if "icp_data" not in st.session_state or st.session_state["icp_data"] is None:
        st.warning("⚠️ Por favor, primeiro carregue os dados na aba '📊 Análise de ICP'")
        return
        
    sistema = st.session_state["icp_data"]["sistema"]
    df_clientes = sistema.df.copy()
    
    # Verificar se há coluna CNAE nos clientes
    if 'cnae' not in df_clientes.columns:
        st.error("❌ Base de clientes não possui coluna 'cnae'. Execute primeiro a análise de ICP com dados que contenham CNAE.")
        return
    
    with st.spinner("🔄 Carregando dados da Receita Federal..."):
        # Carregar dados reais da Receita Federal
        from domain.servicos.dados_mercado import DadosMercado
        dados_mercado = DadosMercado()
        
        try:
            df_mercado = dados_mercado.carregar_dados_receita_federal()
        except Exception as e:
            st.error(f"❌ Erro ao carregar dados da Receita Federal: {str(e)}")
            st.info("📊 Usando dados de exemplo para demonstração...")
            df_mercado = dados_mercado._gerar_dados_exemplo()
    
    # Calcular TAM/SAM/SOM
    with st.spinner("🔄 Calculando TAM/SAM/SOM..."):
        try:
            matriz = dados_mercado.calcular_tam_sam_som_por_cnae(df_clientes, df_mercado)
        except Exception as e:
            st.error(f"❌ Erro ao calcular TAM/SAM/SOM: {str(e)}")
            return
    
    # Debug: Verificar por que SOM é 0
    st.sidebar.markdown("### 🔍 Debug - Por que SOM é 0?")
    if st.sidebar.button("🔍 Verificar Cruzamento de CNPJs"):
        # Verificar CNPJs dos clientes
        cnpjs_clientes = df_clientes['cnpj'].astype(str).unique()
        cnpjs_mercado = df_mercado['cnpj'].astype(str).unique()
        
        # Verificar quantos CNPJs dos clientes estão no mercado
        cnpjs_encontrados = set(cnpjs_clientes) & set(cnpjs_mercado)
        
        st.sidebar.write(f"📊 CNPJs dos clientes: {len(cnpjs_clientes)}")
        st.sidebar.write(f"📊 CNPJs no mercado: {len(cnpjs_mercado)}")
        st.sidebar.write(f"✅ CNPJs encontrados: {len(cnpjs_encontrados)}")
        
        if len(cnpjs_encontrados) == 0:
            st.sidebar.error("❌ Nenhum CNPJ dos clientes foi encontrado na base da Receita Federal!")
            st.sidebar.write("**Possíveis causas:**")
            st.sidebar.write("- Formato diferente dos CNPJs")
            st.sidebar.write("- CNPJs inválidos na base de clientes")
            st.sidebar.write("- Base da Receita Federal desatualizada")
            
            # Mostrar alguns exemplos
            st.sidebar.write("**Exemplos de CNPJs dos clientes:**")
            for cnpj in cnpjs_clientes[:5]:
                st.sidebar.write(f"- {cnpj}")
    
    # Exibir estatísticas gerais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Total de Empresas (TAM)", f"{matriz['TAM'].sum():,}")
    with col2:
        st.metric("🎯 Mercado Atendível (SAM)", f"{matriz['SAM'].sum():,}")
    with col3:
        st.metric("✅ Clientes Atuais (SOM)", f"{matriz['SOM'].sum():,}")
    with col4:
        taxa_penetracao = (matriz['SOM'].sum() / matriz['TAM'].sum()) * 100 if matriz['TAM'].sum() > 0 else 0
        st.metric("📈 Taxa de Penetração", f"{taxa_penetracao:.2f}%")
    
    st.markdown("---")
    
    # Relatório de similaridade
    with st.expander("📊 Relatório Detalhado por CNAE dos Clientes"):
        try:
            relatorio_similaridade = dados_mercado.gerar_relatorio_similaridade_cnae(df_clientes, df_mercado)
            
            st.markdown("#### 📈 Potencial de Expansão por CNAE dos Clientes")
            
            # Formatar números
            relatorio_display = relatorio_similaridade.copy()
            for col in ['qtd_clientes_atual', 'qtd_empresas_mercado', 'potencial_expansao']:
                relatorio_display[col] = relatorio_display[col].apply(lambda x: f"{x:,.0f}")
            
            st.dataframe(relatorio_display, use_container_width=True)
            
            # Gráfico de potencial por descrição
            st.markdown("#### 📊 Potencial de Expansão por CNAE")
            potencial_por_cnae = relatorio_similaridade.groupby('descricao_cliente')['potencial_expansao'].sum().sort_values(ascending=False)
            
            fig_secao = px.bar(
                x=potencial_por_cnae.values,
                y=potencial_por_cnae.index,
                orientation='h',
                title='Potencial de Expansão por CNAE',
                labels={'x': 'Potencial de Expansão', 'y': 'CNAE'}
            )
            st.plotly_chart(fig_secao, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Erro ao gerar relatório de similaridade: {str(e)}")
    
    # Tabela TAM/SAM/SOM por CNAE e Região
    st.markdown("### 📋 Matriz TAM / SAM / SOM por CNAE e Região")
    
    # Formatar números na tabela
    matriz_display = matriz.copy()
    for col in ['TAM', 'SAM', 'SOM', 'Tier_1', 'Tier_2', 'Tier_3', 'Tier_4']:
        if col in matriz_display.columns:
            matriz_display[col] = matriz_display[col].apply(lambda x: f"{x:,}")
    
    st.dataframe(matriz_display, use_container_width=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 TAM/SAM/SOM por CNAE (Top 15)")
        # Top 15 CNAEs por TAM
        top_cnaes = matriz.groupby('descricao_cnae').agg({
            'TAM': 'sum',
            'SAM': 'sum', 
            'SOM': 'sum'
        }).sort_values('TAM', ascending=False).head(15).reset_index()
        
        fig = px.bar(
            top_cnaes, 
            x='descricao_cnae', 
            y=['TAM', 'SAM', 'SOM'], 
            barmode='group',
            title='Top 15 CNAEs por TAM',
            labels={'value': 'Quantidade de Empresas', 'variable': 'Métrica', 'descricao_cnae': 'CNAE'}
        )
        fig.update_layout(height=500, xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🗺️ Distribuição por Região")
        # Distribuição por região
        regiao_stats = matriz.groupby('regiao').agg({
            'TAM': 'sum',
            'SAM': 'sum',
            'SOM': 'sum'
        }).reset_index()
        
        fig2 = px.pie(
            regiao_stats, 
            values='TAM', 
            names='regiao',
            title='Distribuição TAM por Região'
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Oportunidades de expansão
    st.markdown("---")
    st.markdown("### 🚀 Oportunidades de Expansão: CNAEs Não Atendidos")
    
    with st.spinner("🔄 Identificando oportunidades..."):
        try:
            oportunidades = dados_mercado.sugerir_cnaes_semelhantes(df_clientes, df_mercado)
        except Exception as e:
            st.error(f"❌ Erro ao identificar oportunidades: {str(e)}")
            return
    
    if len(oportunidades) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📋 Top 20 CNAEs para Expansão")
            oportunidades_display = oportunidades.head(20).copy()
            oportunidades_display['qtd_empresas'] = oportunidades_display['qtd_empresas'].apply(lambda x: f"{x:,}")
            st.dataframe(oportunidades_display, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Oportunidades por Região")
            fig3 = px.bar(
                oportunidades.head(20), 
                x='descricao_cnae', 
                y='qtd_empresas', 
                color='regiao',
                title='Top 20 CNAEs para Expansão por Região'
            )
            fig3.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig3, use_container_width=True)
        
        # Insights automáticos
        st.markdown("### 💡 Insights Automáticos")
        
        # Top 3 oportunidades por região
        top_por_regiao = oportunidades.groupby('regiao').head(3)
        
        for regiao in top_por_regiao['regiao'].unique():
            regiao_data = top_por_regiao[top_por_regiao['regiao'] == regiao]
            st.markdown(f"**{regiao}:**")
            for _, row in regiao_data.iterrows():
                st.markdown(f"- {row['descricao_cnae']}: {row['qtd_empresas']:,} empresas potenciais")
        
        # CNAEs com maior potencial
        st.markdown(f"**🎯 Maior Oportunidade:** {oportunidades.iloc[0]['descricao_cnae']} com {oportunidades.iloc[0]['qtd_empresas']:,} empresas na região {oportunidades.iloc[0]['regiao']}")
        
    else:
        st.info("ℹ️ Não foram identificadas oportunidades de expansão com os dados atuais.")
    
    # Download dos dados
    st.markdown("---")
    st.markdown("### 📥 Download dos Dados")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_matriz = matriz.to_csv(index=False)
        st.download_button(
            label="📊 Download Matriz TAM/SAM/SOM",
            data=csv_matriz,
            file_name="matriz_tam_sam_som.csv",
            mime="text/csv"
        )
    
    with col2:
        if len(oportunidades) > 0:
            csv_oportunidades = oportunidades.to_csv(index=False)
            st.download_button(
                label="🚀 Download Oportunidades",
                data=csv_oportunidades,
                file_name="oportunidades_expansao.csv",
                mime="text/csv"
            ) 