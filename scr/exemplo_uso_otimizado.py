"""
Exemplo de uso da versão otimizada do DadosMercado
que não carrega o arquivo CSV de 4GB inteiro.
"""

from domain.servicos.dados_mercado import DadosMercado
import pandas as pd

def exemplo_carregamento_otimizado():
    """
    Demonstra como usar a versão otimizada que carrega apenas partes do arquivo.
    """
    
    # Inicializar o serviço
    dados_mercado = DadosMercado()
    
    print("🚀 Exemplos de carregamento otimizado:")
    print("=" * 50)
    
    # 1. Carregar apenas uma região específica
    print("\n1️⃣ Carregando apenas dados do Sudeste...")
    df_sudeste = dados_mercado.carregar_dados_por_regiao(['Sudeste'], chunk_size=5000)
    print(f"   Resultado: {len(df_sudeste):,} empresas do Sudeste")
    
    # 2. Carregar apenas CNAEs específicos (TI e Telecomunicações)
    print("\n2️⃣ Carregando apenas empresas de TI e Telecomunicações...")
    df_ti = dados_mercado.carregar_dados_por_cnae(['62', '61'], chunk_size=5000)
    print(f"   Resultado: {len(df_ti):,} empresas de TI/Telecom")
    
    # 3. Carregar com filtros customizados
    print("\n3️⃣ Carregando empresas de SP e RJ do setor financeiro...")
    df_financeiro = dados_mercado.carregar_dados_receita_federal(
        filtros={
            'uf': ['SP', 'RJ'],
            'cnae': ['64', '65', '66']  # Setor financeiro
        },
        chunk_size=3000,
        max_chunks=5  # Limitar a 5 chunks para teste
    )
    print(f"   Resultado: {len(df_financeiro):,} empresas financeiras de SP/RJ")
    
    # 4. Demonstrar cache
    print("\n4️⃣ Testando cache (segunda chamada deve ser mais rápida)...")
    df_sudeste_2 = dados_mercado.carregar_dados_por_regiao(['Sudeste'], chunk_size=5000)
    print(f"   Resultado: {len(df_sudeste_2):,} empresas (usando cache)")
    
    # 5. Limpar cache
    print("\n5️⃣ Limpando cache...")
    dados_mercado.limpar_cache()
    
    return {
        'sudeste': df_sudeste,
        'ti_telecom': df_ti,
        'financeiro_sp_rj': df_financeiro
    }

def exemplo_analise_com_dados_otimizados():
    """
    Demonstra como fazer análises usando dados carregados de forma otimizada.
    """
    
    dados_mercado = DadosMercado()
    
    print("\n📊 Análise com dados otimizados:")
    print("=" * 50)
    
    # Carregar dados de TI do Sudeste
    print("Carregando dados de TI do Sudeste...")
    df_mercado = dados_mercado.carregar_dados_por_cnae(['62'], chunk_size=3000)
    
    # Simular base de clientes (exemplo)
    clientes_exemplo = pd.DataFrame({
        'cnpj': ['12345678000101', '12345678000102'],
        'cnae': ['62', '62'],
        'razao_social': ['Empresa A', 'Empresa B']
    })
    
    # Fazer análise TAM/SAM/SOM
    print("Realizando análise TAM/SAM/SOM...")
    df_cruzado = dados_mercado.cruzar_dados_mercado(df_mercado, clientes_exemplo)
    df_cruzado = dados_mercado.aplicar_segmentacao_20_30_30_20(df_cruzado, 'cnpj')
    
    matriz = dados_mercado.gerar_matriz_tam_sam_som(df_cruzado, ['regiao', 'descricao_cnae'])
    
    print("\n📈 Resultado da análise:")
    print(matriz.head())
    
    return matriz

if __name__ == "__main__":
    # Executar exemplos
    resultados = exemplo_carregamento_otimizado()
    matriz_analise = exemplo_analise_com_dados_otimizados()
    
    print("\n✅ Exemplos concluídos com sucesso!")
    print("💡 Agora o sistema carrega apenas os dados necessários, não o arquivo inteiro de 4GB.") 