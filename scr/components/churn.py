"""Churn prediction module.

Loads a pre-trained Weibull AFT model (lifelines) and predicts time-to-churn
based on input data.
"""

import pandas as pd
import numpy as np
import pickle
import os

# Base features expected by the model (saved naively no guarantee order)
FEATURE_COLUMNS_PATH = os.path.join(os.path.dirname(__file__), '../data/features_weibull.pkl')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '../data/modelo_final.pkl')


def _load_model():
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def _load_feature_cols():
    with open(FEATURE_COLUMNS_PATH, 'rb') as f:
        return pickle.load(f)


def _prepare_features(df: pd.DataFrame, feature_cols: list) -> pd.DataFrame:
    """Cria um DataFrame com as colunas exatas que o modelo espera."""
    df_proc = df.copy()

    # Garantir colunas numéricas
    for col in ['idade', 'tempo_casa', 'score_engajamento']:
        if col not in df_proc.columns:
            df_proc[col] = 0
        df_proc[col] = pd.to_numeric(df_proc[col], errors='coerce').fillna(0)

    # One-hot para categorias usadas no modelo
    # As colunas já vêm no formato 'perfil_X', 'canal_aquisicao_Y', 'regiao_Z'
    for cat in ['perfil', 'canal_aquisicao', 'regiao']:
        if cat in df_proc.columns:
            dummies = pd.get_dummies(df_proc[cat], prefix=cat)
            df_proc = pd.concat([df_proc, dummies], axis=1)

    # Garantir todas as colunas necessárias
    for col in feature_cols:
        if col not in df_proc.columns:
            df_proc[col] = 0

    # Somente retorna as colunas na ordem esperada
    return df_proc[feature_cols]


def get_churn_data(arquivo) -> dict:
    """Processa arquivo CSV e retorna predições de churn."""
    try:
        df = pd.read_csv(arquivo)
    except Exception as e:
        return {'error': f'Erro ao ler CSV: {e}'}

    try:
        feature_cols = _load_feature_cols()
        model = _load_model()
    except Exception as e:
        return {'error': f'Erro ao carregar modelo: {e}'}

    try:
        df_features = _prepare_features(df, feature_cols)
    except Exception as e:
        return {'error': f'Erro ao preparar features: {e}'}

    try:
        # Previsão do tempo até churn (mediana)
        pred = model.predict_median(df_features)
        df['tempo_ate_churn'] = pred

        # Ajustes: se quiser interpretar como meses ou dias, depende do modelo (normalmente em dias)
        # Aqui assumimos em dias (padrão lifelines usa mesma unidade do tempo usado no treino)

        # Estatísticas simples
        medias = {
            'media_dias': float(np.nanmean(pred)),
            'mediana_dias': float(np.nanmedian(pred)),
            'min_dias': float(np.nanmin(pred)),
            'max_dias': float(np.nanmax(pred)),
            'count': int(len(pred))
        }

        # Mostrar apenas primeiras linhas com a predição
        preview = df.copy()
        if 'nome' in preview.columns:
            preview = preview[['nome', 'tempo_ate_churn']]
        else:
            preview = preview[['tempo_ate_churn']]
        preview = preview.head(20).to_dict(orient='records')

        return {
            'stats': medias,
            'preview': preview
        }

    except Exception as e:
        return {'error': f'Erro ao gerar predições: {e}'}
