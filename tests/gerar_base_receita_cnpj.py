import pandas as pd
import zipfile

# Caminho do arquivo baixado manualmente
ZIP_LOCAL = 'scr/data/Estabelecimentos0.zip'

# Nome do arquivo de saída
ARQUIVO_SAIDA = 'scr/data/cnpjs_receita.csv'
ARQUIVO_FINAL = 'scr/data/cnpjs_receita_final.csv'

# Mapeamento das colunas da Receita Federal (baseado no layout oficial)
COLUNAS_RECEITA = {
    0: 'CNPJ_BASICO',
    1: 'CNPJ_ORDEM', 
    2: 'CNPJ_DV',
    3: 'IDENTIFICADOR_MATRIZ_FILIAL',
    4: 'NOME_FANTASIA',
    5: 'SITUACAO_CADASTRAL',
    6: 'DATA_SITUACAO_CADASTRAL',
    7: 'MOTIVO_SITUACAO_CADASTRAL',
    8: 'NOME_CIDADE_EXTERIOR',
    9: 'PAIS',
    10: 'DATA_INICIO_ATIVIDADE',
    11: 'CNAE_PRINCIPAL',
    12: 'CNAE_SECUNDARIO',
    13: 'TIPO_LOGRADOURO',
    14: 'LOGRADOURO',
    15: 'NUMERO',
    16: 'COMPLEMENTO',
    17: 'BAIRRO',
    18: 'CEP',
    19: 'UF',
    20: 'MUNICIPIO',
    21: 'DDD_1',
    22: 'TELEFONE_1',
    23: 'DDD_2',
    24: 'TELEFONE_2',
    25: 'DDD_FAX',
    26: 'FAX',
    27: 'EMAIL',
    28: 'SITUACAO_ESPECIAL',
    29: 'DATA_SITUACAO_ESPECIAL'
}

# Colunas que queremos manter para TAM/SAM/SOM
COLUNAS_INTERESSE = {
    'CNPJ_BASICO': 'cnpj',
    'CNAE_PRINCIPAL': 'cnae', 
    'NOME_FANTASIA': 'razao_social',
    'UF': 'uf',
    'MUNICIPIO': 'municipio',
    'SITUACAO_CADASTRAL': 'situacao'
}

def extrair_zip_local(path):
    print(f'Lendo {path}...')
    z = zipfile.ZipFile(path)
    info = max(z.infolist(), key=lambda x: x.file_size)
    print(f'Extraindo {info.filename}...')
    
    # Ler o arquivo completo
    df = pd.read_csv(
        z.open(info.filename),
        sep=';',
        dtype=str,
        encoding='latin1',
        low_memory=False,
        on_bad_lines='warn',
        header=None,
        quotechar='"'
    )
    
    # Renomear colunas baseado no mapeamento
    df = df.rename(columns=COLUNAS_RECEITA)
    return df

def filtrar_dados(df):
    """Filtra apenas estabelecimentos ativos e colunas de interesse"""
    print('Filtrando dados...')
    print(f'Colunas disponíveis: {list(df.columns)}')
    print(f'Valores únicos em SITUACAO_CADASTRAL: {df["SITUACAO_CADASTRAL"].value_counts().head(5)}')
    
    # Filtrar apenas estabelecimentos ativos (situação = '02' = ATIVA)
    df_ativos = df[df['SITUACAO_CADASTRAL'] == '02'].copy()
    print(f'Estabelecimentos ativos: {len(df_ativos)} de {len(df)}')
    
    # Selecionar apenas colunas de interesse
    colunas_finais = list(COLUNAS_INTERESSE.keys())
    df_final = df_ativos[colunas_finais].copy()
    
    # Renomear para nomes mais simples
    df_final = df_final.rename(columns=COLUNAS_INTERESSE)
    
    # Limpar dados
    df_final = df_final.dropna(subset=['cnae', 'uf'])
    df_final = df_final[df_final['cnae'].str.len() >= 7]  # CNAE deve ter pelo menos 7 dígitos
    
    print(f'Dados finais: {len(df_final)} registros')
    return df_final

def main():
    # Extrair dados brutos
    df = extrair_zip_local(ZIP_LOCAL)
    print(f'Arquivo lido! Shape: {df.shape}')
    
    # Salvar arquivo bruto
    df.to_csv(ARQUIVO_SAIDA, index=False)
    print(f'Arquivo bruto gerado: {ARQUIVO_SAIDA} ({len(df)} linhas)')
    
    # Filtrar e gerar arquivo final
    df_final = filtrar_dados(df)
    df_final.to_csv(ARQUIVO_FINAL, index=False)
    print(f'Arquivo final gerado: {ARQUIVO_FINAL} ({len(df_final)} linhas)')
    
    # Mostrar estatísticas
    print('\nEstatísticas dos dados finais:')
    print(f'Estados únicos: {df_final["uf"].nunique()}')
    print(f'CNAEs únicos (3 dígitos): {df_final["cnae"].str[:3].nunique()}')
    print(f'Municípios únicos: {df_final["municipio"].nunique()}')
    
    # Top 10 CNAEs (3 dígitos)
    print('\nTop 10 CNAEs (3 dígitos):')
    top_cnaes = df_final['cnae'].str[:3].value_counts().head(10)
    for cnae, count in top_cnaes.items():
        print(f'  {cnae}: {count:,} empresas')

if __name__ == '__main__':
    main() 