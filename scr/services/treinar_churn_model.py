import pandas as pd
import numpy as np
import pickle
from lifelines import WeibullAFTFitter
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score
from sksurv.ensemble import RandomSurvivalForest
from sksurv.metrics import concordance_index_censored
import json

# Caminho do arquivo de clientes históricos
csv_path = 'tests/clientes_historico.csv'  # ou 'scr/data/clientes_historico.csv'

clientes = pd.read_csv(csv_path, parse_dates=['data_entrada', 'data_churn'])

# Feature engineering
clientes['duracao'] = (clientes['data_churn'].fillna(pd.Timestamp('today')) - clientes['data_entrada']).dt.days
clientes['churned'] = clientes['data_churn'].notnull().astype(int)

# One-hot encoding igual ao app
perfis = [
    'Básico Jovem', 'Básico Adulto', 'Básico Sênior',
    'Intermediário Jovem', 'Intermediário Adulto', 'Intermediário Sênior',
    'Premium Jovem', 'Premium Adulto', 'Premium Sênior'
]
canais = ['Orgânico', 'Indicação', 'Ads', 'Evento']
regioes = ['Sul', 'Sudeste', 'Centro-Oeste', 'Norte', 'Nordeste']

for p in perfis[1:]:
    clientes[f'perfil_{p}'] = (clientes['perfil'] == p).astype(int)
for c in canais[1:]:
    clientes[f'canal_aquisicao_{c}'] = (clientes['canal_aquisicao'] == c).astype(int)
for r in regioes[1:]:
    clientes[f'regiao_{r}'] = (clientes['regiao'] == r).astype(int)

num_features = ['idade', 'tempo_casa', 'score_engajamento']
clientes[num_features] = StandardScaler().fit_transform(clientes[num_features])

# Features finais (iguais ao app)
features = []
features += [f'perfil_{p}' for p in perfis[1:]]
features += [f'canal_aquisicao_{c}' for c in canais[1:]]
features += [f'regiao_{r}' for r in regioes[1:]]
features += num_features

X = clientes[features]
y = clientes[['duracao', 'churned']]

# Separar treino/teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# WeibullAFT
train_weibull = X_train.copy()
train_weibull['duracao'] = y_train['duracao']
train_weibull['churned'] = y_train['churned']
weibull = WeibullAFTFitter()
weibull.fit(train_weibull, duration_col='duracao', event_col='churned')

# Random Survival Forest (scikit-survival)
def to_structured(y):
    return np.array([(bool(e), t) for t, e in zip(y['duracao'], y['churned'])], dtype=[('event', '?'), ('time', '<f8')])

rsf = RandomSurvivalForest(n_estimators=200, min_samples_split=10, min_samples_leaf=10, n_jobs=-1, random_state=42)
rsf.fit(X_train, to_structured(y_train))

# Avaliação: previsão de churn em até 12 meses (365 dias)
def avaliar_modelo(model, X, y, tipo='weibull'):
    if tipo == 'weibull':
        y_pred_dias = model.predict_expectation(X)
    else:
        # Para RSF, usar a expectativa de sobrevida
        surv_funcs = model.predict_survival_function(X)
        # Calcular expectativa de tempo até churn
        y_pred_dias = np.array([np.trapz(fn.y, fn.x) for fn in surv_funcs])
    y_pred_churn = (y_pred_dias < 365).astype(int)
    acc = accuracy_score(y['churned'], y_pred_churn)
    try:
        roc = roc_auc_score(y['churned'], -y_pred_dias)  # quanto menor o tempo, maior o risco
    except:
        roc = float('nan')
    return acc, roc

acc_w, roc_w = avaliar_modelo(weibull, X_test, y_test, tipo='weibull')
acc_r, roc_r = avaliar_modelo(rsf, X_test, y_test, tipo='rsf')

print('--- Avaliação dos Modelos ---')
print(f'WeibullAFT:    Acurácia={acc_w:.2%}  ROC-AUC={roc_w:.2%}')
print(f'RandomSurvivalForest: Acurácia={acc_r:.2%}  ROC-AUC={roc_r:.2%}')

# Escolher melhor modelo (maior ROC-AUC)
if roc_r > roc_w:
    melhor_modelo = rsf
    melhor_nome = 'RandomSurvivalForest'
else:
    melhor_modelo = weibull
    melhor_nome = 'WeibullAFT'

# Salvar modelo e features
with open('scr/data/modelo_final.pkl', 'wb') as f:
    pickle.dump(melhor_modelo, f)
with open('scr/data/features_weibull.pkl', 'wb') as f:
    pickle.dump(features, f)

print(f'Melhor modelo: {melhor_nome}')
print('Modelo treinado e salvo em scr/data/modelo_final.pkl')
print('Features salvas em scr/data/features_weibull.pkl')

# Salvar métricas do melhor modelo
metrics = {
    'modelo': melhor_nome,
    'acuracia': float(acc_r if melhor_nome == 'RandomSurvivalForest' else acc_w),
    'roc_auc': float(roc_r if melhor_nome == 'RandomSurvivalForest' else roc_w)
}
with open('scr/data/churn_model_metrics.json', 'w') as f:
    json.dump(metrics, f, indent=2)
print(f'Métricas salvas em scr/data/churn_model_metrics.json') 