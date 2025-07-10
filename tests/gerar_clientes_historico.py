import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

n = 10000

perfis = [
    'Básico Jovem', 'Básico Adulto', 'Básico Sênior',
    'Intermediário Jovem', 'Intermediário Adulto', 'Intermediário Sênior',
    'Premium Jovem', 'Premium Adulto', 'Premium Sênior'
]
canais = ['Orgânico', 'Indicação', 'Ads', 'Evento']
regioes = ['Sul', 'Sudeste', 'Centro-Oeste', 'Norte', 'Nordeste']

dados = []
for i in range(1, n+1):
    perfil = np.random.choice(perfis)
    idade = np.random.randint(18, 70)
    canal = np.random.choice(canais)
    regiao = np.random.choice(regioes)
    valor_mensal = np.random.randint(80, 1200)
    score_engajamento = np.round(np.random.uniform(0.5, 1.0), 2)
    data_entrada = datetime(2020, 1, 1) + timedelta(days=np.random.randint(0, 1500))
    # 20% dos clientes já churnaram
    if np.random.rand() < 0.2:
        data_churn = data_entrada + timedelta(days=np.random.randint(200, 1200))
        if data_churn > datetime.now():
            data_churn = ''
    else:
        data_churn = ''
    tempo_casa = (datetime.now() - data_entrada).days if not data_churn else (pd.to_datetime(data_churn) - data_entrada).days
    dados.append([
        i, perfil, idade, canal, regiao, valor_mensal, score_engajamento,
        data_entrada.strftime('%Y-%m-%d'),
        data_churn.strftime('%Y-%m-%d') if data_churn else '',
        tempo_casa
    ])

df = pd.DataFrame(dados, columns=[
    'id_cliente','perfil','idade','canal_aquisicao','regiao','valor_mensal',
    'score_engajamento','data_entrada','data_churn','tempo_casa'
])

df.to_csv('tests/clientes_historico.csv', index=False)
print('Arquivo tests/clientes_historico.csv gerado com 10.000 linhas!') 