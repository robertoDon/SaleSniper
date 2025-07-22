import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

class AnaliseICP:
    def __init__(self):
        self.capitao_america = pd.DataFrame()
        self.correlacoes = pd.DataFrame()
        self._cache = {}  # Cache interno para cálculos intermediários

    def _correlation_ratio(self, categories: pd.Series, values: pd.Series) -> float:
        """Calcula a correlação para variáveis categóricas de forma otimizada."""
        try:
            # Converter para string primeiro para garantir que podemos adicionar "NaN"
            if categories.dtype.name == 'category':
                categories = categories.astype(str)
            
            # Preencher valores nulos com string "NaN"
            categories = categories.fillna("NaN")
            
            # Usar factorize que é mais eficiente que categorical
            codes, uniques = pd.factorize(categories)
            y = values.fillna(0).values
            y_mean = y.mean()
            
            # Usando numpy para vetorização
            means = np.bincount(codes, weights=y) / np.bincount(codes)
            counts = np.bincount(codes)
            
            ss_between = np.sum(counts * (means - y_mean) ** 2)
            ss_total = np.sum((y - y_mean) ** 2)
            
            return np.sqrt(ss_between / ss_total) if ss_total > 0 else 0.0
        except Exception as e:
            print(f"Erro ao calcular correlation ratio: {str(e)}")
            return 0.0  # Retornar 0 em caso de erro

    def _processar_correlacoes_numericas(self, df: pd.DataFrame, variaveis: List[str]) -> List[Dict]:
        """Processa correlações numéricas de forma otimizada usando vetorização."""
        if not variaveis or not isinstance(df, pd.DataFrame):
            return []
        
        cache_key = f"corr_num_{','.join(sorted(variaveis))}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            df_num = df[variaveis + ["ltv", "ticket_medio"]].copy()
            for col in df_num.columns:
                df_num[col] = pd.to_numeric(df_num[col], errors='coerce').fillna(0).astype('float32')
            
            matriz_corr = df_num.corr()
            correlacoes = []
            
            for var in variaveis:
                try:
                    corr_ltv = float(matriz_corr.at[var, "ltv"])
                    corr_ticket = float(matriz_corr.at[var, "ticket_medio"])
                except:
                    corr_ltv, corr_ticket = 0.0, 0.0
                
                correlacoes.append({
                    "variavel": var,
                    "correlacao_com_ltv": corr_ltv if not np.isnan(corr_ltv) else 0.0,
                    "correlacao_com_ticket": corr_ticket if not np.isnan(corr_ticket) else 0.0
                })
            
            self._cache[cache_key] = correlacoes
            return correlacoes
        except:
            return []

    def _processar_correlacoes_categoricas(self, df: pd.DataFrame, variaveis: List[str]) -> List[Dict]:
        """Processa correlações categóricas em paralelo para melhor performance."""
        try:
            cache_key = f"corr_cat_{','.join(sorted(variaveis))}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            correlacoes = []
            # Garantir que valores numéricos estão otimizados
            ltv = pd.to_numeric(df["ltv"], errors='coerce').fillna(0).astype('float32')
            ticket = pd.to_numeric(df["ticket_medio"], errors='coerce').fillna(0).astype('float32')
            
            # Processar cada variável sequencialmente para evitar erros de concorrência
            for var in variaveis:
                try:
                    if var in df.columns:
                        # Garantir que a variável é categórica
                        if df[var].dtype.name != 'category':
                            cat_series = pd.Categorical(df[var].fillna("NaN"))
                        else:
                            cat_series = df[var]
                        
                        correlacoes.append({
                            "variavel": var,
                            "correlacao_com_ltv": float(self._correlation_ratio(cat_series, ltv)),
                            "correlacao_com_ticket": float(self._correlation_ratio(cat_series, ticket))
                        })
                except Exception as e:
                    print(f"Erro ao processar correlação categórica para {var}: {str(e)}")
                    correlacoes.append({
                        "variavel": var,
                        "correlacao_com_ltv": 0.0,
                        "correlacao_com_ticket": 0.0
                    })
            
            self._cache[cache_key] = correlacoes
            return correlacoes
        except Exception as e:
            print(f"Erro ao processar correlações categóricas: {str(e)}")
            return []

    def _processar_correlacoes_produtos(self, df: pd.DataFrame) -> List[Dict]:
        """Processa correlações de produtos de forma otimizada."""
        try:
            cache_key = "corr_produtos"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            # Verificar se existe coluna de produtos
            if "produtos" not in df.columns:
                return []
            
            # Criar DataFrame com produtos já separados
            produtos_series = df["produtos"].fillna("").astype(str)
            produtos_df = pd.DataFrame()
            
            # Processar produtos de forma segura
            for idx, produtos in produtos_series.items():
                if produtos:
                    for produto in produtos.split(";"):
                        produto = produto.strip()
                        if produto:
                            novo_registro = pd.DataFrame({
                                "produto": [produto],
                                "ltv": [df.at[idx, "ltv"]],
                                "ticket_medio": [df.at[idx, "ticket_medio"]]
                            })
                            produtos_df = pd.concat([produtos_df, novo_registro], ignore_index=True)
            
            if produtos_df.empty:
                return []
            
            # Converter para numérico
            produtos_df["ltv"] = pd.to_numeric(produtos_df["ltv"], errors='coerce').fillna(0).astype('float32')
            produtos_df["ticket_medio"] = pd.to_numeric(produtos_df["ticket_medio"], errors='coerce').fillna(0).astype('float32')
            
            # Criar dummies de forma otimizada
            produtos_dummies = pd.get_dummies(produtos_df["produto"], prefix="", prefix_sep="")
            
            # Calcular correlações
            correlacoes = []
            ltv_values = produtos_df["ltv"].values
            ticket_values = produtos_df["ticket_medio"].values
            
            for produto in produtos_dummies.columns:
                try:
                    produto_values = produtos_dummies[produto].values
                    
                    # Calcular correlações usando numpy
                    corr_ltv = float(np.corrcoef(ltv_values, produto_values)[0,1])
                    corr_ticket = float(np.corrcoef(ticket_values, produto_values)[0,1])
                    
                    correlacoes.append({
                        "variavel": produto,
                        "correlacao_com_ltv": corr_ltv if not np.isnan(corr_ltv) else 0.0,
                        "correlacao_com_ticket": corr_ticket if not np.isnan(corr_ticket) else 0.0
                    })
                except Exception as e:
                    print(f"Erro ao processar correlação para produto {produto}: {str(e)}")
                    correlacoes.append({
                        "variavel": produto,
                        "correlacao_com_ltv": 0.0,
                        "correlacao_com_ticket": 0.0
                    })
            
            self._cache[cache_key] = correlacoes
            return correlacoes
        except Exception as e:
            print(f"Erro ao processar correlações de produtos: {str(e)}")
            return []

    def calcular_capitao_america(self, df: pd.DataFrame, qualitativos: List[str]) -> pd.DataFrame:
        """Calcula o perfil Capitão América - o perfil que gera o maior ticket médio."""
        # Pegar o cliente com maior ticket médio para identificar o perfil
        cliente_ideal = df.loc[df['ticket_medio'].idxmax()]
        
        # Filtrar clientes com o mesmo perfil
        perfil_filtrado = df.copy()
        for col in qualitativos:
            if col in df.columns:
                perfil_filtrado = perfil_filtrado[perfil_filtrado[col] == cliente_ideal[col]]
        
        # Calcular médias para esse perfil
        perfil = {
            'ticket_medio': perfil_filtrado['ticket_medio'].mean(),
            'ltv': perfil_filtrado['ltv'].mean(),
            'meses_ativo': perfil_filtrado['meses_ativo'].mean()
        }
        
        # Adicionar características categóricas do perfil ideal
        for col in qualitativos:
            if col in df.columns:
                perfil[col] = cliente_ideal[col]
        
        return pd.DataFrame([perfil])

    def calcular_correlacoes(self, df: pd.DataFrame, qualitativos: List[str], quantitativos: List[str]) -> Dict:
        """Calcula correlações entre variáveis de forma otimizada."""
        correlacoes = {}
        
        # Garante que 'cnae' está em qualitativos se existir na base
        if 'cnae' in df.columns and 'cnae' not in qualitativos:
            qualitativos = qualitativos + ['cnae']
        
        # Correlações numéricas diretas
        correlacoes['numericas'] = df[quantitativos].corr()
        
        # Análise por categoria
        correlacoes['categorias'] = {}
        
        for cat in qualitativos:
            # Análise de impacto no ticket médio
            ticket_por_cat = df.groupby(cat, observed=True)['ticket_medio'].agg(['mean', 'median', 'count'])
            ticket_por_cat = ticket_por_cat.sort_values('mean', ascending=False)
            
            # Análise de impacto no LTV
            ltv_por_cat = df.groupby(cat, observed=True)['ltv'].agg(['mean', 'median', 'count'])
            ltv_por_cat = ltv_por_cat.sort_values('mean', ascending=False)
            
            correlacoes['categorias'][cat] = {
                'ticket_medio': {
                    'ranking': ticket_por_cat.to_dict(),
                    'melhor_categoria': ticket_por_cat.index[0],
                    'pior_categoria': ticket_por_cat.index[-1],
                    'diferenca_percentual': ((ticket_por_cat['mean'].iloc[0] / ticket_por_cat['mean'].iloc[-1] - 1) * 100)
                },
                'ltv': {
                    'ranking': ltv_por_cat.to_dict(),
                    'melhor_categoria': ltv_por_cat.index[0],
                    'pior_categoria': ltv_por_cat.index[-1],
                    'diferenca_percentual': ((ltv_por_cat['mean'].iloc[0] / ltv_por_cat['mean'].iloc[-1] - 1) * 100)
                }
            }
        
        return correlacoes

    def _rankear_correlacao(self, valor: float) -> str:
        """Ranqueia correlação de forma eficiente."""
        abs_valor = abs(valor)
        if abs_valor >= 0.7: return "Muito Forte"
        if abs_valor >= 0.5: return "Forte"
        if abs_valor >= 0.3: return "Moderada"
        if abs_valor >= 0.1: return "Fraca"
        return "Muito Fraca"