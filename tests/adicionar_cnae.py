"""
Script para adicionar CNAEs ao arquivo de teste baseado no segmento.
"""

import pandas as pd

def adicionar_cnae_por_segmento():
    """
    Adiciona CNAEs apropriados baseados no segmento de cada cliente.
    """
    
    # Ler o arquivo atual
    df = pd.read_excel('tests/clientes_teste.xlsx')
    
    # Mapeamento de segmentos para CNAEs (primeiros 2 dígitos)
    segmento_cnae = {
        'Financeiro': '64',      # Atividades de Serviços Financeiros
        'Logística': '52',       # Armazenagem e Atividades Auxiliares
        'Saúde': '86',           # Atividades de Atenção à Saúde Humana
        'Tecnologia': '62',      # Atividades dos Serviços de TI
        'Educação': '85',        # Educação
        'Varejo': '47',          # Comércio Varejista
        'Indústria': '25',       # Fabricação de Produtos de Metal
        'Consultoria': '70',     # Atividades de Consultoria em Gestão
        'Construção': '41',      # Construção de Edifícios
        'Transporte': '49',      # Transporte Terrestre
        'SaaS': '62',            # Software as a Service (TI)
        'Retailtech': '47',      # Tecnologia para varejo
        'Performance': '73',     # Publicidade e Pesquisa de Mercado
        'Marketing': '73',       # Publicidade e Pesquisa de Mercado
        'E-commerce': '47',      # Comércio Varejista
        'Fintech': '64',         # Tecnologia Financeira
        'Healthtech': '86',      # Tecnologia para Saúde
        'Edtech': '85',          # Tecnologia para Educação
        'PropTech': '68',        # Tecnologia Imobiliária
        'Legaltech': '69'        # Tecnologia para Direito
    }
    
    # Adicionar CNAE baseado no segmento
    df['cnae'] = df['segmento'].map(segmento_cnae)
    
    # Para segmentos não mapeados, usar CNAE genérico
    df['cnae'] = df['cnae'].fillna('82')  # Serviços de Escritório e Apoio Administrativo
    
    # Adicionar CNAE completo (6 dígitos) para alguns casos
    cnae_completo = {
        'Financeiro': '6492000',      # Atividades de factoring
        'Logística': '5222000',       # Armazenagem de mercadorias
        'Saúde': '8621600',           # Atendimento hospitalar
        'Tecnologia': '6201500',      # Desenvolvimento de sistemas
        'Educação': '8599600',        # Atividades de ensino
        'Varejo': '4799000',          # Comércio varejista
        'Indústria': '2512000',       # Fabricação de estruturas metálicas
        'Consultoria': '7020400',     # Consultoria em gestão empresarial
        'Construção': '4120400',      # Construção de edifícios
        'Transporte': '4923000',      # Transporte rodoviário de cargas
        'SaaS': '6201500',            # Desenvolvimento de sistemas
        'Retailtech': '4799000',      # Comércio varejista
        'Performance': '7319000',     # Publicidade
        'Marketing': '7319000',       # Publicidade
        'E-commerce': '4799000',      # Comércio varejista
        'Fintech': '6492000',         # Atividades de factoring
        'Healthtech': '8621600',      # Atendimento hospitalar
        'Edtech': '8599600',          # Atividades de ensino
        'PropTech': '6822600',        # Administração de imóveis
        'Legaltech': '6911700'        # Advocacia
    }
    
    # Adicionar CNAE completo
    df['cnae_completo'] = df['segmento'].map(cnae_completo)
    df['cnae_completo'] = df['cnae_completo'].fillna('8299000')  # Outras atividades de serviços
    
    # Salvar o arquivo atualizado
    df.to_excel('tests/clientes_teste.xlsx', index=False)
    
    print("✅ CNAEs adicionados com sucesso!")
    print(f"📊 Total de clientes: {len(df)}")
    print("\n📋 Distribuição por CNAE:")
    print(df['cnae'].value_counts())
    
    print("\n📋 Distribuição por segmento:")
    print(df['segmento'].value_counts())
    
    return df

if __name__ == "__main__":
    df_atualizado = adicionar_cnae_por_segmento()
    print("\n✅ Arquivo 'tests/clientes_teste.xlsx' atualizado com CNAEs!") 