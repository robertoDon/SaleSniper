import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

# Parâmetros
def gen_nome(i):
    return f'Cliente_{i+1}'

def gen_data_aleatoria():
    start_date = datetime.now() - timedelta(days=5*365)
    random_days = np.random.randint(0, 5*365)
    return (start_date + timedelta(days=int(random_days))).date()

n_historico = 1000
n_ativos = 200
segmentos = ['Tecnologia']
localizacoes = ['SP', 'RJ', 'MG', 'RS', 'PR']
portes = ['Pequeno', 'Médio', 'Grande']
dores = ['Custos', 'Produtividade', 'Financeiro', 'Retenção', 'Expansão']
cnaes = ['6201500', '6202300', '6203100', '6311900']
perfis = [
    'Básico Jovem', 'Básico Adulto', 'Básico Sênior',
    'Intermediário Jovem', 'Intermediário Adulto', 'Intermediário Sênior',
    'Premium Jovem', 'Premium Adulto', 'Premium Sênior'
]
canais = ['Orgânico', 'Indicação', 'Ads', 'Evento']
regioes = ['Sul', 'Sudeste', 'Centro-Oeste', 'Norte', 'Nordeste']

# Gerar clientes históricos (~1000)
historico = []
for i in range(n_historico):
    data_contratacao = gen_data_aleatoria()
    meses_ativo = np.random.randint(1, 60)
    ticket_medio = int(np.random.normal(40000, 15000))
    ltv = ticket_medio * meses_ativo
    historico.append({
        'nome_cliente': gen_nome(i),
        'porte': np.random.choice(portes, p=[0.5, 0.3, 0.2]),
        'dores': np.random.choice(dores),
        'localizacao': np.random.choice(localizacoes),
        'segmento': 'Tecnologia',
        'cnae': np.random.choice(cnaes),
        'faturamento': int(np.random.normal(800000, 300000)),
        'ticket_medio': ticket_medio,
        'meses_ativo': meses_ativo,
        'ltv': ltv,
        'produtos': '',
        'data_contratacao': data_contratacao,
        'data_entrada': data_contratacao,
        'data_churn': pd.NaT,
        'tempo_negociacao': np.random.randint(1, 12),
        'perfil': np.random.choice(perfis),
        'canal_aquisicao': np.random.choice(canais),
        'regiao': np.random.choice(regioes),
        'idade': np.random.randint(18, 70),
        'tempo_casa': np.random.randint(1, 60),
        'score_engajamento': np.random.uniform(0, 1)
    })

# Gerar clientes ativos (~200, subconjunto do histórico)
ativos_idx = np.random.choice(range(n_historico), n_ativos, replace=False)
ativos = []
for idx in ativos_idx:
    c = historico[idx].copy()
    c['meses_ativo'] = np.random.randint(12, 60)
    c['ticket_medio'] = int(np.random.normal(50000, 10000))
    c['ltv'] = c['ticket_medio'] * c['meses_ativo']
    c['produtos'] = ''
    c['data_contratacao'] = gen_data_aleatoria()
    c['data_entrada'] = c['data_contratacao']
    c['data_churn'] = pd.NaT
    c['tempo_negociacao'] = np.random.randint(1, 12)
    c['perfil'] = np.random.choice(perfis)
    c['canal_aquisicao'] = np.random.choice(canais)
    c['regiao'] = np.random.choice(regioes)
    c['idade'] = np.random.randint(18, 70)
    c['tempo_casa'] = np.random.randint(1, 60)
    c['score_engajamento'] = np.random.uniform(0, 1)
    ativos.append(c)

# Salvar histórico como CSV
pd.DataFrame(historico).to_csv('scr/data/clientes_historico.csv', index=False)
# Salvar ativos como Excel
pd.DataFrame(ativos).to_excel('tests/clientes_teste.xlsx', index=False)

print('Arquivos scr/data/clientes_historico.csv e tests/clientes_teste.xlsx gerados com sucesso!') 