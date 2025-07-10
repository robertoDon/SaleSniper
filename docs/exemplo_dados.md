# Exemplos de Dados para Testes

## 1. Estrutura do Excel de Clientes
O arquivo Excel deve conter as seguintes colunas:

| nome_cliente | porte  | dores         | localizacao | segmento    | faturamento | ticket_medio | meses_ativo | ltv     |
|--------------|--------|--------------|-------------|-------------|-------------|--------------|-------------|---------|
| Cliente A    | Médio  | Custos       | SP          | Tecnologia  | 1000000     | 50000        | 24          | 1200000 |
| Cliente B    | Grande | Produtividade| RJ          | Indústria   | 5000000     | 100000       | 36          | 3600000 |

- `ltv` pode ser calculado como `ticket_medio * meses_ativo`.

## 2. Formato do arquivo usuarios.json
```json
{
  "admin": "<hash_sha256>",
  "usuario1": "<hash_sha256>"
}
```

## 3. Exemplo de Análise ICP
```json
{
  "porte": "Grande",
  "dores": "Produtividade",
  "localizacao": "SP",
  "segmento": "Tecnologia",
  "ticket_medio": 75000,
  "ltv": 2250000,
  "meses_ativo": 30
}
```

## 4. Exemplo de Segmentação
- **Por valor acumulado (80/20):**
  - Grupo A: 20% dos clientes com 80% do valor
  - Grupo B: 80% dos clientes com 20% do valor
- **Por quantidade (20/30/30/20):**
  - Tier 1: 20% dos clientes
  - Tier 2: 30% dos clientes
  - Tier 3: 30% dos clientes
  - Tier 4: 20% dos clientes

## 5. Exemplo de Metas e Projeções
```json
{
  "funil": {
    "leads": 1000,
    "oportunidades": 100,
    "negociacoes": 50,
    "fechamentos": 10
  },
  "taxas_conversao": {
    "lead_oportunidade": 0.10,
    "oportunidade_negociacao": 0.50,
    "negociacao_fechamento": 0.20
  },
  "metas": {
    "receita_mensal": 1000000,
    "ticket_medio": 100000,
    "deals_necessarios": 10
  }
}
```

## 6. Variáveis de Ambiente (.env)
```env
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
OLLAMA_MODEL=neural-chat
```

## 7. Exemplo de Logs
```
2024-06-01 10:30:15 INFO: Usuário admin logado
2024-06-01 10:30:20 INFO: Arquivo Excel carregado: clientes.xlsx
2024-06-01 10:30:21 INFO: Análise ICP concluída
2024-06-01 10:30:22 INFO: Insights de IA gerados
```

Utilize o arquivo `/tests/clientes_teste.xlsx` para testar o sistema. 