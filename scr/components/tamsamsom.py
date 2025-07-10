import streamlit as st

def exibir_tamsamsom():
    st.title("Análise de TAM / SAM / SOM")
    
    if "icp_data" not in st.session_state or st.session_state["icp_data"] is None:
        st.warning("Por favor, primeiro carregue os dados na aba 'Análise de ICP'")
        return
        
    sistema = st.session_state["icp_data"]["sistema"]
    
    # Verificar se já temos dados de TAM/SAM/SOM calculados
    if "tamsamsom_data" in st.session_state and st.session_state["tamsamsom_data"] is not None:
        # Mostrar dados existentes
        dados = st.session_state["tamsamsom_data"]
        st.success("Dados de mercado carregados.")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("TAM", dados["total_tam"])
        with col2:
            st.metric("SAM", dados["total_sam"])
        with col3:
            st.metric("SOM", dados["total_som"])

        st.markdown("### Matriz TAM / SAM / SOM por TIER")
        st.dataframe(dados["matriz_tiers"])
        
        # Botão para recalcular
        if st.button("Recalcular Dados de Mercado"):
            st.session_state["tamsamsom_data"] = None
            st.rerun()
            
    else:
        # Botão para calcular pela primeira vez
        if st.button("Buscar Dados de Mercado (Simulado)"):
            sistema.configurar_api_mercado("mock")
            filtros = {"estado": "SP", "cnae": "6201-5/01"}
            sistema.carregar_dados_mercado(filtros)
            sistema.cruzar_com_clientes()
            sistema.aplicar_segmentacao_mercado("faturamento")

            total_tam = len(sistema.df_mercado)
            total_sam = (~sistema.df_mercado["é_cliente"]).sum()
            total_som = sistema.df_mercado["é_cliente"].sum()
            matriz_tiers = sistema.dados_mercado.gerar_resumo_tam_sam_som(sistema.df_mercado)

            # Salvar dados na sessão
            st.session_state["tamsamsom_data"] = {
                "total_tam": total_tam,
                "total_sam": total_sam,
                "total_som": total_som,
                "matriz_tiers": matriz_tiers
            }

            st.rerun() 