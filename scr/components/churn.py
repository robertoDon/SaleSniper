import streamlit as st
import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
import io

def exibir_churn():
    st.markdown("<h1 style='color: #FF8C00;'>SaleSniper - Previsão de Churn de Clientes</h1>", unsafe_allow_html=True)
    
    # Upload do arquivo de clientes
    arquivo_clientes = st.file_uploader(
        "Envie o arquivo CSV de clientes (com as colunas do modelo)", type="csv", key="clientes_churn"
    )
    if not arquivo_clientes:
        st.warning("Envie um arquivo CSV para continuar.")
        st.stop()
    
    # Ler CSV sem parse_dates para evitar erro se colunas não existirem
    clientes = pd.read_csv(arquivo_clientes)
    
    # Converter colunas de data se existirem
    colunas_data = ['data_entrada', 'data_churn', 'data_contratacao']
    for col in colunas_data:
        if col in clientes.columns:
            clientes[col] = pd.to_datetime(clientes[col], errors='coerce')
    
    # Carregar modelo e features
    base_path = os.path.join(os.path.dirname(__file__), '../data')
    with open(os.path.join(base_path, 'modelo_final.pkl'), 'rb') as f:
        modelo = pickle.load(f)
    with open(os.path.join(base_path, 'features_weibull.pkl'), 'rb') as f:
        features_weibull = pickle.load(f)
    
    # Ler acurácia do modelo
    metrics_path = os.path.join(os.path.dirname(__file__), '../data/churn_model_metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        acuracia = metrics.get('acuracia', 0.7)
    else:
        acuracia = 0.7  # valor padrão se não existir
    
    # Função para preparar features
    def get_features(df):
        perfis = [
            'Básico Jovem', 'Básico Adulto', 'Básico Sênior',
            'Intermediário Jovem', 'Intermediário Adulto', 'Intermediário Sênior',
            'Premium Jovem', 'Premium Adulto', 'Premium Sênior'
        ]
        canais = ['Orgânico', 'Indicação', 'Ads', 'Evento']
        regioes = ['Sul', 'Sudeste', 'Centro-Oeste', 'Norte', 'Nordeste']
        for p in perfis[1:]:
            df[f'perfil_{p}'] = (df['perfil'] == p).astype(int)
        for c in canais[1:]:
            df[f'canal_aquisicao_{c}'] = (df['canal_aquisicao'] == c).astype(int)
        for r in regioes[1:]:
            df[f'regiao_{r}'] = (df['regiao'] == r).astype(int)
        num_features = ['idade', 'tempo_casa', 'score_engajamento']
        df[num_features] = (df[num_features] - clientes[num_features].mean()) / clientes[num_features].std()
        features = features_weibull
        for col in features:
            if col not in df.columns:
                df[col] = 0
        return df[features]
    
    # Previsão para clientes ativos
    ativos = clientes[clientes['data_churn'].isna()].copy()
    if len(ativos) == 0:
        st.info("Nenhum cliente ativo encontrado no arquivo enviado.")
        st.stop()
    ativos_features = get_features(ativos)
    hoje = pd.Timestamp(datetime.today().date())
    ativos['data_entrada'] = pd.to_datetime(ativos['data_entrada'])
    ativos['dias_ate_churn_pred'] = modelo.predict_expectation(ativos_features)
    ativos['data_churn_pred'] = ativos['data_entrada'] + pd.to_timedelta(ativos['dias_ate_churn_pred'], unit='D')
    ativos['data_churn_pred'] = ativos['data_churn_pred'].apply(lambda x: x if x > hoje else hoje)
    
    # Previsão para próximos 9 meses
    meses_a_frente = 9
    limite_futuro = hoje + pd.DateOffset(months=meses_a_frente)
    ativos_validos = ativos[(ativos['data_churn_pred'] >= hoje) & (ativos['data_churn_pred'] < limite_futuro)].copy()
    ativos_validos['valor_perdido'] = ativos_validos['valor_mensal']
    ativos_validos['mes_ano_churn_pred'] = ativos_validos['data_churn_pred'].dt.to_period('M')
    churns_mes = ativos_validos.groupby('mes_ano_churn_pred', as_index=False).agg({'id_cliente':'count'})
    churns_mes.rename(columns={'id_cliente':'qtd_churns'}, inplace=True)
    valor_perdido_mes = ativos_validos.groupby('mes_ano_churn_pred', as_index=False).agg({'valor_perdido':'sum'})
    
    # Remover o mês atual das tabelas e gráficos
    mes_atual = hoje.to_period('M')
    churns_mes = churns_mes[churns_mes['mes_ano_churn_pred'] != mes_atual]
    valor_perdido_mes = valor_perdido_mes[valor_perdido_mes['mes_ano_churn_pred'] != mes_atual]
    
    # Vida útil média por perfil
    clientes['vida_util'] = (clientes['data_churn'].fillna(pd.Timestamp('today')) - clientes['data_entrada']).dt.days
    vida_util_perfil = clientes.groupby('perfil')['vida_util'].mean().reset_index()
    
    # Função para formatar valores monetários
    def formatar_reais(x):
        return f'R$ {int(round(x)):,}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    # Tabelas
    st.markdown(f"<h3 style='color:#FF8C00;'>Churns previstos nos próximos meses:</h3>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:#888;'>Acurácia do modelo: {acuracia:.2%}</span>", unsafe_allow_html=True)
    churns_mes_fmt = churns_mes.copy()
    churns_mes_fmt['mes_ano_churn_pred'] = churns_mes_fmt['mes_ano_churn_pred'].astype(str)
    # Faixa dinâmica baseada na acurácia
    def faixa_incerteza(val):
        delta = (1 - acuracia) * val
        return int(np.floor(val - delta)), int(np.ceil(val + delta))
    churns_mes_fmt['faixa'] = churns_mes_fmt['qtd_churns'].apply(lambda x: f"{faixa_incerteza(x)[0]} a {faixa_incerteza(x)[1]}")
    st.dataframe(churns_mes_fmt[['mes_ano_churn_pred','qtd_churns','faixa']], hide_index=True)
    
    st.markdown(f"<h3 style='color:#FF8C00;'>Valor perdido previsto por mês:</h3>", unsafe_allow_html=True)
    st.markdown(f"<span style='color:#888;'>Acurácia do modelo: {acuracia:.2%}</span>", unsafe_allow_html=True)
    valor_perdido_mes_fmt = valor_perdido_mes.copy()
    valor_perdido_mes_fmt['mes_ano_churn_pred'] = valor_perdido_mes_fmt['mes_ano_churn_pred'].astype(str)
    valor_perdido_mes_fmt['faixa'] = valor_perdido_mes_fmt['valor_perdido'].apply(lambda x: f"R$ {faixa_incerteza(x)[0]:,} a R$ {faixa_incerteza(x)[1]:,}".replace(',', 'X').replace('.', ',').replace('X', '.'))
    valor_perdido_mes_fmt['valor_perdido'] = valor_perdido_mes_fmt['valor_perdido'].apply(formatar_reais)
    st.dataframe(valor_perdido_mes_fmt[['mes_ano_churn_pred','valor_perdido','faixa']], hide_index=True)
    
    st.markdown(f"<h3 style='color:#FF8C00;'>Vida útil média por perfil:</h3>", unsafe_allow_html=True)
    vida_util_perfil_fmt = vida_util_perfil.copy()
    vida_util_perfil_fmt['vida_util'] = vida_util_perfil_fmt['vida_util'].apply(lambda x: f'{x:.0f} dias')
    st.dataframe(vida_util_perfil_fmt, hide_index=True)
    
    # Gráficos
    st.markdown(f"<h3 style='color:#FF8C00;'>Distribuição dos churns previstos por mês</h3>", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='#0E1117')
    ax.set_facecolor('#0E1117')
    bars = sns.barplot(x=churns_mes['mes_ano_churn_pred'].astype(str), y=churns_mes['qtd_churns'], ax=ax, color='#FF8C00', edgecolor='#FF8C00')
    # Remover títulos dos eixos
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.tick_params(axis='x', colors='#FF8C00', labelsize=10, labelrotation=30)
    ax.tick_params(axis='y', colors='#FF8C00', labelsize=10)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontweight('bold')
    plt.xticks(rotation=30, ha='right', fontweight='bold')
    plt.yticks(fontweight='bold')
    # Adicionar valor em cima de cada barra
    for bar, value in zip(bars.patches, churns_mes['qtd_churns']):
        ax.annotate(f'{int(value)}',
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    ha='center', va='bottom',
                    fontsize=11, fontweight='bold', color='#FF8C00')
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), bbox_inches='tight')
    buf.seek(0)
    st.image(buf)
    plt.close(fig)

    st.markdown(f"<h3 style='color:#FF8C00;'>Valor perdido previsto por mês</h3>", unsafe_allow_html=True)
    fig2, ax2 = plt.subplots(figsize=(10, 4), facecolor='#0E1117')
    ax2.set_facecolor('#0E1117')
    bars2 = sns.barplot(x=valor_perdido_mes['mes_ano_churn_pred'].astype(str), y=valor_perdido_mes['valor_perdido'], ax=ax2, color='#FF8C00', edgecolor='#FF8C00')
    # Remover títulos dos eixos
    ax2.set_xlabel('')
    ax2.set_ylabel('')
    ax2.tick_params(axis='x', colors='#FF8C00', labelsize=10, labelrotation=30)
    ax2.tick_params(axis='y', colors='#FF8C00', labelsize=10)
    for label in ax2.get_xticklabels() + ax2.get_yticklabels():
        label.set_fontweight('bold')
    plt.xticks(rotation=30, ha='right', fontweight='bold')
    plt.yticks(fontweight='bold')
    # Adicionar valor em cima de cada barra
    for bar, value in zip(bars2.patches, valor_perdido_mes['valor_perdido']):
        ax2.annotate(f'{int(value):,}'.replace(',', '.'),
                     (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                     ha='center', va='bottom',
                     fontsize=11, fontweight='bold', color='#FF8C00')
    buf2 = io.BytesIO()
    plt.savefig(buf2, format='png', facecolor=fig2.get_facecolor(), bbox_inches='tight')
    buf2.seek(0)
    st.image(buf2)
    plt.close(fig2)
    
    # Exportar previsões detalhadas
    st.markdown(f"<h3 style='color:#FF8C00;'>Exportar previsões detalhadas dos clientes ativos</h3>", unsafe_allow_html=True)
    ativos_export = ativos.copy()
    nome_cols = ['id_cliente','perfil','idade','canal_aquisicao','regiao','valor_mensal','score_engajamento','data_entrada','dias_ate_churn_pred','data_churn_pred']
    ativos_export = ativos_export[nome_cols]
    ativos_export['dias_ate_churn_pred'] = ativos['dias_ate_churn_pred'].round(1)
    nome_csv = 'previsoes_detalhadas_clientes_ativos.csv'
    st.download_button('Baixar CSV de previsões detalhadas', data=ativos_export.to_csv(index=False).encode('utf-8'), file_name=nome_csv, mime='text/csv') 