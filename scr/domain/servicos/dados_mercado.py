import os
import pandas as pd
import requests
from typing import Optional, List, Dict
import numpy as np

class DadosMercado:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.endpoint = "https://api.econodata.com.br/v1/empresas"  # Exemplo real
        self.caminho_receita = "scr/data/cnpjs_receita_final.csv"
        self._cache_dados = {}  # Cache para dados já carregados
        
        # Descrições completas dos CNAEs (baseada na classificação oficial da Receita Federal)
        self.descricoes_cnae = {
            # Seção A - Agricultura, Pecuária e Serviços Relacionados
            '01': 'Agricultura, Pecuária e Serviços Relacionados',
            '02': 'Produção Florestal',
            '03': 'Pesca e Aquicultura',
            
            # Seção B - Indústrias Extrativas
            '05': 'Extração de Carvão Mineral',
            '06': 'Extração de Petróleo e Gás Natural',
            '07': 'Extração de Minerais Metálicos',
            '08': 'Extração de Minerais Não-Metálicos',
            '09': 'Atividades de Apoio à Extração',
            
            # Seção C - Indústrias de Transformação
            '10': 'Fabricação de Produtos Alimentícios',
            '11': 'Fabricação de Bebidas',
            '12': 'Fabricação de Produtos do Fumo',
            '13': 'Fabricação de Produtos Têxteis',
            '14': 'Confecção de Artigos do Vestuário',
            '15': 'Curtimento e Fabricação de Artigos de Couro',
            '16': 'Fabricação de Produtos de Madeira',
            '17': 'Fabricação de Papel e Produtos de Papel',
            '18': 'Impressão e Reprodução de Gravações',
            '19': 'Fabricação de Produtos de Petróleo',
            '20': 'Fabricação de Produtos Químicos',
            '21': 'Fabricação de Produtos Farmacêuticos',
            '22': 'Fabricação de Produtos de Borracha e Plástico',
            '23': 'Fabricação de Produtos de Minerais Não-Metálicos',
            '24': 'Metalurgia',
            '25': 'Fabricação de Produtos de Metal',
            '26': 'Fabricação de Equipamentos de Informática',
            '27': 'Fabricação de Equipamentos Elétricos',
            '28': 'Fabricação de Máquinas e Equipamentos',
            '29': 'Fabricação de Veículos Automotores',
            '30': 'Fabricação de Outros Equipamentos de Transporte',
            '31': 'Fabricação de Móveis',
            '32': 'Fabricação de Produtos Diversos',
            '33': 'Manutenção e Reparação de Máquinas',
            
            # Seção D - Eletricidade, Gás e Outras Utilidades
            '35': 'Eletricidade, Gás e Outras Utilidades',
            
            # Seção E - Água, Esgoto e Gestão de Resíduos
            '36': 'Captação, Tratamento e Distribuição de Água',
            '37': 'Esgoto',
            '38': 'Coleta, Tratamento e Disposição de Resíduos',
            '39': 'Descontaminação e Outros Serviços',
            
            # Seção F - Construção
            '41': 'Construção de Edifícios',
            '42': 'Obras de Infraestrutura',
            '43': 'Serviços Especializados para Construção',
            
            # Seção G - Comércio e Reparação
            '45': 'Comércio e Reparação de Veículos',
            '46': 'Comércio por Atacado',
            '47': 'Comércio Varejista',
            
            # Seção H - Transporte e Armazenagem
            '49': 'Transporte Terrestre',
            '50': 'Transporte Aquaviário',
            '51': 'Transporte Aéreo',
            '52': 'Armazenagem e Atividades Auxiliares',
            '53': 'Correio e Outras Atividades de Entrega',
            
            # Seção I - Hospedagem e Alimentação
            '55': 'Hospedagem',
            '56': 'Alimentação',
            
            # Seção J - Informação e Comunicação
            '58': 'Edição',
            '59': 'Atividades Cinematográficas',
            '60': 'Atividades de Rádio e Televisão',
            '61': 'Telecomunicações',
            '62': 'Atividades dos Serviços de TI',
            '63': 'Atividades de Prestação de Serviços de Informação',
            
            # Seção K - Atividades Financeiras e Seguros
            '64': 'Atividades de Serviços Financeiros',
            '65': 'Seguros, Previdência e Planos de Saúde',
            '66': 'Atividades Auxiliares dos Serviços Financeiros',
            
            # Seção L - Atividades Imobiliárias
            '68': 'Atividades Imobiliárias',
            
            # Seção M - Atividades Profissionais e Técnicas
            '69': 'Atividades Jurídicas e Contabilidade',
            '70': 'Atividades de Consultoria em Gestão',
            '71': 'Serviços de Arquitetura e Engenharia',
            '72': 'Pesquisa e Desenvolvimento',
            '73': 'Publicidade e Pesquisa de Mercado',
            '74': 'Outras Atividades Profissionais',
            '75': 'Atividades Veterinárias',
            
            # Seção N - Atividades Administrativas
            '77': 'Aluguel de Máquinas e Equipamentos',
            '78': 'Seleção e Agenciamento de Mão de Obra',
            '79': 'Agências de Viagens e Organizadores de Eventos',
            '80': 'Atividades de Vigilância e Segurança',
            '81': 'Serviços para Edifícios e Paisagismo',
            '82': 'Serviços de Escritório e Apoio Administrativo',
            
            # Seção O - Administração Pública
            '84': 'Administração Pública',
            
            # Seção P - Educação
            '85': 'Educação',
            
            # Seção Q - Saúde Humana e Serviços Sociais
            '86': 'Atividades de Atenção à Saúde Humana',
            '87': 'Atividades de Atenção à Saúde Integrada',
            '88': 'Atividades de Assistência Social',
            
            # Seção R - Artes, Cultura e Recreação
            '90': 'Atividades Criativas, Artísticas e Espetáculos',
            '91': 'Atividades Culturais',
            '92': 'Atividades de Lazer e Esporte',
            '93': 'Atividades Associativas',
            
            # Seção S - Outras Atividades de Serviços
            '94': 'Atividades de Organizações Associativas',
            '95': 'Reparação de Computadores e Objetos Pessoais',
            '96': 'Outras Atividades de Serviços Pessoais',
            
            # Seção T - Serviços Domésticos
            '97': 'Serviços Domésticos',
            
            # Seção U - Organizações Internacionais
            '99': 'Organizações Internacionais'
        }

    def obter_descricao_cnae(self, cnae) -> str:
        """
        Retorna a descrição do CNAE baseada nos primeiros 2 dígitos.
        """
        # Converter para string e garantir que tenha pelo menos 2 dígitos
        cnae_str = str(cnae).zfill(2)
        cnae_2dig = cnae_str[:2]
        return self.descricoes_cnae.get(cnae_2dig, 'Outros')

    def carregar_dados_receita_federal(self, 
                                     filtros: Optional[Dict] = None, 
                                     chunk_size: int = 10000,
                                     max_chunks: Optional[int] = None) -> pd.DataFrame:
        """
        Carrega dados da Receita Federal de forma otimizada.
        
        Args:
            filtros: Dicionário com filtros (ex: {'uf': ['SP', 'RJ'], 'cnae': ['62']})
            chunk_size: Tamanho de cada chunk para processamento
            max_chunks: Número máximo de chunks a processar (None = todos)
        
        Returns:
            DataFrame com dados filtrados
        """
        if not os.path.exists(self.caminho_receita):
            print(f"⚠️ Arquivo da Receita Federal não encontrado: {self.caminho_receita}")
            print("📊 Usando dados de exemplo para demonstração...")
            # Limpar cache para forçar uso de dados de exemplo
            self._cache_dados.clear()
            return self._gerar_dados_exemplo()
        
        print(f"Carregando dados da Receita Federal: {self.caminho_receita}")
        
        # Criar chave de cache baseada nos filtros
        cache_key = str(filtros) + str(chunk_size) + str(max_chunks)
        if cache_key in self._cache_dados:
            print("📦 Usando dados do cache...")
            return self._cache_dados[cache_key]
        
        chunks = []
        chunk_count = 0
        
        # Ler arquivo em chunks
        for chunk in pd.read_csv(self.caminho_receita, dtype=str, chunksize=chunk_size):
            # Aplicar filtros se especificados
            if filtros:
                for coluna, valores in filtros.items():
                    if coluna in chunk.columns:
                        chunk = chunk[chunk[coluna].isin(valores)]
            
            if len(chunk) > 0:
                chunks.append(chunk)
                chunk_count += 1
                
                if max_chunks and chunk_count >= max_chunks:
                    break
                
                if chunk_count % 10 == 0:
                    print(f"📊 Processados {chunk_count} chunks...")
        
        if not chunks:
            print("⚠️ Nenhum dado encontrado com os filtros especificados")
            return pd.DataFrame()
        
        # Concatenar chunks
        df = pd.concat(chunks, ignore_index=True)
        
        # Adicionar coluna regiao baseada na UF
        regioes = {
            'SP': 'Sudeste', 'RJ': 'Sudeste', 'MG': 'Sudeste', 'ES': 'Sudeste',
            'RS': 'Sul', 'SC': 'Sul', 'PR': 'Sul',
            'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'DF': 'Centro-Oeste',
            'BA': 'Nordeste', 'PE': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 
            'PB': 'Nordeste', 'RN': 'Nordeste', 'AL': 'Nordeste', 'SE': 'Nordeste', 'PI': 'Nordeste',
            'AM': 'Norte', 'PA': 'Norte', 'AC': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'AP': 'Norte', 'TO': 'Norte'
        }
        df['regiao'] = df['uf'].map(regioes)
        
        # Adicionar descrição do CNAE
        df['descricao_cnae'] = df['cnae'].apply(self.obter_descricao_cnae)
        
        # Salvar no cache
        self._cache_dados[cache_key] = df
        
        print(f"✅ Dados carregados: {len(df):,} estabelecimentos (de {chunk_count} chunks)")
        return df

    def _gerar_dados_exemplo(self) -> pd.DataFrame:
        """
        Gera dados de exemplo para demonstração quando o arquivo da Receita Federal não está disponível.
        """
        print("🔄 Gerando dados de exemplo para demonstração...")
        
        # Dados de exemplo baseados em CNAEs reais
        dados_exemplo = {
            'cnpj': [f"{i:014d}" for i in range(1000)],
            'cnae': np.random.choice(['62', '47', '52', '43', '41', '45', '46', '49', '55', '56'], 1000),
            'razao_social': [f"Empresa Exemplo {i}" for i in range(1000)],
            'uf': np.random.choice(['SP', 'RJ', 'MG', 'RS', 'SC', 'PR', 'GO', 'BA', 'PE', 'CE'], 1000),
            'municipio': np.random.choice(['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Porto Alegre', 'Curitiba'], 1000),
            'situacao': ['ATIVA'] * 1000
        }
        
        df = pd.DataFrame(dados_exemplo)
        
        # Adicionar coluna regiao baseada na UF
        regioes = {
            'SP': 'Sudeste', 'RJ': 'Sudeste', 'MG': 'Sudeste', 'ES': 'Sudeste',
            'RS': 'Sul', 'SC': 'Sul', 'PR': 'Sul',
            'GO': 'Centro-Oeste', 'MT': 'Centro-Oeste', 'MS': 'Centro-Oeste', 'DF': 'Centro-Oeste',
            'BA': 'Nordeste', 'PE': 'Nordeste', 'CE': 'Nordeste', 'MA': 'Nordeste', 
            'PB': 'Nordeste', 'RN': 'Nordeste', 'AL': 'Nordeste', 'SE': 'Nordeste', 'PI': 'Nordeste',
            'AM': 'Norte', 'PA': 'Norte', 'AC': 'Norte', 'RO': 'Norte', 'RR': 'Norte', 'AP': 'Norte', 'TO': 'Norte'
        }
        df['regiao'] = df['uf'].map(regioes)
        
        # Adicionar descrição do CNAE
        df['descricao_cnae'] = df['cnae'].apply(self.obter_descricao_cnae)
        
        print(f"✅ Dados de exemplo gerados: {len(df):,} estabelecimentos")
        return df

    def carregar_dados_por_regiao(self, regioes: List[str], chunk_size: int = 10000) -> pd.DataFrame:
        """
        Carrega dados apenas para regiões específicas.
        """
        # Mapear regiões para UFs
        regiao_uf = {
            'Sudeste': ['SP', 'RJ', 'MG', 'ES'],
            'Sul': ['RS', 'SC', 'PR'],
            'Centro-Oeste': ['GO', 'MT', 'MS', 'DF'],
            'Nordeste': ['BA', 'PE', 'CE', 'MA', 'PB', 'RN', 'AL', 'SE', 'PI'],
            'Norte': ['AM', 'PA', 'AC', 'RO', 'RR', 'AP', 'TO']
        }
        
        ufs = []
        for regiao in regioes:
            if regiao in regiao_uf:
                ufs.extend(regiao_uf[regiao])
        
        return self.carregar_dados_receita_federal(
            filtros={'uf': ufs},
            chunk_size=chunk_size
        )

    def carregar_dados_por_cnae(self, cnaes: List[str], chunk_size: int = 10000) -> pd.DataFrame:
        """
        Carrega dados apenas para CNAEs específicos.
        """
        return self.carregar_dados_receita_federal(
            filtros={'cnae': cnaes},
            chunk_size=chunk_size
        )

    def carregar_dados_econodata(self, params: dict) -> pd.DataFrame:
        """
        Método legado - agora usa dados da Receita Federal
        """
        return self.carregar_dados_receita_federal()

    def cruzar_dados_mercado(self, df_mercado: pd.DataFrame, df_clientes: pd.DataFrame) -> pd.DataFrame:
        """
        Cruza dados do mercado com base de clientes.
        Adiciona coluna 'é_cliente' indicando se o CNPJ está na base de clientes.
        """
        # Garantir que CNPJ seja string em ambos os DataFrames
        df_mercado['cnpj'] = df_mercado['cnpj'].astype(str)
        df_clientes['cnpj'] = df_clientes['cnpj'].astype(str)
        
        # Marcar quais CNPJs são clientes
        df_mercado["é_cliente"] = df_mercado["cnpj"].isin(df_clientes["cnpj"])
        
        print(f"Cruzamento realizado: {df_mercado['é_cliente'].sum():,} clientes encontrados no mercado")
        return df_mercado

    def aplicar_segmentacao_20_30_30_20(self, df: pd.DataFrame, campo: str) -> pd.DataFrame:
        df = df.sort_values(by=campo, ascending=False).copy()
        total = len(df)
        limites = [
            int(0.2 * total),
            int(0.5 * total),
            int(0.8 * total),
            total
        ]
        tiers = []
        for i, idx in enumerate(df.index):
            if i < limites[0]:
                tiers.append("Tier 1")
            elif i < limites[1]:
                tiers.append("Tier 2")
            elif i < limites[2]:
                tiers.append("Tier 3")
            else:
                tiers.append("Tier 4")
        df["tier"] = tiers
        return df

    def gerar_matriz_tam_sam_som(self, df: pd.DataFrame, agrupadores=["regiao", "descricao_cnae"]) -> pd.DataFrame:
        """
        Gera matriz TAM/SAM/SOM agrupada por região e descrição do CNAE.
        """
        matriz = df.groupby(agrupadores).agg(
            TAM=("cnpj", "count"),
            SAM=("é_cliente", lambda x: (~x).sum()),
            SOM=("é_cliente", "sum"),
            Tier_1=("tier", lambda x: (x == "Tier 1").sum()),
            Tier_2=("tier", lambda x: (x == "Tier 2").sum()),
            Tier_3=("tier", lambda x: (x == "Tier 3").sum()),
            Tier_4=("tier", lambda x: (x == "Tier 4").sum())
        ).reset_index()
        
        return matriz
    
    def gerar_resumo_tam_sam_som(self, df: pd.DataFrame) -> pd.DataFrame:
        if "tier" not in df.columns or "é_cliente" not in df.columns:
            raise ValueError("DataFrame precisa conter colunas 'tier' e 'é_cliente'.")

        df["é_potencial"] = ~df["é_cliente"]

        resultado = {
            "TAM": df.groupby("tier")["cnpj"].count(),
            "SAM": df[df["é_potencial"]].groupby("tier")["cnpj"].count(),
            "SOM": df[df["é_cliente"]].groupby("tier")["cnpj"].count(),
        }

        matriz = pd.DataFrame(resultado).T.fillna(0).astype(int)
        return matriz

    def sugerir_cnaes_semelhantes(self, df_clientes: pd.DataFrame, df_mercado: pd.DataFrame) -> pd.DataFrame:
        """
        Sugere CNAEs semelhantes presentes no mercado, mas não na base de clientes.
        Retorna DataFrame com descrição do CNAE, quantidade de empresas e região.
        """
        # Extrai os CNAEs dos clientes
        cnaes_clientes = df_clientes['cnae'].astype(str).str[:2].unique()
        
        # Filtra CNAEs do mercado que não estão nos clientes
        df_novos = df_mercado[~df_mercado['cnae'].astype(str).str[:2].isin(cnaes_clientes)]
        
        # Agrupa por descrição do CNAE e região
        oportunidades = df_novos.groupby(['descricao_cnae', 'regiao']).agg(
            qtd_empresas=('cnpj', 'count')
        ).reset_index()
        
        oportunidades = oportunidades.sort_values('qtd_empresas', ascending=False)
        return oportunidades

    def calcular_tam_sam_som_por_cnae(self, df_clientes: pd.DataFrame, df_mercado: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula TAM/SAM/SOM por descrição do CNAE e região.
        """
        # Preparar dados dos clientes
        df_clientes['descricao_cnae'] = df_clientes['cnae'].apply(self.obter_descricao_cnae)
        
        # Cruzar dados
        df_cruzado = self.cruzar_dados_mercado(df_mercado, df_clientes)
        
        # Aplicar segmentação por quantidade de empresas
        df_cruzado = self.aplicar_segmentacao_20_30_30_20(df_cruzado, 'cnpj')
        
        # Gerar matriz TAM/SAM/SOM
        matriz = self.gerar_matriz_tam_sam_som(df_cruzado, agrupadores=['regiao', 'descricao_cnae'])
        
        return matriz

    def gerar_relatorio_similaridade_cnae(self, df_clientes: pd.DataFrame, df_mercado: pd.DataFrame) -> pd.DataFrame:
        """
        Gera relatório detalhado de similaridade entre CNAEs dos clientes e do mercado.
        """
        print("📊 Gerando relatório de similaridade de CNAEs...")
        
        cnaes_clientes = df_clientes['cnae'].astype(str).str[:2].unique()
        relatorio = []
        
        for cnae_cliente in cnaes_clientes:
            # Calcular estatísticas
            qtd_empresas_similares = df_mercado[df_mercado['cnae'].astype(str).str[:2] == cnae_cliente]['cnpj'].count()
            qtd_clientes_nesse_cnae = df_clientes[df_clientes['cnae'].astype(str).str[:2] == cnae_cliente]['cnpj'].count()
            
            relatorio.append({
                'cnae_cliente': cnae_cliente,
                'descricao_cliente': self.obter_descricao_cnae(cnae_cliente),
                'qtd_clientes_atual': qtd_clientes_nesse_cnae,
                'qtd_empresas_mercado': qtd_empresas_similares,
                'potencial_expansao': qtd_empresas_similares - qtd_clientes_nesse_cnae
            })
        
        df_relatorio = pd.DataFrame(relatorio)
        df_relatorio = df_relatorio.sort_values('potencial_expansao', ascending=False)
        
        print(f"📈 Relatório gerado: {len(df_relatorio)} CNAEs de clientes analisados")
        return df_relatorio

    def limpar_cache(self):
        """
        Limpa o cache de dados carregados.
        """
        self._cache_dados.clear()
        print("🗑️ Cache limpo")

